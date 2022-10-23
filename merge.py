import socket, cv2, pickle, struct, imutils
import time
import traceback
from datetime import datetime
import numpy as np
from threading import Thread
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders


def servo():
    print("asd")

def sendmail(filename):
    email_user = 'pythonalertsender@gmail.com'
    email_password = 'dcktqchdwnmdugpi'
    email_send = 'pythonalertsender@gmail.com'

    subject = 'security alert'

    msg = MIMEMultipart()
    msg['From'] = email_user
    msg['To'] = email_send
    msg['Subject'] = subject

    body = 'The PIR sensor detected some motion!'
    msg.attach(MIMEText(body, 'plain'))

    #filename = name
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



def sensor():
    GPIO.setmode(GPIO.BCM)
    PIR_PIN = 7
    GPIO.setup(PIR_PIN, GPIO.IN)
    while True:
        if GPIO.input(PIR_PIN):
            return True

def camera():
    name = datetime.now().strftime("%y-%m-%d-%H-%M")

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host_name = socket.gethostname()
    host_ip = socket.gethostbyname(host_name)
    print('HOST IP:', host_ip)
    port = 9999
    socket_address = (host_ip, port)

    # Socket Bind
    server_socket.bind(socket_address)

    # Socket Listen
    server_socket.listen(5)
    print("LISTENING AT:", socket_address)
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    result = cv2.VideoWriter(name + '.avi', fourcc, 35, (640, 480))
    # Socket Accept
    i = 0
    while True:
        client_socket, addr = server_socket.accept()
        print('GOT CONNECTION FROM:', addr)
        if client_socket:
            vid = cv2.VideoCapture(0)

            while (True):
                name2 = datetime.now().strftime("%y-%m-%d-%H-%M")
                name = name2
                i = i + 1
                img, frame = vid.read()
                font = cv2.FONT_HERSHEY_PLAIN
                # frame = imutils.resize(frame, width=640, height=480)
                frame = cv2.putText(frame, name, (480, 460), font, 1, (18, 18, 18), 2, cv2.LINE_AA)
                a = pickle.dumps(frame)
                message = struct.pack("Q", len(a)) + a
                client_socket.sendall(message)
                # cv2.imshow('TRANSMITTING VIDEO', frame)

                result.write(frame)
                if i == 1800:
                    #print(name)
                    #print("asd")
                    result.release()
                    result = cv2.VideoWriter(name2 + '.avi', fourcc, 35, (640, 480))
                    i = 0


                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    client_socket.close()
                    # result.release()
    if sensor():
         try:
           sendmail(name)
         except:
            with open("exception.log", "a") as logfile:
               traceback.print_exc(file=logfile)


while True:
    camera()
    servo()

