#!/usr/bin/env python3

from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib
import subprocess
import json
import html
import sys
import time

hostName = "localhost"
serverPort = 8080

blurb = open("blurb.html","rb").read()

class Loogle():
    def start(self):
        self.loogle = subprocess.Popen(
            ["./build/bin/loogle","Mathlib","-j"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )

    def __init__(self):
        self.start()

    def query(self, query):
        try:
            self.loogle.stdin.write(bytes(query, "utf8"));
            self.loogle.stdin.write(b"\n");
            self.loogle.stdin.flush();
            output = self.loogle.stdout.readline()
            return json.loads(output)
        except (IOError, json.JSONDecodeError) as e:
            time.sleep(5) # to allow the process to die
            code = self.loogle.poll()
            if code == -31:
                sys.stderr.write(f"Backend died trying to escape the sandbox.\n")
                self.start()
                return {"error":
                    f"Backend died trying to escape the sandbox. Restarting..."
                }
            if code is not None:
                sys.stderr.write(f"Backend died with code {code}.\n")
                self.start()
                return {"error":
                    f"The backend process died with code {code}. Restarting..."
                }
            else:
                sys.stderr.write(f"Backend did not respond ({e}).\n")
                self.loogle.kill() # just to be sure
                self.start()
                return {"error": "The backend process did not respond, killing and restarting..."}

loogle = Loogle()

class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = ""
        result = {}

        url_query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(url_query)
        if "q" in params and len(params["q"]) == 1:
            query = params["q"][0]
            if "\n" in query:
                return
            result = loogle.query(query)
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes(f"""
            <!doctype html>
            <html lang="de">
            <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <link rel="stylesheet" href="https://unpkg.com/chota@latest">
            <title>Loogle!</title>
            <body>
            <main class="container">

            <section>
            <h1>Loogle!</h1>
            <form method="GET">
            <p class="grouped">
            <input type="text" name="q" value="{html.escape(query)}"/>
            <input type="submit" value="#find"/>
            </p>
            </form>
            </section>
        """, "utf-8"))
        if "error" in result:
            self.wfile.write(bytes(f"""
                <h2>Error</h2>
                <pre>{html.escape(result['error'])}</pre>
            """, "utf-8"))
        if "header" in result:
            self.wfile.write(b"""
                <h2>Result</h2>
            """)
            self.wfile.write(bytes(f"""
                <p>{html.escape(result['header'])}</p>
            """, "utf-8"))
        if "names" in result:
            self.wfile.write(bytes(f"""
                <ul>
            """, "utf-8"))
            for name in result["names"]:
                self.wfile.write(bytes(f"""
                    <li><a href="https://leanprover-community.github.io/mathlib4_docs/find/?pattern={html.escape(name)}#doc">{html.escape(name)}</a></li>
                """, "utf-8"))
            self.wfile.write(b"""
                </ul>
            """)
        self.wfile.write(blurb)
        self.wfile.write(b"""
            </main>
            </body>
            </html>
        """)

if __name__ == "__main__":
    webServer = HTTPServer((hostName, serverPort), MyHandler)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")
