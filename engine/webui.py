import socket
from logging import getLogger
from flask import Flask, render_template

app = Flask(__name__)
app.static_folder = "static"


@app.route('/')
def web():
    return render_template('index.html')


def run():
    log = getLogger('werkzeug')
    log.disabled = True
    print(f"WebUI at http://{socket.gethostbyname(socket.gethostname())}:5201")
    app.run(socket.gethostbyname(socket.gethostname()), 5201)
