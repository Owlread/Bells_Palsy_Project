import cv2
import mediapipe as mp
import math
import time

# MediaPipe Face Mesh configuration
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, min_detection_confidence=0.5)

# Function to calculate the distance between two points
def calculate_distance(point1, point2):
    return math.sqrt((point2[0] - point1[0]) ** 2 + (point2[1] - point1[1]) ** 2)

# Counter and status for monitoring
counter = 0
set_counter = 0  # Counter for the number of times it reaches 10
counting_enabled = True  # Status to monitor counting
start_time = None  # Start time to wait for 2 seconds

# Start camera
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Convert frame color to RGB as required by MediaPipe
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Detect face and landmarks
    result = face_mesh.process(rgb_frame)

    # Check if a face is detected
    if result.multi_face_landmarks:
        for face_landmarks in result.multi_face_landmarks:
            # Extract required landmarks from Face Mesh
            left_eye = (face_landmarks.landmark[159].x, face_landmarks.landmark[159].y)
            left_eyebrow = (face_landmarks.landmark[55].x, face_landmarks.landmark[55].y)
            right_eye = (face_landmarks.landmark[386].x, face_landmarks.landmark[386].y)
            right_eyebrow = (face_landmarks.landmark[285].x, face_landmarks.landmark[285].y)

            # Calculate the distance between the eyes and eyebrows on both sides
            left_distance = calculate_distance(left_eye, left_eyebrow)
            right_distance = calculate_distance(right_eye, right_eyebrow)

            # Check the condition if the distance is greater than or equal to 0.05
            if (left_distance >= 0.05 or right_distance >= 0.05) and counting_enabled:
                # Set the start time if it hasn't started yet
                if start_time is None:
                    start_time = time.time()

                # Check if 2 seconds have passed
                elif time.time() - start_time > 1:
                    counter += 1
                    counting_enabled = False  # Disable counting until the next condition is met
                    start_time = None  # Reset start time

            # Reset the status when the distance is below 0.05 on both sides
            if left_distance < 0.05 and right_distance < 0.05:
                counting_enabled = True  # Enable counting when the distance is below 0.05
                start_time = None  # Reset start time

            # Check if counter reaches 10
            if counter >= 10:
                set_counter += 1  # Increase set counter
                counter = 0  # Reset counter to 0

            # Convert landmark positions to fit the image coordinates
            h, w, _ = frame.shape
            left_eye = (int(left_eye[0] * w), int(left_eye[1] * h))
            left_eyebrow = (int(left_eyebrow[0] * w), int(left_eyebrow[1] * h))
            right_eye = (int(right_eye[0] * w), int(right_eye[1] * h))
            right_eyebrow = (int(right_eyebrow[0] * w), int(right_eyebrow[1] * h))

            # Draw points and display distance on the image
            cv2.circle(frame, left_eye, 3, (0, 255, 0), -1)
            cv2.circle(frame, left_eyebrow, 3, (0, 255, 0), -1)
            cv2.circle(frame, right_eye, 3, (0, 255, 0), -1)
            cv2.circle(frame, right_eyebrow, 3, (0, 255, 0), -1)
            cv2.putText(frame, f"Left Distance: {left_distance:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
            cv2.putText(frame, f"Right Distance: {right_distance:.2f}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

    # Display counter at the top-right corner of the screen
    cv2.putText(frame, f"Counter: {counter}", (frame.shape[1] - 250, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
    cv2.putText(frame, f"Sets: {set_counter}", (frame.shape[1] - 150, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    # Display the output
    cv2.imshow('Bells Palsy', frame)

    # Press 'q' to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Close everything
cap.release()
cv2.destroyAllWindows()
