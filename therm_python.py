import os
import glob
import time
import RPi.GPIO as GPIO
from tb_device_mqtt import TBDeviceMqttClient, TBPublishInfo

GPIO.setmode(GPIO.BOARD)
GPIO.setup(16, GPIO.OUT)

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

telemetry = {"temperature": 41.9, "enabled": False, "currentFirmwareVersion": "v1.2.2"}
client = TBDeviceMqttClient("thingsboard.cloud", username="2o52a4j2x8g1olcqi43e")

def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        return temp_c

client.connect()

while True:
    actual_temp = read_temp()
    print("Temp is: ", actual_temp)
    time.sleep(1)
    telemetry["temperature"] = actual_temp
    client.send_telemetry(telemetry)
    result = client.send_telemetry(telemetry)
    success = result.get() == TBPublishInfo.TB_ERR_SUCCESS
    if actual_temp > 19:
        GPIO.output(16, GPIO.HIGH)
        print("Compressor is ON")
    else:
        GPIO.output(16, GPIO.LOW)
        print("Compressor is OFF")

client.disconnect()
