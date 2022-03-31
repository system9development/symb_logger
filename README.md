This repo is just for recording metrics on connection issues with Symbridge exchange

3 issues with WS connections frequently observed:
1: WS times out, we never receive a response
2: socket getaddrinfo errors (solved by adding mapping in etc/hosts file)
3: 1000 OK close code sent to websockets still in operation (closure_logger)