import streamlit as st
import paho.mqtt.client as mqtt
import json
import threading

# Configuración del broker público
cfg = {
    "broker": "broker.hivemq.com",  # Broker público gratuito
    "port": 1883,
    "topic": "iot/demo"             # Tema donde publicaremos y escucharemos
}

# Variable global para almacenar mensajes recibidos
messages = []

# Callback cuando nos conectamos al broker
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Conectado al broker MQTT")
        client.subscribe(cfg["topic"])
    else:
        print(f"❌ Error de conexión: {rc}")

# Callback cuando recibimos un mensaje
def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode("utf-8")
        data = json.loads(payload)
    except Exception:
        data = {"raw": msg.payload.decode("utf-8")}
    messages.append(data)

# Lanzar cliente MQTT en un hilo aparte
def mqtt_thread():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(cfg["broker"], cfg["port"], 60)
    client.loop_forever()

threading.Thread(target=mqtt_thread, daemon=True).start()

# ---- Interfaz Streamlit ----
st.title("🌐 IoT Dashboard con MQTT (Broker Público)")
st.write(f"Conectado al broker **{cfg['broker']}:{cfg['port']}**, tópico **{cfg['topic']}**")

# Mostrar mensajes recibidos
st.subheader("📩 Mensajes recibidos")
if messages:
    for m in reversed(messages[-10:]):  # Mostrar los últimos 10
        st.json(m)
else:
    st.info("Esperando mensajes MQTT en el tópico...")
