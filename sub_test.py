#!/usr/bin/python
# -*- coding: utf-8 -*-
import paho.mqtt.client as mqtt

topic = '806/sound/#'

def on_connect(client, userdata, flags, respons_code):
    print('watch %s' % topic)
    client.subscribe(topic)

def on_message(client, userdata, msg):
    # doa_angle = 0.0
    print(msg.topic + ' ' + str(msg.payload.decode(encoding='utf-8')))
    if msg.topic == '806/sound/mic_array/doa':
        doa_angle = float(msg.payload.decode(encoding='utf-8'))
    if msg.topic == '806/sound/usb_mic/laughter':
        laughter_cls = msg.payload.decode(encoding='utf-8')
        print(laughter_cls, doa_angle)
        # print('笑いの種類:%s  音の方向:%.1f' % (laughter_cls, doa_angle))


def main():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect('localhost', 1883, keepalive=60)
    client.loop_forever()

if __name__ == '__main__':
    main()
