import cv2
import mediapipe as mp
import math
import numpy as np
import time
import pygame

# Initialize pygame mixer for playing sound
pygame.mixer.init()

# Initialize Mediapipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1)

# Function to play notification sounds
def play_sound(sound_path):
    pygame.mixer.music.load(sound_path)
    pygame.mixer.music.play()

def notified2():
    play_sound('S1/notified2.mp3')

def set1():
    play_sound('S1/set1.mp3')

def set2():
    play_sound('S1/set2.mp3')

def set3():
    play_sound('S1/set3.mp3')

def n3():
    play_sound('S1/3.mp3')

# Function to calculate Euclidean distance
def calculate_distance(point1, point2):
    return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)

# Variables to store distances for moving average
left_eyebrow_distances = []
right_eyebrow_distances = []
window_size = 10  # Window size for moving average
counter = 0  # Counter for number of times the distance is less than or equal to 48
is_close = False  # State variable to check if distance is below or equal to 48
set_count = 0  # Count the number of times counter reaches 10
start_time = None  # Variable to store the time when distance becomes <= 48
end = False

# OpenCV Video Capture
cap = cv2.VideoCapture(0)
n3()

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    # Convert the frame to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb_frame)

    # Check if face landmarks are detected
    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            # Get the coordinates of the nose and eyebrow landmarks
            nose_tip = face_landmarks.landmark[1]
            left_eyebrow = face_landmarks.landmark[55]
            right_eyebrow = face_landmarks.landmark[285]

            # Convert landmarks to pixel positions
            nose_tip_pos = (int(nose_tip.x * frame.shape[1]), int(nose_tip.y * frame.shape[0]))
            left_eyebrow_pos = (int(left_eyebrow.x * frame.shape[1]), int(left_eyebrow.y * frame.shape[0]))
            right_eyebrow_pos = (int(right_eyebrow.x * frame.shape[1]), int(right_eyebrow.y * frame.shape[0]))

            # Calculate the distance between nose and each eyebrow
            distance_left_eyebrow = calculate_distance(nose_tip_pos, left_eyebrow_pos)
            distance_right_eyebrow = calculate_distance(nose_tip_pos, right_eyebrow_pos)

            # Append distances to lists and maintain window size
            left_eyebrow_distances.append(distance_left_eyebrow)
            right_eyebrow_distances.append(distance_right_eyebrow)
            if len(left_eyebrow_distances) > window_size:
                left_eyebrow_distances.pop(0)
            if len(right_eyebrow_distances) > window_size:
                right_eyebrow_distances.pop(0)

            # Calculate moving average for both distances
            avg_left_eyebrow_distance = np.mean(left_eyebrow_distances)
            avg_right_eyebrow_distance = np.mean(right_eyebrow_distances)

            # Check if average distances are less than or equal to 40 and not already close
            if (avg_left_eyebrow_distance <= 80 or avg_right_eyebrow_distance <= 80) and not is_close:
                start_time = time.time()
                is_close = True
            elif (avg_left_eyebrow_distance > 79 and avg_left_eyebrow_distance < 90 or avg_right_eyebrow_distance > 79 and avg_right_eyebrow_distance <90):
                cv2.putText(frame, f"OK", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 4)
            # If is_close is True and 2 seconds have passed
            if is_close and start_time and time.time() - start_time >= 1:
                counter += 1
                start_time = None
                is_close = False

            # Reset the state if the distance goes above 48
            elif avg_left_eyebrow_distance > 80 and avg_right_eyebrow_distance > 80:
                is_close = False
                start_time = None

            # Check if counter reaches 10
            if counter == 3:
                set_count += 1
                counter = 0

            # Play corresponding set sound
                if set_count == 1 and counter == 0:
                    set1()
                elif set_count == 2 and counter == 0:
                    set2()
                elif set_count == 3 and counter == 0:
                    set3()
                    time.sleep(3)
                    end = True

            # Display the smoothed distances on the frame
            cv2.putText(frame, f"Distance (Left Eyebrow): {int(avg_left_eyebrow_distance)}", (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
            cv2.putText(frame, f"Distance (Right Eyebrow): {int(avg_right_eyebrow_distance)}", (50, 70),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

            # Draw circles around the landmarks
            cv2.circle(frame, nose_tip_pos, 5, (0, 255, 0), -1)
            cv2.circle(frame, left_eyebrow_pos, 5, (255, 0, 0), -1)
            cv2.circle(frame, right_eyebrow_pos, 5, (0, 0, 255), -1)

    # Display the counter and set count at the top-right corner of the frame
    cv2.putText(frame, f"Counter: {counter}", (frame.shape[1] - 200, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.putText(frame, f"Set: {set_count}", (frame.shape[1] - 150, 100),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    if end == True:
        break
    # Display the frame
    cv2.imshow('Bells Palsy', frame)
    if cv2.waitKey(5) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
pygame.mixer.quit()
