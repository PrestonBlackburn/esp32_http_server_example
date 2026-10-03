# Preview the generated HTML without needing to run anything on device

from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from build_web import get_jinja_env

ROOT = Path(__file__).resolve().parent.parent.parent
TEMPLATE_DIR = ROOT / "templates"
PAGES = {"/": "pages/live_demo.html"}   # URL path -> template

class PreviewHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # serve /static/... from the project root
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path in PAGES:
            # new env per request so template edits show up on refresh
            env = get_jinja_env(str(TEMPLATE_DIR))
            html = env.get_template(PAGES[path]).render(context={})
            body = html.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(body)
        elif path.startswith("/static/"):
            super().do_GET()          # file lookup under ROOT/static
        else:
            self.send_error(404)


if __name__ == "__main__":
    httpd = HTTPServer(("", 8000), PreviewHandler)
    print("Preview on http://localhost:8000")
    httpd.serve_forever()