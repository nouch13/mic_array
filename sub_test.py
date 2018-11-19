#!/usr/bin/python
# -*- coding: utf-8 -*-
from time import sleep
import paho.mqtt.client as mqtt

topic = '806/sound/#'
host = 'localhost'
port = 1883

def on_connect(client, userdata, flags, respons_code):
    print('status {0}'.format(respons_code))
    client.subscribe(topic)

def on_message(client, userdata, msg):
    # print(msg.topic + '' + str(msg.payload))
    topics = msg.topic.split('/')
    if topics[-1] == 'doa':
        store_doa(msg)
    elif topics[-1] == 'laughter':
        # print(msg.payload.decode('utf-8'))
        doa_data = open('./tmp_doa.txt', 'r')
        angle_doa = float(doa_data.read())
        print('笑いの種類: %s \t 到来角度: %.1f' % (msg.payload.decode('utf-8'), angle_doa))


def store_doa(msg):
    with open('./tmp_doa.txt', 'w') as file:
        # 角度をファイルに保存
        file.write(msg.payload.decode('utf-8'))


if __name__ == '__main__':
    client = mqtt.Client(protocol=mqtt.MQTTv311)
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(host, port=port, keepalive=60)

    client.loop_forever()
