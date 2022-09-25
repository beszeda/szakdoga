import os
import RPi.GPIO as GPIO
import time
from datetime import datetime
import numpy as np
import cv2
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

timeout = time.time() + 60*1   # 5 minutes from now
name = datetime.now().strftime("%y-%m-%d-%H-%M"+".avi")
def sendmail():
    email_user = 'pythonalertsender@gmail.com'
    email_password = 'cbjximkhhingytce'
    email_send = 'pythonalertsender@gmail.com'

    subject = 'security alert'

    msg = MIMEMultipart()
    msg['From'] = email_user
    msg['To'] = email_send
    msg['Subject'] = subject

    body = 'The PIR sensor detected some motion!'
    msg.attach(MIMEText(body, 'plain'))

    filename = name
    attachment = open(filename, 'rb')
    part = MIMEBase('application', 'octet-stream')
    part.set_payload((attachment).read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', "attachment; filename= " + filename)
    msg.attach(part)
    text = msg.as_string()
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(email_user, email_password)
    server.sendmail(email_user, email_send, text)
    server.quit()


def camera():
    # This will return video from the first webcam on your computer.
    cap = cv2.VideoCapture(0)
    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter( name, fourcc, 20.0, (640, 480))

    # loop runs if capturing has been initialized.
    while (True):
        # reads frames from a camera
        # ret checks return at each frame
        ret, frame = cap.read()
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        original = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # output the frame
        out.write(hsv)
        # The original input frame is shown in the window
       # cv2.imshow('Original', frame)
        # The window showing the operated video stream
        #cv2.imshow('frame', hsv)
        if time.time() > timeout:
           # cap.release()
           # out.release()
            break

def sensor():
    GPIO.setmode(GPIO.BCM)
    PIR_PIN = 7
    GPIO.setup(PIR_PIN, GPIO.IN)
    while True:
        if GPIO.input(PIR_PIN):
            print("Motion Detected!")
            time.sleep(1)
            return 1
        else:
            return 0


def run():
    print("start camera")
    time.sleep(2)
    print("started")
    camera()
#    time.sleep(6)
 #   print("sending mail")
  #  sendmail()

if sensor() == 1:
    run()
    time.sleep(3)
    print("asd")