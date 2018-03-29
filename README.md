# A plugin-based HTTP proxy in Python
```
usage: httpvec [-h] [-d] [-V] [-v]
               [-i [INSPECTOR_PATHS [INSPECTOR_PATHS ...]]] [-p PORT]
               [-H HOST]
               VECTORS

Plugin-based HTTP Proxy

positional arguments:
  VECTORS               YAML file with the list of vectors

optional arguments:
  -h, --help            show this help message and exit
  -d, --debug           show detailed debug information
  -V, --verbose         show additional information
  -v, --version         show program's version number and exit
  -i , --inspectors     path to inspector module or a directory that contains
                        inspector modules
  -p PORT, --port PORT  port used to listen for incoming requests
  -H HOST, --host HOST  IP or hostname used to listen for incoming requests
```

## Using HTTPVEC
`httpvec` can be configured with a list of base Urls to backend
HTTP servers called `vectors` and a list of HTTP-header-inspecting
python modules called `inspectors`.

When an HTTP request arrives, `httpvec` calls the `select` method on each 
`inspector` in-order. The first `inspector` to return a valid `vector` wins.
If no vector is chosen, the connection is dropped.

### Configuration
Vectors are provided via a `yaml` file specified on the command-line. A
vector is a python dictionary. `httpvec` requires a `url` key whose
value is the URL of the backend server to proxy when the vector is chosen.
This url must start with either `http` or `https`.

Additional keys can be added as required by your inspectors. Dictionary
keys that start with a dot character (e.g. `.host`) are reserved for internal use
by `httpvec`.

#### Example vectors.yml (with extra type attribute)
``` YAML
- {
  'url': 'https://httpbin.org/',
  'type': 'prod',
  }
- {
  'url': 'http://www.google.com/',
  'type': 'prod',
  }
- {
  'url': 'https://yahoo.local:5000/'
  'type': 'test',
  }
```

### Inspectors
At startup, `httpvec` searches the `inspectors` paths specified by the
 `-i, --inspectors` option for python modules that implement the 
`select(headers, vectors)` function. This function inspects the 
incoming request headers and returns the correct `vector`. If no
choice can be made, it returns `None`.

Each vector is a dictionary with the keys and values from the YAML file.
`httpvec` extends the dictionary to include the following additional
attributes.

|Key        |Value      |
|-----------|-----------|
|`.scheme`  |Url scheme (e.g. `http` or `https`)|
|`.host`    |Url host (e.g. `yahoo.local:5000`)|
|`.port`    |Url port (e.g. `5000`)|
|`.path`    |Url path (e.g. `/api/resource`)|
|`.query`   |Url query following `?` (e.g. `search=a&limit=1`)|
|`.fragment`|Url fragment following `#` (e.g. `#heading-1`)|

## Sample inspectors
The following inspectors are provided in the samples directory. They
are used by `httpvec` when the `-i, --inspectors` argument is not
provided.

|Name    |Description|
|--------|-----------|
|[host](httpvec/samples/host.py)|Compares the HTTP `Host` header to the vector host|
|[chaos](httpvec/samples/chaos.py)|Chooses a random vector|
|[chill](httpvec/samples/chill.py)|Always takes the first vector|
|[null](httpvec/samples/null.py)|Never chooses a vector|


