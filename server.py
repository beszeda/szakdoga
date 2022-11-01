import socket, queue, threading, cv2, pickle, struct
from datetime import datetime

import weak_flag
import outputvideoanalyze


def InitSockets(host, port):
    endpoint = (host, port)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(endpoint)
    server.listen(5)
    print(f"LISTENING AT: {host}:{port}")

    client, addr = server.accept()
    print('GOT CONNECTION FROM:', addr)

    return (server, client)


def SendFrame(client, frame):
    data = pickle.dumps(frame)
    message = struct.pack("Q", len(data)) + data
    client.sendall(message)


def Run(host, port, savedVideos, shouldStop):
    server, client = InitSockets(host, port)

    # Init video capture
    codec = cv2.VideoWriter_fourcc(*'XVID')
    font = cv2.FONT_HERSHEY_PLAIN
    cameraFeed = cv2.VideoCapture(0)

    # Init current video
    lastTime = datetime.now().strftime("%y-%m-%d-%H-%M-%S")
    currentTime = lastTime
    result = cv2.VideoWriter('C:/Users/imreb/szakdoga/videos/' + currentTime + '.avi', codec, 35, (640, 480))

    frameCount = 0
    frameCountToSave = 1400

    while not shouldStop.get():

        # Write a single frame
        currentTime = datetime.now().strftime("%y-%m-%d-%H-%M-%S")
        _, frame = cameraFeed.read()
        frame = cv2.putText(frame, currentTime, (480, 450), font, 1, (18, 18, 18), 2, cv2.LINE_AA)
        result.write(frame)
        frameCount += 1

        SendFrame(client, frame)

        if frameCount == frameCountToSave:
            result.release()
            savedVideos.put('C:/Users/imreb/szakdoga/videos/' + lastTime + '.avi')

            # Init next video
            lastTime = datetime.now().strftime("%y-%m-%d-%H-%M-%S")
            result = cv2.VideoWriter('C:/Users/imreb/szakdoga/videos/' + lastTime + '.avi', codec, 35, (640, 480))
            frameCount = 0

    client.close()
    server.close()


def QueryConsol(shouldStop):
    while not shouldStop.get():
        command = input()
        if command == "exit":
            shouldStop.set(True)
        else:
            pass


def Main():
    # Inter-thread communication objects
    savedVideos = queue.Queue()
    videosWithMotion = queue.Queue()
    shouldStop = weak_flag.WeakFlag(False)

    analyzationThread = threading.Thread(
        target=lambda: outputvideoanalyze.analyzevids(savedVideos, videosWithMotion, shouldStop))
    emailThread = threading.Thread(target=lambda: outputvideoanalyze.sendemailS(videosWithMotion, shouldStop))
    inputThread = threading.Thread(target=lambda: QueryConsol(shouldStop))

    analyzationThread.start()
    emailThread.start()
    inputThread.start()

    Run("127.0.0.1", 9999, savedVideos, shouldStop)

    inputThread.join()
    emailThread.join()
    analyzationThread.join()


if __name__ == "__main__":
    Main()


