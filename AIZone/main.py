import cv2
import mediapipe as mp
import time

from FallDetector import FallDetector

detecor = FallDetector()

mpDraw = mp.solutions.drawing_utils
mpPose = mp.solutions.pose
pose = mpPose.Pose()

cap = cv2.VideoCapture('videos/video_0.mp4')
pTime = 0

legs_head_landmarks = [27, 11, 28, 12] #left shouder, right shouder, left ankle ... 
legs_head_points = []

while True:
    success, img = cap.read()
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = pose.process(imgRGB)

    if results.pose_landmarks:
        mpDraw.draw_landmarks(img, results.pose_landmarks, mpPose.POSE_CONNECTIONS)
        for id, lm in enumerate(results.pose_landmarks.landmark):
            h, w, c = img.shape
            cx, cy = int(lm.x * w), int(lm.y * h)
            cv2.circle(img, (cx, cy), 5, (255, 0, 0), cv2.FILLED)
            if id in legs_head_landmarks:
                xy = (cx, cy)
                legs_head_points.append(xy)

        p1, p2 = detecor.calculate_center_line_points(legs_head_points)

        cv2.line(img, p1, p2, (0,255,0) ,6)
    
        detecor.check_body_position(legs_head_points)
    
        legs_head_points = []


    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime

    cv2.putText(img, str(int(fps)), (70, 50), cv2.FONT_HERSHEY_PLAIN, 3,
                (255, 0, 0), 3)

    cv2.imshow("Image", img)
    cv2.waitKey(1)

