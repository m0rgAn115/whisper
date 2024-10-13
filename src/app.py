from flask import Flask
from flask_cors import CORS
from endpoints import register_endpoints
from config import configure_app


app = Flask(__name__)

CORS(app)
configure_app(app)
register_endpoints(app)



if __name__ == '__main__':
    # Iniciamos el servidor Flask
    app.run(host='0.0.0.0', port=8080)