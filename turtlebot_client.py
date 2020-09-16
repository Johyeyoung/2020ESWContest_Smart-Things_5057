import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, rc):
    print("connected with result code" + str(rc))
    client.subscribe("pathList")


def on_message(client, userdata, msg):
    print(msg.topic + "" +str(msg.payload))



# 객체 생성
client = mqtt.Client()
client.on_connect = on_connect()
client.on_message = on_message()

client.connect('192.168.0.15', 1833, 60)
print("")
client.loop_forever()
