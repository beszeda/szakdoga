import socket, cv2, pickle, struct, imutils
from datetime import datetime
import outputvideoanalyze
import threading
import queue

q = queue.Queue()
q2 = queue.Queue()

def camera():
    name = datetime.now().strftime("%y-%m-%d-%H-%M-%S")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host_name = socket.gethostname()
    #host_ip = socket.gethostbyname(host_name)
    host_ip = '127.0.0.1'
    print('HOST IP:', host_ip)
    port = 9999
    socket_address = (host_ip, port)

    # Socket Bind
    server_socket.bind(socket_address)

    # Socket Listen
    server_socket.listen(5)
    print("LISTENING AT:", socket_address)
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    result = cv2.VideoWriter('C:/Users/imreb/szakdoga/videos/' +name + '.avi', fourcc, 35, (640, 480))
    # Socket Accept
    i = 0
    while True:
        client_socket, addr = server_socket.accept()
        print('GOT CONNECTION FROM:', addr)
        if client_socket:
            vid = cv2.VideoCapture(0)

            while True:
                name2 = datetime.now().strftime("%y-%m-%d-%H-%M-%S")
                i = i + 1
                img, frame = vid.read()
                font = cv2.FONT_HERSHEY_PLAIN
                # frame = imutils.resize(frame, width=640, height=480)
                frame = cv2.putText(frame, name2, (480, 460), font, 1, (18, 18, 18), 2, cv2.LINE_AA)
                a = pickle.dumps(frame)
                message = struct.pack("Q", len(a)) + a
                client_socket.sendall(message)
                result.write(frame)
                if i == 350:
                    result.release()
                    result = cv2.VideoWriter('C:/Users/imreb/szakdoga/videos/' + name2 + '.avi', fourcc, 35, (640, 480))
                    i = 0
                    print("t0: " + 'C:/Users/imreb/szakdoga/videos/' + name + '.avi' )
                    q.put('C:/Users/imreb/szakdoga/videos/' + name + '.avi')
                    name = name2


def main():
    thread1 = threading.Thread(target=lambda: outputvideoanalyze.analyzevids(q , q2))
    thread2 = threading.Thread(target=lambda: outputvideoanalyze.sendemailS(q2))
    thread1.start()
    thread2.start()
    camera()
    thread1.join()
    thread2.join()


if __name__ == "__main__":
    main()




