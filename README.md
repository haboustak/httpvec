# A plugin-based HTTP router
```
usage: httpvec [-h] [-d] [-V] [-v]
               [-i [INSPECTOR_PATHS [INSPECTOR_PATHS ...]]]
               VECTORS

Plugin-based HTTP Proxy

  VECTORS               YAML file with the list of vectors

optional arguments:
  -h, --help            show this help message and exit
  -d, --debug           show detailed debug information
  -V, --verbose         show additional information
  -v, --version         show program's version number and exit
  -i , --inspectors     path to directory that contains inspector modules
```

## Using HTTPVEC
`httpvec` can be configured with a list of base Urls to backend
HTTP servers called `vectors` and a list of HTTP-header-inspecting
python modules called `inspectors`.

When an HTTP request arrives, `httpvec` calls the `select` method on each 
`inspector` in-order. The first `inspector` to return a valid `vector` wins.
If no vector is chosen the connection is dropped.

### Configuration
Vectors are provided via a yaml file specified on the command-line.

**Example vectors.yml**
``` YAML
- https://httpbin.org/
- http://www.google.com/
- https://yahoo.local:5000/
```

At startup, `httpvec` searches the `inspectors` paths specified by the
 `-i, --inspectors` option for python modules that implement the 
`select(headers, vectors)` function. This function inspects the 
incoming request headers and returns the correct `vector`. If no
choice can be made, it returns `None`.

## Example inspectors
|Name    |Description|
|--------|-----------|
|[samples/host_header.py]|Compares the HTTP `Host` header to the vector host|


