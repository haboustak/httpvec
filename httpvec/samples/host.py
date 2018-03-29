"""
Host header inspector sample
"""

def select(headers, vectors):
    """
    Select a vector whose .host attribute matches the Host header
    """
    host_header = headers.get("Host", "")
    if not host_header:
        return None

    for v in vectors:
        if v['.host'] == host_header:
            return v

    return None
