import os

from fourthand1web.app import app, socketio

HOST = os.getenv("IP", "0.0.0.0")
PORT = int(os.getenv("PORT", 5000))

socketio.run(app, host=HOST, port=PORT, debug=os.environ.get("DEBUG", "True") == "True")
