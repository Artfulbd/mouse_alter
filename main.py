import cv2
import mediapipe as mp
import HandTracker as ht
import time

cap = cv2.VideoCapture(0)

mpHands = mp.solutions.hands
hands = mpHands.Hands()
mpDraw = mp.solutions.drawing_utils





detector = ht.handDetector(detectionCon=0.7)
capture_interval = 10

while True:
    # reading image from video
    success, img = cap.read()
    
    if success == False :
        print("\n*************Camera is busy with other application******************\n")
        break

    # fixing mirror image
    #img = cv2.flip(img, 1)

    img = detector.findHands(img, drawFps=True)
    lmList = detector.findPosition(img, draw=False)
    lmList = lmList[0]
    if len(lmList) != 0:
      #print(lmList[4][1], lmList[8], lmList[12],lmList[16],lmList[20])
      thumb = tuple(lmList[4][1:])
      index = tuple(lmList[8][1:])
      middle = tuple(lmList[12][1:])
      ring = tuple(lmList[16][1:])
      pinky = tuple(lmList[20][1:])
      wrist = tuple(lmList[0][1:])
      detector.track(thumb, index, middle, ring, pinky, wrist)

    
      # circle around
      cv2.circle(img, thumb, 10, (255,0.255), cv2.FILLED)
      cv2.circle(img, index, 10, (255,0.255), cv2.FILLED)
      cv2.circle(img, middle, 10, (255,0.255), cv2.FILLED)
      cv2.circle(img, ring, 10, (255,0.255), cv2.FILLED)
      cv2.circle(img, pinky, 10, (255,0.255), cv2.FILLED)

        







    # showing image into screen
    cv2.imshow("Image", img)
    #time.sleep(capture_interval / 1000.0)
    if cv2.waitKey(1) == ord('q'):
        break

# releasing camera resorce
cap.release()
cv2.destroyAllWindows()



