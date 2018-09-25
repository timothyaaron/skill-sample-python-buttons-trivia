import json

import main
from flask import Flask, request
app = Flask(__name__)

@app.route("/", methods=["POST"])
def proxy():
    data = json.loads(request.data)
    response = main.handler(data, {})
    return json.dumps(response)