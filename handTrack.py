import cv2
import mediapipe as mp
import numpy as np
import pyautogui
import time
import threading

# Initialize MediaPipe hands module
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7,
    model_complexity=1
)

# Set up the webcam
cap = cv2.VideoCapture(0)
ret, frame = cap.read()
if not ret:
    print("Failed to capture video")
    exit(1)

# Configure PyAutoGUI
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0

# Get screen size
screen_width, screen_height = pyautogui.size()

# Define the portion of the camera view to map to the full screen (70% here)
inner_area_percent = 0.7

# Calculate the margins around the inner area
def calculate_margins(frame_width, frame_height, inner_area_percent):
    margin_width = frame_width * (1 - inner_area_percent) / 2
    margin_height = frame_height * (1 - inner_area_percent) / 2
    return margin_width, margin_height

# Convert video coordinates to screen coordinates
def convert_to_screen_coordinates(x, y, frame_width, frame_height, margin_width, margin_height):
    screen_x = np.interp(x, (margin_width, frame_width - margin_width), (0, screen_width))
    screen_y = np.interp(y, (margin_height, frame_height - margin_height), (0, screen_height))
    return screen_x, screen_y

# Function to get distance between two landmarks
def get_landmark_distance(landmark1, landmark2):
    x1, y1 = landmark1.x, landmark1.y
    x2, y2 = landmark2.x, landmark2.y
    distance = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    return distance

# Movement Thread for smoother cursor movement
class CursorMovementThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.daemon = True
        self.current_x, self.current_y = pyautogui.position()
        self.target_x, self.target_y = self.current_x, self.current_y
        self.running = True
        self.active = False
        self.jitter_threshold = 0.003

    def run(self):
        while self.running:
            if self.active:
                distance = np.hypot(self.target_x - self.current_x, self.target_y - self.current_y)
                screen_diagonal = np.hypot(screen_width, screen_height)
                if distance / screen_diagonal > self.jitter_threshold:
                    step = max(0.0001, distance / 12)  # Smoother movement
                    if distance != 0:
                        step_x = (self.target_x - self.current_x) / distance * step
                        step_y = (self.target_y - self.current_y) / distance * step
                        self.current_x += step_x
                        self.current_y += step_y
                        pyautogui.moveTo(self.current_x, self.current_y, _pause=False)
                time.sleep(0)
            else:
                time.sleep(0.1)

    def update_target(self, x, y):
        self.target_x, self.target_y = x, y

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False

    def stop(self):
        self.running = False

# Scrolling Thread for smooth scrolling with inertia
class ScrollThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.daemon = True
        self.scroll_queue = []
        self.scroll_lock = threading.Lock()
        self.running = True
        self.inertia = 0.95  # Slower reduction for rolling stop effect
        self.scroll_step = 0.01  # Smaller step for smoother scroll
        self.inertia_threshold = 0.01  # Minimum inertia scroll amount

    def run(self):
        while self.running:
            if self.scroll_queue:
                with self.scroll_lock:
                    scroll_amount = self.scroll_queue.pop(0)
                pyautogui.scroll(scroll_amount)
                # Apply inertia effect if the queue is empty
                if len(self.scroll_queue) == 0 and abs(scroll_amount) > self.inertia_threshold:
                    scroll_amount *= self.inertia
                    if abs(scroll_amount) > self.scroll_step:
                        with self.scroll_lock:
                            self.scroll_queue.append(scroll_amount)
            time.sleep(0.005)  # Increased frequency for smoother processing

    def add_scroll(self, scroll_amount):
        with self.scroll_lock:
            self.scroll_queue.append(scroll_amount)

    def stop(self):
        self.running = False

# Initialize the movement and scroll threads
movement_thread = CursorMovementThread()
scroll_thread = ScrollThread()
movement_thread.start()
scroll_thread.start()

# Initialize control variables
mouse_pressed = False
touch_threshold = 0.19
scroll_threshold = 0.005  # Smaller threshold for finer detection
scroll_sensitivity = 0.05  # Adjust this value for scrolling speed

try:
    previous_y = None
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

        # Check for the presence of hands
        if results.multi_hand_landmarks:
            movement_thread.activate()
            for hand_landmarks in results.multi_hand_landmarks:
                # Use the base of the ring finger (RING_FINGER_MCP) for tracking
                ring_finger_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_MCP]
                mcp_x = int(ring_finger_mcp.x * frame.shape[1])
                mcp_y = int(ring_finger_mcp.y * frame.shape[0])

                # Calculate margins based on the current frame size
                margin_width, margin_height = calculate_margins(frame.shape[1], frame.shape[0], inner_area_percent)

                # Convert video coordinates to screen coordinates
                target_x, target_y = convert_to_screen_coordinates(mcp_x, mcp_y, frame.shape[1], frame.shape[0], margin_width, margin_height)

                # Update target position in movement thread
                movement_thread.update_target(target_x, target_y)

                # Calculate the adaptive touch threshold based on the average length of fingers
                wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
                middle_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
                hand_size = get_landmark_distance(wrist, middle_finger_tip)
                adaptive_threshold = touch_threshold * hand_size

                # Check if index finger and thumb are touching (for clicking)
                index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
                index_thumb_distance = get_landmark_distance(index_tip, thumb_tip)

                if index_thumb_distance < adaptive_threshold:
                    if not mouse_pressed:
                        pyautogui.mouseDown()
                        mouse_pressed = True
                else:
                    if mouse_pressed:
                        pyautogui.mouseUp()
                        mouse_pressed = False

                # Check if middle finger and thumb are touching (for scrolling)
                middle_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
                middle_thumb_distance = get_landmark_distance(middle_tip, thumb_tip)

                if middle_thumb_distance < adaptive_threshold:
                    # Scroll gesture detection
                    if previous_y is not None:
                        delta_y = middle_tip.y - previous_y
                        if abs(delta_y) > scroll_threshold:
                            scroll_amount = delta_y * screen_height * scroll_sensitivity
                            scroll_thread.add_scroll(scroll_amount)

                    previous_y = middle_tip.y
                else:
                    previous_y = None
        else:
            # No hands detected
            if mouse_pressed:
                pyautogui.mouseUp()
                mouse_pressed = False
            movement_thread.deactivate()

        if cv2.waitKey(1) & 0xFF == 27:
            break

finally:
    movement_thread.stop()
    scroll_thread.stop()
    cap.release()
    cv2.destroyAllWindows()
