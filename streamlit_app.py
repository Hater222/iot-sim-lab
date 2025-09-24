import json, threading, collections
import streamlit as st
import paho.mqtt.client as mqtt
from src.utils import load_config
from src.mqtt_io import make_client

st.set_page_config(page_title="IoT Live Dashboard", layout="wide")

cfg = load_config()
BUFFER = 200
store = {k: collections.deque(maxlen=BUFFER) for k in ("temp","hum","prox")}

# Callback MQTT
def on_message(client, userdata, message):
    try:
        payload = json.loads(message.payload.decode("utf-8"))
        topic = message.topic.split("/")[-1]
        if topic in store:
            store[topic].append(float(payload["value"]))
    except Exception as e:
        print("Error en mensaje:", e)

# Hilo MQTT
def start_mqtt():
    client = make_client(
        "streamlit",
        cfg["broker"],
        cfg["port"],
        cfg["username"],
        cfg["password"],
        on_message
    )
    client.subscribe(f"{cfg['base_topic']}/#")
    client.loop_forever()

# Lanzar hilo solo una vez
if "mqtt_started" not in st.session_state:
    threading.Thread(target=start_mqtt, daemon=True).start()
    st.session_state["mqtt_started"] = True

st.title("Simulación IoT – Dashboard en Tiempo Real")

# Placeholders para gráficos y métricas
placeholder_metrics = st.empty()
placeholder_charts = st.empty()

# Auto refresco cada segundo (sin bloquear la app)
st_autorefresh = st.experimental_rerun  # Se ejecuta al final de cada ciclo

import time

# Loop de actualización visual (no bloquea MQTT)
for _ in range(2000):  # simplemente limitar iteraciones
    with placeholder_metrics.container():
        col1, col2, col3 = st.columns(3)
        for c, k, label in [(col1,"temp","Temperatura (°C)"),
                            (col2,"hum","Humedad (%)"),
                            (col3,"prox","Proximidad (cm)")]:
            val = store[k][-1] if len(store[k]) else None
            c.metric(label, val)
    
    with placeholder_charts.container():
        st.line_chart(list(store["temp"]), height=200)
        st.line_chart(list(store["hum"]), height=200)
        st.line_chart(list(store["prox"]), height=200)
        st.caption(f"Broker: {cfg['broker']} | Base topic: {cfg['base_topic']}")
    
    time.sleep(1)
    st.experimental_rerun()
