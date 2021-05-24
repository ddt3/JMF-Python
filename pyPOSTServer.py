from http.server import HTTPServer, BaseHTTPRequestHandler

# from io import BytesIO
from time import time


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        #print("in GET")
        self.send_response(200)
        self.end_headers()
        #self.wfile.write(b'Hello, world!')

    def do_POST(self):
        #print("in POST")
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        self.send_response(200)
        self.end_headers()
        
        # you cn do anything with the body, even save it ot disk :)
        # for now, just use time in milisec to make sure the file name is unique
        with open("signal_%s.status" %time(), 'wb') as f:
            f.write(body)
           
        #response = BytesIO()
        #response.write(b'This is POST request. ')
        #response.write(b'Received: ')
        #response.write(body)
        #self.wfile.write(response.getvalue())
        #print(body)


port = 9090

httpd = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
print("Listening on port %s..." %port)
httpd.serve_forever()