import argparse
import glob
import httplib
import imp
import logging
import os
import sys
import traceback
import urlparse
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from SocketServer import ForkingMixIn

import yaml

from . import log
from .version import __version__

class ResolvePath(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        is_list = not isinstance(values, str)
        paths = getattr(namespace, self.dest) or []
        v = values if is_list else [values]
        for path in v:
            abspath = os.path.abspath(os.path.expanduser(path))
            if not os.path.exists(abspath):
                raise Exception("Path {} does not exist".format(abspath))
            paths.append(abspath)

        setattr(
            namespace,
            self.dest,
            paths if is_list else paths[0]
            )

def shorten_path(path):
    path = os.path.abspath(os.path.realpath(path))
    if path.startswith(os.path.abspath(os.curdir)):
        return os.path.relpath(path)
    return path

class ForkingHttpServer(ForkingMixIn, HTTPServer):
    pass

class VectoringHttpHandler(BaseHTTPRequestHandler, object):
    inspectors = []
    vectors = []
    connectors = dict(
        http=httplib.HTTPConnection,
        https=httplib.HTTPSConnection,
        )

    def handle_request(self):
        if not self.vectors:
            log.error("No vectors available")
            return
        if not self.inspectors:
            log.error("No inspectors available")
            return

        choice = None
        for inspector in self.inspectors:
            try:
                choice = inspector.select(self.headers, self.vectors)
            except:
                log.error("inspector %s failed", inspector.__name__)

            if choice:
                log.info(
                    "Inspector \"%s\" chose vector %s",
                    inspector.__name__,
                    choice[1]
                    )
                break
        if not choice:
            log.info("No vector chosen, hanging up")
            return

        scheme, host = choice if choice else self.vectors[1]
        conn = self.connectors[scheme](
            host,
            timeout=self.timeout
            )
        u = urlparse.urlsplit(self.path)
        path = (u.path + '?' + u.query if u.query else u.path)
        self.headers['Host'] = host

        body_len = int(self.headers.get('Content-Length', '0'))
        body = self.rfile.read(body_len) if body_len else None
        conn.request(self.command, path, body, dict(self.headers))
        res = conn.getresponse()

        self.wfile.write("HTTP/1.1 %d %s\r\n" % (res.status, res.reason))

        for key in res.msg:
            self.wfile.write("{}={}\r\n".format(key, res.msg[key]))

        self.end_headers()
        self.wfile.write(res.read())
        self.wfile.flush()

    # All verbs, one implementation
    do_GET = handle_request
    do_POST = handle_request
    do_PUT = handle_request
    do_HEAD = handle_request

def inspect(vectors):
    class WrappedHandler(VectoringHttpHandler):
        @classmethod
        def using(cls, inspectors):
            cls.inspectors = inspectors
            return cls

    WrappedHandler.vectors = vectors
    return WrappedHandler

def find_inspectors(paths):
    if not paths:
        mod_path = os.path.dirname(os.path.abspath(__file__))
        paths = [os.path.join(mod_path, 'samples')]

    inspectors = []
    for path in paths:
        inspectors.extend(load_inspectors(path))

    return inspectors

def load_inspectors(path):
    inspectors = []
    pattern = os.path.join(path, "*.py")
    log.info("Searching %s for inspectors", shorten_path(pattern))

    for filename in glob.glob(pattern):
        relpath = shorten_path(filename)
        module = os.path.basename(filename.strip('.py'))
        try:
            plugin = imp.load_source(module, filename)
            if 'select' in dir(plugin):
                inspectors.append(plugin)
                log.info("Loading inspector: %s", relpath)
        except TypeError:
            log.debug(
                "Ignoring module that failed to load: %s",
                relpath)
        except:
            log.error("Failed to load inspector: %s", relpath)

    return inspectors

def parse_args():
    parser = argparse.ArgumentParser(
        prog='httpvec',
        description='Plugin-based HTTP Proxy')

    parser.add_argument(
        '-d', '--debug',
        action="store_true",
        help="show detailed debug information")
    parser.add_argument(
        '-V', '--verbose',
        action="store_true",
        help="show additional information")
    parser.add_argument(
        '-v', '--version',
        action='version',
        version='%(prog)s v'+__version__)

    parser.add_argument(
        '-i', '--inspectors',
        dest="inspector_paths",
        nargs="*",
        action=ResolvePath,
        help="path to directory that contains inspector modules")

    parser.add_argument(
        '-p', '--port',
        dest='port',
        action='store',
        type=int,
        default='8080',
        help='port used to listen for incoming requests')
    parser.add_argument(
        '-H', '--host',
        dest='host',
        action='store',
        default='localhost',
        help='IP or hostname used to listen for incoming requests')
    parser.add_argument(
        'VECTORS',
        action=ResolvePath,
        help="YAML file with the list of vectors")

    args = parser.parse_args()

    if args.debug:
        log.setLevel(logging.DEBUG)
    elif args.verbose:
        log.setLevel(logging.INFO)

    return args

def run_proxy():
    args = parse_args()

    vectors = []
    with open(args.VECTORS, 'rt') as f:
        config = yaml.load(f)
        for url in config:
            url_parts = urlparse.urlsplit(url)
            scheme = url_parts[0].lower()
            host = url_parts[1]
            if not scheme in ['http', 'https']:
                raise Exception(
                    "Url must be http:// or https://"
                    )
            vectors.append((scheme, host,))
    inspectors = find_inspectors(args.inspector_paths)

    handler = inspect(vectors).using(inspectors)
    proxy = ForkingHttpServer(
        (args.host, args.port),
        handler)

    sockname = proxy.socket.getsockname()
    log.info("Listening for HTTP requests on %s:%s...", *sockname)
    proxy.serve_forever()

def main():
    logging.basicConfig(
        stream=sys.stderr,
        level=logging.DEBUG,
        format='%(levelname)s: %(message)s')

    try:
        run_proxy()
    except KeyboardInterrupt:
        pass
    except:
        log.error(sys.exc_info()[1])
        if log.level == logging.DEBUG:
            traceback.print_exc()

        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
