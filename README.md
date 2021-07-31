# tcpproxy
Proxy TCP on a specific port. This is used to proxy data between two distinct ports on the same machine or two different machines entirely.

```
usage: tcpproxy.py [-h] [--chunkSize CHUNKSIZE] listenAddr proxyAddr

End-to-end TCP Proxy

positional arguments:
  listenAddr            Listen on this address. Default: "0.0.0.0:80"
  proxyAddr             Destination server address to proxy

optional arguments:
  -h, --help            show this help message and exit
  --chunkSize CHUNKSIZE
                        Data reception is done in chunks. Default: 1024
```
