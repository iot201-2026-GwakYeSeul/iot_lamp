from IO7FuPython import ConfiguredDevice
import json
import time
import uComMgr32
from machine import Pin

BUTTON_PIN = 1
button = Pin(BUTTON_PIN, Pin.IN)        # 모듈에 저항이 있어서 내부 풀업/풀다운 없음

def isPushed():
    return button.value() == 1          # 누르면 1

def handleCommand(topic, msg):
    global lastPub
    jo = json.loads(str(msg, 'utf8'))
    if ("button" in jo['d']):
        if jo['d']['button'] == 'current':
            lastPub = - device.meta['pubInterval']

def publishButton(state):
    device.publishEvent('status', json.dumps({'d': {'button': state}}))

nic = uComMgr32.startWiFi('io7button')
device = ConfiguredDevice()
device.setUserCommand(handleCommand)
device.connect()

lastState = isPushed()
lastPub = time.ticks_ms() - device.meta['pubInterval']

while True:
    if not device.loop():
        break

    state = isPushed()
    if state != lastState:                  # 버튼 상태가 바뀌었을 때
        time.sleep_ms(30)                   # 채터링 제거
        state = isPushed()
        if state != lastState:
            lastState = state
            publishButton('pushed' if state else 'released')
            lastPub = time.ticks_ms()

    if (time.ticks_ms() - device.meta['pubInterval']) > lastPub:
        lastPub = time.ticks_ms()
        publishButton('held' if lastState else 'released')   # 항상 주기 보고 → 연결 유지