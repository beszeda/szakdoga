import time
import traceback
import cv2
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import glob
import os
import datetime
import queue




def oldestFile():
    folder_path = r'C:/Users/imreb/szakdoga/'
    file_type = r'\*avi'
    files = glob.glob(folder_path + file_type)
    min_file = min(files, key=os.path.getctime)
    return min_file


def rmOldFiles():
    today = datetime.datetime.today()
    modified_date = datetime.datetime.fromtimestamp(os.path.getctime(oldestFile()))
    duration = today - modified_date

    if duration.days > 30:
        print(oldestFile())
        os.remove(oldestFile())


def sendmail(filename):
    print("sending....")
    email_user = 'pythonalertsender@gmail.com'
    email_password = 'dcktqchdwnmdugpi'
    email_send = 'pythonalertsender@gmail.com'

    subject = 'security alert'

    msg = MIMEMultipart()
    msg['From'] = email_user
    msg['To'] = email_send
    msg['Subject'] = subject

    body = 'The camera video analyze  detected some motion!'
    msg.attach(MIMEText(body, 'plain'))
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
    print("sent")


def analyzevids(q):
    while True:
        path = q.get()
        print("t1: " + path)
        cap = cv2.VideoCapture(path)

        ret, frame1 = cap.read()
        ret, frame2 = cap.read()
        i = 0
        while cap.isOpened():
            diff = cv2.absdiff(frame1, frame2)
            gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(gray, (5, 5), 0)
            _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
            dilated = cv2.dilate(thresh, None, iterations=3)
            contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            for contour in contours:
                (x, y, w, h) = cv2.boundingRect(contour)

                if cv2.contourArea(contour) < 900:
                    continue
                else:
                    cv2.rectangle(frame1, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.putText(frame1, "Status: {}".format('Movement'), (10, 20), cv2.FONT_HERSHEY_SIMPLEX,
                                1, (0, 0, 255), 3)
                    i = 1

            # cv2.drawContours(frame1, contours, -1, (0, 255, 0), 2)
            # cv2.imshow("feed", frame1)
            frame1 = frame2
            ret, frame2 = cap.read()
            if not ret:
                break

            key = cv2.waitKey(1)
            if key == ord('q'):
                break
        if i == 1:
            try:
                sendmail(path)
            except:
                with open("exception.log", "a") as logfile:
                    traceback.print_exc(file=logfile)
            #rmOldFiles()
