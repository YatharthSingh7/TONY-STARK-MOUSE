import tkinter as tk
import pyautogui
import cv2
import mediapipe as mp

# Set up the hand tracking module
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()

# Start capturing video from the camera
cap = cv2.VideoCapture(0)

# Create a root window
root = tk.Tk()
root.title("Floating Keyboard")
root.attributes("-topmost", True)  # Keep the keyboard window on top of other windows

# Define the keyboard keys
keys = [
    ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
    ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
    ['Z', 'X', 'C', 'V', 'B', 'N', 'M']
]


# Create a function to handle key presses
def key_press(event):
    key = event.widget.cget("text")
    pyautogui.press(key)


# Create a function to type using the floating keyboard on a QWERTY layout
def type_text(text):
    pyautogui.typewrite(text)


# Increase the window size
root.geometry("1000x800")


# Create a virtual keyboard widget
class VirtualKeyboard(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.create_buttons()

    def create_buttons(self):
        for row in keys:
            key_frame = tk.Frame(self)
            key_frame.pack(pady=5)
            for key in row:
                key_button = tk.Button(key_frame, text=key, width=5, command=lambda key=key: self.type_key(key))
                key_button.pack(side=tk.LEFT, padx=2)

    def type_key(self, key):
        text_entry.insert(tk.END, key)


# Create the keyboard buttons
for row in keys:
    key_frame = tk.Frame(root)
    key_frame.pack(pady=5)
    for key in row:
        key_button = tk.Button(key_frame, text=key, width=5, command=lambda key=key: pyautogui.press(key))
        key_button.pack(side=tk.LEFT, padx=2)

# Create a frame for the typing function
type_frame = tk.Frame(root)
type_frame.pack(pady=10)

# Create an entry field and a button for typing
text_entry = tk.Entry(type_frame, font=("Arial", 12))
text_entry.pack(side=tk.LEFT, padx=5)
type_button = tk.Button(type_frame, text="Type", font=("Arial", 12), command=lambda: type_text(text_entry.get()))
type_button.pack(side=tk.LEFT)

# Create an instance of the virtual keyboard
virtual_keyboard = VirtualKeyboard(root)
virtual_keyboard.pack(pady=10)

while True:
    # Read a frame from the camera
    ret, frame = cap.read()

    if ret:
        # Flip the frame horizontally for a mirrored view
        frame = cv2.flip(frame, 1)

        # Convert the frame to RGB color space
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process the frame with the hand tracking module
        results = hands.process(rgb_frame)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Draw landmarks on the frame
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                # Get the coordinates of index finger tip and thumb tip
                index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]

                # Convert the coordinates to screen coordinates
                height, width, _ = frame.shape
                ix, iy = int(index_finger_tip.x * width), int(index_finger_tip.y * height)
                tx, ty = int(thumb_tip.x * width), int(thumb_tip.y * height)

                # Move the mouse to the index finger tip position
                pyautogui.moveTo(ix, iy, duration=0)

                # Check if the hand is within the keyboard region
                keyboard_x, keyboard_y = root.winfo_x(), root.winfo_y()
                keyboard_width, keyboard_height = root.winfo_width(), root.winfo_height()
                if (
                        keyboard_x < ix < keyboard_x + keyboard_width and
                        keyboard_y < iy < keyboard_y + keyboard_height
                ):
                    # Simulate a left-click when the thumb is close to the index finger
                    if ty < iy:
                        left_click = True
                        right_click = False
                    elif tx > ix:
                        right_click = True
                        left_click = False
                    else:
                        left_click = False
                        right_click = False
        # Display the frame with the hand tracking
        cv2.imshow('Hand Tracking', frame)

    # Check for keyboard input and exit if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture and destroythe windows
cap.release()
cv2.destroyAllWindows()


