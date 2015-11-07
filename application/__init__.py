from flask import Flask
from .blueprints.user_bp import *
from .blueprints.paragraph_bp import *
from .blueprints.plane_bp import *

app = Flask(__name__)
app.config["DEBUG"] = True
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

app.register_blueprint(user_bp, url_prefix='/user')
app.register_blueprint(paragraph_bp, url_prefix='/paragraph')
app.register_blueprint(plane_bp, url_prefix='/plane')