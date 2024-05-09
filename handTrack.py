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
    model_complexity=1, # You can experiment with this parameter (0, 1, 2)
)

# Set up the webcam
cap = cv2.VideoCapture(0)

# Get screen size
screen_width, screen_height = pyautogui.size()

# Define the portion of the camera view to map to the full screen (80% here)
inner_area_percent = 0.8  # This means 80% of the camera view maps to 100% of the screen

# Calculate the margins around the inner area
def calculate_margins(frame_width, frame_height, inner_area_percent):
    margin_width = frame_width * (1 - inner_area_percent) / 2
    margin_height = frame_height * (1 - inner_area_percent) / 2
    return margin_width, margin_height

# Convert video coordinates to screen coordinates
def convert_to_screen_coordinates(x, y, frame_width, frame_height, margin_width, margin_height):
    # Map the inner area (defined by the margins) to the full screen size
    screen_x = np.interp(x, (margin_width, frame_width - margin_width), (0, screen_width))
    screen_y = np.interp(y, (margin_height, frame_height - margin_height), (0, screen_height))
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

                # Calculate margins based on the current frame size
                margin_width, margin_height = calculate_margins(frame.shape[1], frame.shape[0], inner_area_percent)

                # Convert video coordinates to screen coordinates
                screen_x, screen_y = convert_to_screen_coordinates(mcp_x, mcp_y, frame.shape[1], frame.shape[0], margin_width, margin_height)

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
