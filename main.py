import RPi.GPIO as GPIO
import time
import requests
import cv2
from datetime import datetime

deurpin = 11
webpath = "/var/www/html"
webindex = "index.html"
telegram_token = "***REMOVED***"
telegram_chat_id = "***REMOVED***"
enable_notifications = False

def send_notification(message):
    url = f"https://api.telegram.org/bot{telegram_token}"
    params = {"chat_id": telegram_chat_id, "text": message}
    r = requests.get(url + "/sendMessage", params=params)
    print(r)


def deur_veranderd(status):
    log = "Deur is " + ("gesloten" if status else "open")
    write_log(log)
    print(log)

    if not status:
        take_picture()

    if enable_notifications:
        send_notification(log)


def write_log(log):
    today = str(datetime.now())
    f = open(webpath + "/" + webindex, "a")
    f.write(today + " " + log + "<hr/>")
    f.close()

def take_picture():
    time.sleep(1)
    picname = str(datetime.now().strftime("%s%m%d%Y")) + ".png"
    camera = cv2.VideoCapture(0)
    result, image = camera.read()
    cv2.imwrite(webpath + "/" + picname, image)
    f = open(webpath + "/" + webindex, "a")
    f.write("<img src=\"./" + picname + "\"<img/><hr/>")
    f.close()


GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(deurpin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
deurstatus = not GPIO.input(deurpin)


while True:
    status = not GPIO.input(deurpin)
    time.sleep(0.1)
    if status != deurstatus:
        deurstatus = status
        deur_veranderd(status)


GPIO.cleanup()
