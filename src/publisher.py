import paho.mqtt.client as mqtt
import json
import time
import random

# Configuración del broker público
BROKER = "broker.hivemq.com"
PORT = 1883
TOPIC = "iot/demo"

# Crear cliente MQTT con callback API versión 2
client = mqtt.Client(client_id="publisher", callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
client.connect(BROKER, PORT, 60)

# Simular 3 sensores: temperatura, humedad, proximidad
def read_temperature():
    return round(random.uniform(20, 30), 2)

def read_humidity():
    return round(random.uniform(40, 70), 1)

def read_proximity():
    # valores cercanos o lejanos
    if random.random() < 0.1:
        return round(random.uniform(15, 40), 1)
    return round(random.uniform(120, 200), 1)

try:
    while True:
        messages = [
            {"device": "sensor1", "value": read_temperature()},
            {"device": "sensor2", "value": read_humidity()},
            {"device": "sensor3", "value": read_proximity()},
        ]

        for msg in messages:
            client.publish(TOPIC, json.dumps(msg))
            print(f"Mensaje enviado: {msg}")

        time.sleep(1)  # enviar cada segundo

except KeyboardInterrupt:
    print("Publicador detenido por usuario.")

finally:
    client.disconnect()
