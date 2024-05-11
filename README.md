# handTrack
> This Python script allows you to control your computer's mouse cursor using hand gestures, with the help of a webcam. It uses OpenCV for image processing, MediaPipe for hand tracking, and PyAutoGUI for simulating mouse movements and clicks.

<p align="center">
  <img src="handTrack.png" width="200">
</p>

## Features
- **Mouse Movement**: Just move your hand in front of the screen to control the mouse, your palm should be facing the camera like you're using the force.
- **Mouse Click**: Touch your index and thumb together to click the mouse.

## Demos
### Accuracy even at range, 1080p webcam
https://github.com/small-cactus/handTrack/assets/125771841/9bd73899-23d6-4333-980b-56a602728c6e
> This is a combined 2 videos from a screen recording and my phone, there is no VFX, and no processing, everything you see is how it actually is when you use it. The webcam used in this video is the one in the MacBook.

### Extremely accurate click detection

https://github.com/small-cactus/handTrack/assets/125771841/c43e9694-5947-44b0-a232-ce0945ccc05d
> This video has nothing special done to it, no tunings tweaked, no higher resolution camera, just everything from my MacBook.

## How Our Hand Tracking System Works

Here's why our hand tracking system stands out from the competition:

- **Absolute Hand Tracking**: Our system implements absolute hand tracking, meaning that specific hand positions always correspond to the same screen locations. This feature ensures predictable and intuitive control, enhancing the user experience by making interactions more natural and consistent.

- **Mapped Camera to Screen**: Our system maps the camera view to a specific portion of the screen, allowing full-screen hand tracking without the common issue of reaching tracking limits. This mapping ensures users can navigate the entire screen smoothly with their hand movements.

- **Dynamic Mouse Steps for Low FPS**: We generate dynamic mouse steps to compensate for low camera frame rates, ensuring the mouse movement remains smooth and responsive. This feature is crucial for maintaining a high-quality user experience, even when camera input is slower.

- **Real-Time, Multithreaded Processing**: The system runs on a separate thread and calculates hand tracking in real-time. This approach minimizes latency and maximizes performance, providing instant response to hand movements.

- **Advanced Click Detection**: Our click detection algorithm is more refined than typical systems. Not only do we detect if the thumb and index finger are touching, but we also monitor the overall hand size changes. This method helps prevent accidental clicks and allows reliable activation from varying distances from the camera.

- **Smart Hand Presence Detection**: The system automatically disables hand tracking when no hands are detected and allows tracking for only one hand at a time. This prevents accidental mouse control from nearby people and ensures that the system is both secure and user-centric.



## Prerequisites

Before you can use this script, you'll need to have Python installed on your machine, along with a few libraries. This guide assumes you have Python 3.6 or newer. (I used 3.11)

## Installation
> [!WARNING]
> This script is optimized for a Macbook Pro Retina Display, meaning if you are using anything higher or lower resolution, hand tracking may or may not work.

1. **Clone the Repository**
   First, clone this repository to your local machine using:

   ```bash
   git clone https://github.com/small-cactus/handTrack.git
   cd handTrack
   ```

2. **Set Up a Python Virtual Environment** (optional but recommended)

   ```bash
   python -m venv venv
   
   venv\Scripts\activate      # On Windows
   
   source venv/bin/activate   # On macOS and Linux
   ```

3. **Install Required Libraries**
   Install the required Python libraries with:

   ```
   pip install -r requirements.txt
   ```

   Here's what's installed, you don't need to do any step for this:

   ```
   opencv-python==4.5.5.64
   mediapipe==0.8.11
   numpy==1.23.3
   pyautogui==0.9.53
   ```

## Configuration (In case defaults don't work)

Before running the script, you might need to adjust a few parameters based on your webcam setup and personal preferences:

- **Camera Index**: If your system has multiple cameras and the script does not use the correct one, change the `cap = cv2.VideoCapture(0)` line. Replace `0` with the index of the desired camera.
- **Detection Confidence**: Adjust `min_detection_confidence` and `min_tracking_confidence` in the hand tracking setup section if the script is too sensitive or not sensitive enough.
- **Model Complexity**: Change `model_complexity` in the hand detection setup. Use `1` (default) for a balance between performance and accuracy, or try `0` for faster but less accurate detection, and `2` for more accurate but slower detection.
- **Distance Threshold**: If your fingers need to be closer or further apart to register a click, modify the `touch_threshold` value. This value measures changes in overall hand size, like what happens when you click your index and thumb together.

## Usage

Run the script from your command line:

   ```
   python3 handTrack.py
   ```

Make sure you have sufficient lighting and your hand is visible to the webcam for best performance.

## Troubleshooting

- **Script Doesn't Recognize Hand Movements**: Ensure your hand is well-lit and within the frame. Adjust the confidence thresholds if necessary.
- **Mouse Movements Are Erratic**: Try adjusting the screen coordinates mapping in `convert_to_screen_coordinates` to match your screen size more accurately.
- **Clicks Are Not Registering**: Modify the `touch_threshold`. You might need to increase or decrease this value based on your hand size.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
