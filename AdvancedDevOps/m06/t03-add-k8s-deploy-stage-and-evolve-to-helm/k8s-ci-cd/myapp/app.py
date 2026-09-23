from http.server import HTTPServer, BaseHTTPRequestHandler
import os, socket

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        hostname = socket.gethostname()
        self.wfile.write(f"my-app running on {hostname}\n".encode())

if __name__ == '__main__':
    port = int(os.getenv('PORT', '8081'))
    server = HTTPServer(('0.0.0.0', port), Handler)
    print(f"Server running on port {port}")
    server.serve_forever()
