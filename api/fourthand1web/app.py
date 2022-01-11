from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config.from_object("fourthand1web.settings")

CORS(app, resources=r'/*')
# csrf = CSRFProtect(app)
db = SQLAlchemy(app)
# socketio = SocketIO(app, cors_allowed_origins=["http://localhost:5000"])
socketio = SocketIO(app, cors_allowed_origins="*")

if __name__ == '__main__':
    socketio.run(app)
