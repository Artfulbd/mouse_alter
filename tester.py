import cv2
import mediapipe as mp

# Initialize Mediapipe Hand Tracking
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Open the camera
cap = cv2.VideoCapture(0)  # Change the index (0, 1, 2, etc.) to select a different camera

while True:
    # Read frame from the camera
    success, image = cap.read()
    if not success:
        break

    # Flip the image horizontally for a mirror effect
    image = cv2.flip(image, 1)

    # Convert the BGR image to RGB
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Process the image with Mediapipe
    results = hands.process(image_rgb)

    # Check if hand landmarks are detected
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Get the x and y coordinates of the palm (wrist) and opposite side of the palm
            palm_x = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].x
            palm_y = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].y

            opposite_x = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_MCP].x
            opposite_y = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_MCP].y

            # Draw circles to visualize the palm and opposite side of the palm
            image_height, image_width, _ = image.shape
            palm_x_pixel = int(palm_x * image_width)
            palm_y_pixel = int(palm_y * image_height)

            opposite_x_pixel = int(opposite_x * image_width)
            opposite_y_pixel = int(opposite_y * image_height)

            cv2.circle(image, (palm_x_pixel, palm_y_pixel), 5, (0, 255, 0), -1)
            cv2.circle(image, (opposite_x_pixel, opposite_y_pixel), 5, (255, 0, 0), -1)

    # Display the image
    cv2.imshow("Hand Tracking", image)

    # Break the loop when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the camera and close all windows
cap.release()
cv2.destroyAllWindows()
