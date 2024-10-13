from flask import Flask
from flask_cors import CORS
from py_eureka_client import eureka_client
from config import configure_app
from endpoints import register_endpoints

app = Flask(__name__)

# Configuración del cliente Eureka
eureka_client.init(
    eureka_server="http://localhost:8070/eureka",  # URL del servidor Eureka
    app_name="whisper",                      # Nombre del servicio Flask
    instance_port=5050,                            # Puerto del servicio Flask
    instance_host="localhost",                     # Host del servicio Flask
    instance_ip="127.0.0.1",                       # IP del servicio
    renewal_interval_in_secs=30,                   # Intervalo de renovación
    duration_in_secs=90                            # Duración del registro
)

CORS(app)
configure_app(app)
register_endpoints(app)

if __name__ == '__main__':
    # Iniciamos el servidor Flask
    app.run(host='0.0.0.0', port=5050)