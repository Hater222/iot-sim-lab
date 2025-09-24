import streamlit as st
import paho.mqtt.client as mqtt
import threading
import json
import collections

# ---- Configuración del broker público ----
BROKER = "broker.hivemq.com"
PORT = 1883
TOPIC = "iot/demo"

# ---- Variables para almacenar datos ----
BUFFER = 200
store = {
    "temp": collections.deque(maxlen=BUFFER),
    "hum": collections.deque(maxlen=BUFFER),
    "prox": collections.deque(maxlen=BUFFER)
}

# ---- Callback cuando recibimos mensajes ----
def on_message(client, userdata, message):
    try:
        payload = json.loads(message.payload.decode("utf-8"))
        device = payload.get("device", "")
        value = payload.get("value", None)

        # Asignar a cada sensor
        if device == "sensor1":
            store["temp"].append(value)
        elif device == "sensor2":
            store["hum"].append(value)
        elif device == "sensor3":
            store["prox"].append(value)
    except Exception:
        pass  # ignorar errores de parsing

# ---- Hilo MQTT ----
def mqtt_thread():
    client = mqtt.Client(client_id="streamlit", callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
    client.on_message = on_message
    client.connect(BROKER, PORT, 60)
    client.subscribe(TOPIC)
    client.loop_forever()

# Iniciar hilo MQTT si no está iniciado
if "mqtt_started" not in st.session_state:
    threading.Thread(target=mqtt_thread, daemon=True).start()
    st.session_state["mqtt_started"] = True

# ---- Interfaz Streamlit ----
st.set_page_config(page_title="IoT Dashboard Público", layout="wide")
st.title("🌐 Simulación IoT – Dashboard en Tiempo Real")
st.write(f"Broker: **{BROKER}:{PORT}** | Tópico: **{TOPIC}**")

# Mostrar métricas actuales
col1, col2, col3 = st.columns(3)
col1.metric("Temperatura (°C)", store["temp"][-1] if store["temp"] else "—")
col2.metric("Humedad (%)", store["hum"][-1] if store["hum"] else "—")
col3.metric("Proximidad (cm)", store["prox"][-1] if store["prox"] else "—")

# Mostrar gráficos en tiempo real
st.subheader("📈 Gráficos de sensores")
st.line_chart(list(store["temp"]), height=200)
st.line_chart(list(store["hum"]), height=200)
st.line_chart(list(store["prox"]), height=200)

# Mensajes recibidos (últimos 10)
st.subheader("📩 Últimos mensajes MQTT")
if store["temp"] or store["hum"] or store["prox"]:
    last_msgs = []
    for t, h, p in zip(store["temp"], store["hum"], store["prox"]):
        last_msgs.append({"temp": t, "hum": h, "prox": p})
    for msg in reversed(last_msgs[-10:]):
        st.json(msg)
else:
    st.info("Esperando mensajes MQTT en el tópico...")
