import RPi.GPIO as GPIO
import time
import requests
import cv2
import os
from datetime import datetime

# conf
door_gpio = 23
disable_gpio = 21
webpath = "/var/www/html"
webindex = "index.html"
telegram_token = os.environ.get("telegramtoken")
telegram_chat_id = os.environ.get("telegramchatid")
enable_notifications = True

# vars
is_closed = False
is_disabled = False

def send_notification(message):
    if not is_disabled:
        print("Sending Telegram message!")
        url = f"https://api.telegram.org/bot{telegram_token}"
        params = {"chat_id": telegram_chat_id, "text": message}
        r = requests.get(url + "/sendMessage", params=params)
        print("Success!" if r.status_code == 200 else "Failure!")


def is_closed_changed(is_closed):
    log = "Door is " + ("closed!" if is_closed else "open!")
    write_log(log)
    print(log)

    if not is_closed:
        take_picture()

    if enable_notifications:
        send_notification(log)

def write_log(log):
    today = str(datetime.now())
    print("Writing to logs.")
    f = open(webpath + "/" + webindex, "a")
    f.write(today + " " + log + "<hr/>")
    f.close()


def take_picture():
    if not is_disabled:
        print("Taking picture.")
        time.sleep(1)
        picname = str(datetime.now().strftime("%s%m%d%Y")) + ".png"
        camera = cv2.VideoCapture(0)
        result, image = camera.read()
        image = cv2.rotate(image, cv2.ROTATE_180)
        cv2.imwrite(webpath + "/" + picname, image)
        f = open(webpath + "/" + webindex, "a")
        f.write("<img src=\"./" + picname + "\"<img/><hr/>")
        f.close()
    else:
        print("Attempted to take a picture but pictures are disabled!")

def disable_changed(disabled):
    log = "Pictures/messages Off" if disabled else "Pictures/messages On"
    write_log(log)
    print(log)


GPIO.setmode(GPIO.BOARD)


# Door pin
GPIO.setup(door_gpio, GPIO.IN)
# Disable Pin
GPIO.setup(disable_gpio, GPIO.IN)

is_closed = GPIO.input(door_gpio)
is_disabled = GPIO.input(disable_gpio)
print("Ready to go!")
print("Current state: " + ("Pictures/messages Off" if is_disabled else "Pictures/messages On"))
print("Door is currently: " + ("closed!" if is_closed else "open!"))
while True:
    time.sleep(0.1)

    status = GPIO.input(door_gpio)
    if status != is_closed:
        is_closed = status
        is_closed_changed(status)

    disabled = GPIO.input(disable_gpio)
    if disabled != is_disabled:
        is_disabled = disabled
        disable_changed(disabled)

GPIO.cleanup()
