import streamlit as st
import threading
import time
import json
from src.mqtt_io import make_client

# -----------------------------------------------------
# CONFIGURACIÓN DEL BROKER MQTT
# -----------------------------------------------------
cfg = {
    "broker": "broker.hivemq.com",  # Broker público
    "port": 1883,                   # Puerto estándar MQTT sin TLS
    "username": "",                 # Vacío para broker público
    "password": ""                  # Vacío para broker público
}

# Estado global para almacenar mensajes recibidos
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# -----------------------------------------------------
# Callback cuando llega un mensaje MQTT
# -----------------------------------------------------
def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    try:
        data = json.loads(payload)
    except:
        data = {"raw": payload}

    st.session_state["messages"].append({
        "topic": msg.topic,
        "data": data,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    })

# -----------------------------------------------------
# Hilo para gestionar conexión MQTT
# -----------------------------------------------------
def mqtt_thread():
    client = make_client(
        "streamlit",
        cfg["broker"],
        cfg["port"],
        cfg["username"],
        cfg["password"],
        on_message
    )
    client.subscribe("#")  # Suscribirse a todos los tópicos
    client.loop_forever()

# Lanzar el hilo MQTT solo una vez
if "mqtt_thread_started" not in st.session_state:
    t = threading.Thread(target=mqtt_thread, daemon=True)
    t.start()
    st.session_state["mqtt_thread_started"] = True

# -----------------------------------------------------
# Interfaz Streamlit
# -----------------------------------------------------
st.title("IoT Sim Lab - MQTT Monitor")

st.markdown("Conectado a broker público **HiveMQ** (`broker.hivemq.com:1883`)")

# Mostrar mensajes
st.subheader("Mensajes recibidos")
for msg in st.session_state["messages"][-20:]:
    st.json(msg)
