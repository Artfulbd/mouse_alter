import cv2
import mediapipe as mp
import time
import math
import OsCordinator
import winsound
 
class handDetector():
    max, min = 0, 1000
    
    def __init__(self, mode=False, maxHands=2, detectionCon=0.5, trackCon=0.5):
        self.trigger = Trigger()
        self.mode = mode
        self.modelComplexity = 1
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon
        self.pTime, self.cTime = 0, 0
        
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode, self.maxHands, self.modelComplexity, self.detectionCon, self.trackCon)
        #self.hands = self.mpHands.Hands(False, 2, 0.7, 0.5)
        self.mpDraw = mp.solutions.drawing_utils
        self.tipIds = [4, 8, 12, 16, 20]

    # to keep track of time
    def printFPS(self, img):
        global cTime, max, min, pTime

        self.cTime = time.time()
        fps = 1 / (self.cTime - self.pTime)
        self.pTime = self.cTime

        cv2.putText(img, str(int (fps)), (10, 70), cv2.FONT_HERSHEY_COMPLEX, 3, (17, 122, 101), 3)


    def findHands(self, img, draw=True, drawFps=False):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)
        # print(results.multi_hand_landmarks)
    
        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms,self.mpHands.HAND_CONNECTIONS)
        if drawFps:
            self.printFPS(img)
        return img
    
    def findPosition(self, img, handNo=0, draw=True):
        xList = []
        yList = []
        bbox = []
        self.lmList = []
        if self.results.multi_hand_landmarks:
            self.myHand = self.results.multi_hand_landmarks[handNo]
            for id, lm in enumerate(self.myHand.landmark):
                # print(id, lm)
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                xList.append(cx)
                yList.append(cy)
                # print(id, cx, cy)
                self.lmList.append([id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 5, (255, 0, 255), cv2.FILLED)
            xmin, xmax = min(xList), max(xList)
            ymin, ymax = min(yList), max(yList)
            bbox = xmin, ymin, xmax, ymax

            if draw:
                cv2.rectangle(img, (bbox[0] - 20, bbox[1] - 20), (bbox[2] + 20, bbox[3] + 20), (0, 255, 0), 2)
        
        return self.lmList, bbox
    
    def fingersUp(self):
        fingers = []
        # Thumb
        if self.lmList[self.tipIds[0]][1] > self.lmList[self.tipIds[0] - 1][1]:
            fingers.append(1)
        else:
            fingers.append(0)
        # 4 Fingers
        for id in range(1, 5):
            if self.lmList[self.tipIds[id]][2] < self.lmList[self.tipIds[id] - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)
        return fingers
    
    def findDistance(self, p1, p2, img, draw=True):
    
        x1, y1 = self.lmList[p1][1], self.lmList[p1][2]
        x2, y2 = self.lmList[p2][1], self.lmList[p2][2]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        
        if draw:
            cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), 15, (255, 0, 255), cv2.FILLED)
            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
            cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)
        
        length = math.hypot(x2 - x1, y2 - y1)
        return length, img, [x1, y1, x2, y2, cx, cy]
    
    def detect_direction(self, reference_point, current_point):
        tolerance = 6
        _, y_ref = reference_point
        _, y_current = current_point

        current_distance = y_current - y_ref
        #print(current_distance, self.trigger.previous_distance)

        if current_distance > self.trigger.previous_distance and current_distance - self.trigger.previous_distance > tolerance:
            self.trigger.updateDistance(current_distance, "down")
            return "down"
        
        elif current_distance < self.trigger.previous_distance and self.trigger.previous_distance - current_distance > tolerance:
            self.trigger.updateDistance(current_distance, "up")
            return "up"
        
        return "no movement"
    
    def calculate_distance(self, point1, point2):
        x1, y1 = point1
        x2, y2 = point2
        distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        return distance
    
    def analyze_finger_tip_movement(self, previous_avg_distance, current_points):
        tolerance = 5
        current_avg_distance = self.calculate_average_distance(current_points)
        
        #print(current_avg_distance, previous_avg_distance)
        if current_avg_distance < previous_avg_distance and previous_avg_distance - current_avg_distance > tolerance:
            self.trigger.updateTipMovement(current_avg_distance, "closer")
            return "closer"
        elif current_avg_distance > previous_avg_distance and current_avg_distance - previous_avg_distance > tolerance:
            self.trigger.updateTipMovement(current_avg_distance, "apart")
            return "farther apart"
        else:
            return "not moving"

    def calculate_average_distance(self, points):
        total_distance = 0
        num_pairs = 0

        for i in range(len(points)):
            for j in range(i + 1, len(points)):
                distance = self.calculate_distance(points[i], points[j])
                total_distance += distance
                num_pairs += 1

        average_distance = total_distance / num_pairs
        return average_distance

        

    def track(self, thumb, index, middle, ring, pinky, wrist):
        reference_point = (330, 40)
        # check thumb is moving up or down
        #print(thumb, index, middle, ring, pinky, wrist)
        direction = self.detect_direction(reference_point, wrist)
        #print (direction)

        # finger tips
        finger_tip_state = self.analyze_finger_tip_movement(self.trigger.previous_avg_distance, [thumb, index, middle, ring, pinky, wrist])
        #print(finger_tip_state)


        # taking action
        self.trigger.takeAction()

        
 
class Trigger():
    # general
    sleep_interval = 1500
    last_update_time = 0.0
    last_update_time_thresh = 10 # second
    # for thumb
    thumb_move_trigger_thresh = 3
    previous_distance = 0
    prvious_thumb = []

    # finger tips
    tip_state_trigger_thresh = 3
    previous_avg_distance = 0
    previous_tip_state = []

    # trigger
    wrist_up = False
    wrist_down = False
    tips_closer = False
    tips_apart = False

    def __init__(self):
        self.flush()
        self.oc = OsCordinator.OsCordinator()

    def updateTime(self):
        self.last_update_time = time.time()
        #print("Time updating: ",self.last_update_time)
        

    def takeAction(self):
        #self.printState()
        time_interval = time.time() - self.last_update_time

        if self.tips_closer and self.tips_apart and self.wrist_up and self.wrist_down: 
            print("Flashing, interval:", time_interval)
            self.flush()

        if self.tips_closer and self.wrist_up and self.tips_apart:
            if (time_interval <= self.last_update_time_thresh):
                print("Screen 1 to 2, interval:", time_interval)
                self.oc.do_swapping(1)
                winsound.PlaySound("*", winsound.SND_ALIAS)
                time.sleep(self.sleep_interval / 1000.0)
            self.flush()
        elif self.tips_closer and self.wrist_down and self.tips_apart:
            if (time_interval <= self.last_update_time_thresh):
                print("Screen 2 to 1, interval:", time_interval)
                self.oc.do_swapping(2)
                winsound.PlaySound("*", winsound.SND_ALIAS)
                time.sleep(self.sleep_interval / 1000.0)
            self.flush()
        


    def printState(self):
        print("Wrist up:",self.wrist_up,"; Wrist down:",self.wrist_down,"; Tips closer:",self.tips_closer,"; Tips apart:",self.tips_apart)


    def updateDistance(self, updated_val, direction):
        self.previous_distance = updated_val
        self.prvious_thumb.append(direction)

        if self.prvious_thumb.count("up") > self.thumb_move_trigger_thresh:
            print("**************Trigger up****************")
            self.prvious_thumb = []
            self.wrist_up = True
            self.wrist_down = False
            self.updateTime()
            self.printState()

        elif self.prvious_thumb.count("down") > self.thumb_move_trigger_thresh:
            print("**************Trigger down****************")
            self.prvious_thumb = []
            self.wrist_down = True
            self.wrist_up = False
            self.updateTime()
            self.printState()
        
        if self.prvious_thumb.count("up") > 0 and self.prvious_thumb.count("down") > 0:
            self.prvious_thumb = []
            

    def updateTipMovement(self, update_val, state):
        self.previous_avg_distance = update_val
        self.previous_tip_state.append(state)

        if self.previous_tip_state.count("closer") > self.tip_state_trigger_thresh:
            print("##############tips getting closer##############")
            self.previous_tip_state = []
            self.tips_closer = True
            self.updateTime()
            self.printState()

            winsound.PlaySound("*", winsound.SND_ALIAS)

        elif self.previous_tip_state.count("apart") > self.tip_state_trigger_thresh:
            print("##############tipsgetting apart##############")
            self.previous_tip_state = []
            self.tips_apart = True
            self.updateTime()
            self.printState()

        if self.previous_tip_state.count("apart") > 0 and self.previous_tip_state.count("closer") > 0:
            self.previous_tip_state = []
            



    def flush(self):
        self.wrist_up = False
        self.wrist_down = False
        self.tips_closer = False
        self.tips_apart = False
        self.last_update_time = time.time()