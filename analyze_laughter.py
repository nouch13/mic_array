#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime
import re
import socket
import numpy as np
from bs4 import BeautifulSoup
import paho.mqtt.client as mqtt

def get_laugh_class(snt):
    # 観測された音素列から，笑いの分類結果を導出する
    lengths = [0, 0, 0]
    lengths = np.array(lengths)
    laughter_classes = ['普通の笑い', '含み笑い', '照れ隠しの笑い']
    ptn_a = '(ア|ッ)?(ハ|ッ)+'
    ptn_b = '(ウ|ッ)?(フ|ッ)+'
    ptn_c = '(エ|ッ)?(ヘ|ッ)+'
    if re.match(ptn_a, snt) != None: lengths[0] = len(re.match(ptn_a, snt).group())  # 普通の笑いに一致する長さ
    if re.match(ptn_b, snt) != None: lengths[1] = len(re.match(ptn_b, snt).group())  # 含み笑いに一致する長さ
    if re.match(ptn_c, snt) != None: lengths[2] = len(re.match(ptn_c, snt).group())  # 照れ隠し笑いに一致する長さ
    return laughter_classes[np.argmax(lengths)]

def main():
    host = 'localhost'
    port = 10500
    j_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    j_client.connect((host, port))

    start_s = 0
    end_s = 0
    try:
        topic = '806/sound/usb_mic/laughter'  # publish先のトピック名をここで指定
        m_client = mqtt.Client(protocol=mqtt.MQTTv311)
        m_client.connect(host, port=1883, keepalive=60)
        data = ''
        while 1:
            if '\n.' in data:
                data = data.replace('\n.', '')
                soup = BeautifulSoup(data, 'xml')
                if soup.find(STATUS="STARTREC"):
                    start_s = int(soup.find(STATUS="STARTREC")['TIME'])  # 音声入力開始時刻(UnixTime)
                if soup.find(STATUS="ENDREC"):
                    end_s = int(soup.find(STATUS="ENDREC")['TIME'])      # 音声入力終了時刻(UnixTime)
                words = ''  # 認識結果1文をここに格納
                for whypo in soup.find_all('WHYPO'):
                    words += whypo['WORD']  # WORDの部分を連結する形で，sentenceを取得(冗長実装の可能性あり)
                if len(words) > 0:
                    # rec_s = (start_s+end_s)/2  # 笑いが検出された時間(入力区間の中点を取る)
                    rec_s = start_s  # 認識時刻は，ひとまずは入力開始時刻とする(終点時刻が難しいため)
                    rec_s = datetime.datetime.fromtimestamp(rec_s)  # 普通の時刻に変換
                    rec_s = rec_s.strftime('%H:%M:%S')
                    print('%s %sを検出しました' % (rec_s, get_laugh_class(words)))
                    m_client.publish(topic, get_laugh_class(words))
                data = ''
            else:
                data = data + j_client.recv(1024).decode(encoding='utf-8')
    except KeyboardInterrupt:
        j_client.close()
        m_client.disconnect()

if __name__ == "__main__":
    main()
