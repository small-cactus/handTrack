import cv2
import mediapipe as mp
import numpy as np
import pyautogui

# Initialize MediaPipe hands module
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7,
    model_complexity=1,  # You can experiment with this parameter (0, 1, 2)
)

# Initialize MediaPipe drawing module
mp_drawing = mp.solutions.drawing_utils

# Set up the webcam
cap = cv2.VideoCapture(0)

# Get screen size
screen_width, screen_height = pyautogui.size()

# Convert video coordinates to screen coordinates
def convert_to_screen_coordinates(x, y, frame_width, frame_height):
    screen_x = np.interp(x, (0, frame_width), (0, screen_width))
    screen_y = np.interp(y, (0, frame_height), (0, screen_height))
    return screen_x, screen_y

# Function to check if two fingertips are touching
def are_fingertips_touching(tip1, tip2, threshold=87):
    x1, y1 = tip1
    x2, y2 = tip2
    distance = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    return distance < threshold

# Initialize the flag that controls the click action
fingertips_touching = False

try:
    while True:
        # Read a frame from the webcam
        ret, frame = cap.read()
        if not ret:
            continue

        # Flip the frame horizontally for a natural selfie-view, and convert the BGR image to RGB
        frame = cv2.cvtColor(cv2.flip(frame, 1), cv2.COLOR_BGR2RGB)

        # Process the frame and find hands
        results = hands.process(frame)

        # Convert the frame color back so it can be displayed
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        # Extract hand landmarks
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Get the base of the middle finger (MCP joint)
                middle_finger_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP]
                mcp_x = int(middle_finger_mcp.x * frame.shape[1])
                mcp_y = int(middle_finger_mcp.y * frame.shape[0])

                # Convert video coordinates to screen coordinates
                screen_x, screen_y = convert_to_screen_coordinates(mcp_x, mcp_y, frame.shape[1], frame.shape[0])

                # Move the mouse
                pyautogui.moveTo(screen_x, screen_y)

                # Check if index finger and thumb are touching
                index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]

                index_pos = (int(index_tip.x * frame.shape[1]), int(index_tip.y * frame.shape[0]))
                thumb_pos = (int(thumb_tip.x * frame.shape[1]), int(thumb_tip.y * frame.shape[0]))

                # Click the mouse if index and thumb are touching
                if are_fingertips_touching(index_pos, thumb_pos):
                    if not fingertips_touching:
                        pyautogui.click()
                        fingertips_touching = True
                else:
                    fingertips_touching = False

        if cv2.waitKey(1) & 0xFF == 27:
            break
finally:
    cap.release()
    cv2.destroyAllWindows()
