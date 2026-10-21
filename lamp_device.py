from IO7FuPython import ConfiguredDevice
import json
import time
import uComMgr32
from machine import Pin

LAMP_PIN = 15                           # 릴레이 IN 핀에 연결한 GPIO (32p 회로)
ACTIVE_LOW = False                      # 릴레이가 반대로 동작하면 True로 변경
relay = Pin(LAMP_PIN, Pin.OUT)
lampOn = False

def setLamp(on):
    global lampOn
    lampOn = on
    relay.value((not on) if ACTIVE_LOW else on)

def handleCommand(topic, msg):
    global lastPub
    jo = json.loads(str(msg, 'utf8'))
    if ("lamp" in jo['d']):
        cmd = jo['d']['lamp']
        if cmd == 'on':
            setLamp(True)
        elif cmd == 'off':
            setLamp(False)
        elif cmd == 'toggle':           # 버튼(Push 함수)에서 오는 명령
            setLamp(not lampOn)
        lastPub = - device.meta['pubInterval']   # 바뀐 상태를 바로 보고

nic = uComMgr32.startWiFi('io7lamp')
device = ConfiguredDevice()
device.setUserCommand(handleCommand)
device.connect()

setLamp(False)                          # 시작할 때는 꺼진 상태
lastPub = time.ticks_ms() - device.meta['pubInterval']

while True:
    if not device.loop():
        break
    if (time.ticks_ms() - device.meta['pubInterval']) > lastPub:
        lastPub = time.ticks_ms()
        device.publishEvent('status', json.dumps({'d': {'lamp': 'on' if lampOn else 'off'}}))