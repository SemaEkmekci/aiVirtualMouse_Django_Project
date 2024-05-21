from django.http import HttpResponse, StreamingHttpResponse
import cv2
import threading
import mediapipe as mp
import pyautogui
from django.shortcuts import render


def index(request):
    return render(request, "pages/index.html")

global_cam = None


class VideoCamera(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)
        (self.grabbed, self.frame) = self.video.read()
        threading.Thread(target=self.update, args=()).start()

    def get_frame(self):
        _, jpeg = cv2.imencode('.jpg', self.frame)
        return jpeg.tobytes()

    def update(self):
        while True:
            (self.grabbed, self.frame) = self.video.read()

def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


def virtualMouse(camera):
    handDetector = mp.solutions.hands.Hands()
    drawingUtils = mp.solutions.drawing_utils
    screenWidth, screenHeight = pyautogui.size()
    index_y = 0

    while True:
        _, frame = camera.video.read() 
        frame = cv2.flip(frame, 1)
        frameHeight, frameWidth, _ = frame.shape
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        output = handDetector.process(rgb_frame)
        hands = output.multi_hand_landmarks
        center = (frame.shape[1] // 2, frame.shape[0] // 3)
        cv2.line(frame, (center[0], 0), (center[0], frame.shape[0]), (0, 255, 0), 3)
        
        if hands:
            for hand in hands:
                drawingUtils.draw_landmarks(frame, hand)
                landmarks = hand.landmark
                for id, landmark in enumerate(landmarks):
                    x = int(landmark.x * frameWidth)
                    y = int(landmark.y * frameHeight)
                    print(x, y)

                    if id == 8:
                        cv2.circle(img=frame, center=(x, y), radius=10, color=(0, 255, 255))
                        index_x = screenWidth / frameWidth * x
                        index_y = screenHeight / frameHeight * y
                        pyautogui.moveTo(index_x, index_y)
                    if id == 4:
                        cv2.circle(img=frame, center=(x, y), radius=10, color=(0, 255, 255))
                        thumb_x = screenWidth / frameWidth * x
                        thumb_y = screenHeight / frameHeight * y
                        if abs(index_y - thumb_y) < 50:
                            pyautogui.click()
                            pyautogui.sleep(1)
                    if id == 20:
                        cv2.circle(img=frame, center=(x, y), radius=10, color=(0, 255, 255))
                        little_x = screenWidth / frameWidth * x
                        little_y = screenHeight / frameHeight * y
                        if abs(thumb_y-little_y) < 50:
                            pyautogui.click()
                            pyautogui.click()
                            pyautogui.sleep(1)
                    if id == 16:
                        cv2.circle(img=frame, center=(x, y), radius=10, color=(0, 255, 255))
                        thumb_x = screenWidth / frameWidth * x
                        thumb_y = screenHeight / frameHeight * y

                        print("center[0]",center[0])
                        print("thumb_x",thumb_x)
                        if thumb_x > 1100:
                            if thumb_y > index_y:  
                                pyautogui.scroll(15)  
                            elif thumb_y < index_y:  
                                pyautogui.scroll(-15) 
     
        _, jpeg = cv2.imencode('.jpg', frame)
        frame_bytes = jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n\r\n'
                b'<h1 style="position: absolute; left: 10px; top: 10px;">Hello, World!</h1>\r\n\r\n')

def stop_camera(request):
    global global_cam
    try:
        if global_cam:
            global_cam.video.release()  
            global_cam = None 
            return HttpResponse("Kamera başarıyla kapatıldı.")
        else:
            return HttpResponse("Kamera zaten kapalı.")
    except Exception as e:
        return HttpResponse("Kamera kapatılırken bir hata oluştu: {}".format(str(e)))
        

def Home(request):
    global global_cam
    try:
        if not global_cam:
            global_cam = VideoCamera()  
        return StreamingHttpResponse(virtualMouse(global_cam), content_type="multipart/x-mixed-replace; boundary=frame")
    except Exception as e:
        print(e)
        return HttpResponse("An error occurred.")
