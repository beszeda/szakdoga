import socket, cv2, pickle, struct, imutils
from datetime import datetime
import outputvideoanalyze
import threading
import queue
import weak_flag


def camera(q, shouldStop):
    name = datetime.now().strftime("%y-%m-%d-%H-%M-%S")
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
    # Socket Accept
    client_socket, addr = server_socket.accept()
    print('GOT CONNECTION FROM:', addr)
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    result = cv2.VideoWriter('C:/Users/imreb/szakdoga/videos/' + name + '.avi', fourcc, 35, (640, 480))
    i = 0
    vid = cv2.VideoCapture(0)

    while not shouldStop.get():
        name2 = datetime.now().strftime("%y-%m-%d-%H-%M-%S")
        i = i + 1
        img, frame = vid.read()
        font = cv2.FONT_HERSHEY_PLAIN
        frame = cv2.putText(frame, name2, (480, 450), font, 1, (18, 18, 18), 2, cv2.LINE_AA)
        a = pickle.dumps(frame)
        message = struct.pack("Q", len(a)) + a
        client_socket.sendall(message)
        result.write(frame)
        if i == 4200:
            result.release()
            result = cv2.VideoWriter('C:/Users/imreb/szakdoga/videos/' + name2 + '.avi', fourcc, 35, (640, 480))
            i = 0
            print("t0: " + 'C:/Users/imreb/szakdoga/videos/' + name + '.avi')
            q.put('C:/Users/imreb/szakdoga/videos/' + name + '.avi')
            name = name2


def QueryConsol(shouldStop):
    while not shouldStop.get():
        command = input()
        if command == "exit":
            shouldStop.set(True)
        else:
            pass


def main():
    q = queue.Queue()
    q2 = queue.Queue()
    shouldStop = weak_flag.WeakFlag(False)
    inputThread = threading.Thread(target=lambda: QueryConsol(shouldStop))
    thread1 = threading.Thread(target=lambda: outputvideoanalyze.analyzevids(q, q2, shouldStop))
    thread2 = threading.Thread(target=lambda: outputvideoanalyze.sendemailS(q2, shouldStop))
    thread1.start()
    thread2.start()
    inputThread.start()
    camera(q, shouldStop)
    inputThread.join()
    thread1.join()
    thread2.join()


if __name__ == "__main__":
    main()
