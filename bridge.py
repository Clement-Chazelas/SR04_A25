import serial
import json
import time
import paho.mqtt.client as mqtt

# ================= CONFIGURATION A MODIFIER =================
# 1. L'adresse IP que vous avez notée sur le PC 3 (Serveur)
MQTT_SERVER_IP = "192.168.1.50" 

# 2. Le port USB où est branché l'Arduino sur CE PC
# Windows : souvent "COM3", "COM4", ou "COM5" (vérifiez dans le Gestionnaire de Périphériques)
# Linux/Mac : "/dev/ttyACM0" ou "/dev/ttyUSB0"
SERIAL_PORT = "COM3" 
# ============================================================

BAUD_RATE = 9600
TOPIC_PREFIX = "maison/capteurs/"

client = mqtt.Client()

def run():
    print(f"Connexion au serveur MQTT {MQTT_SERVER_IP}...")
    try:
        client.connect(MQTT_SERVER_IP, 1883, 60)
        client.loop_start()
    except:
        print("ERREUR: Impossible de joindre le serveur MQTT (Vérifiez l'IP et le Pare-feu)")
        return

    print(f"Ouverture du port série {SERIAL_PORT}...")
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    except:
        print("ERREUR: Impossible d'ouvrir le port USB. Vérifiez le nom (COMx).")
        return

    while True:
        if ser.in_waiting > 0:
            try:
                line = ser.readline().decode('utf-8').strip()
                if not line: continue
                
                # On décode le JSON reçu de l'Arduino
                data = json.loads(line)
                
                # On publie sur: maison/capteurs/temperature OU maison/capteurs/air_quality
                topic = TOPIC_PREFIX + data['id']
                
                client.publish(topic, json.dumps(data))
                print(f"Envoyé : {topic} -> {data}")
                
            except json.JSONDecodeError:
                pass # On ignore les lignes incomplètes
            except Exception as e:
                print(f"Erreur : {e}")
        time.sleep(0.1)

if _name_ == "_main_":
    run()
