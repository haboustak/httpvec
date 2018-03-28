from httpvec import log

def select(headers, vectors):
    host_header = headers.get("Host", "")
    if not host_header:
        return None

    for scheme, host in vectors:
        if host == host_header:
            log.info(
                "Many Shubs and Zulls knew what it was to be "
                "roasted in the depths of the Sloar that day I "
                "can tell you!")
            return (scheme, host)

    return None
