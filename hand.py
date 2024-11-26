import cv2
import numpy as np

def detect_fingers(frame):
    # Convert the frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Apply GaussianBlur to reduce noise and improve contour detection
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Apply thresholding to create a binary image
    _, threshold = cv2.threshold(blurred, 100, 255, cv2.THRESH_BINARY_INV)

    # Find contours in the binary image
    contours, _ = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        # Simplify the contour to reduce points and potential self-intersections
        epsilon = 0.02 * cv2.arcLength(contour, True)
        simplified_contour = cv2.approxPolyDP(contour, epsilon, True)

        # Check if the simplified contour has at least three points
        if len(simplified_contour) >= 3:
            # Calculate the bounding rectangle
            x, y, w, h = cv2.boundingRect(simplified_contour)

            # Calculate the aspect ratio of the bounding rectangle
            aspect_ratio = float(w) / h

            # Set a depth range for finger detection (adjust these values)
            min_aspect_ratio = 0.3
            max_aspect_ratio = 1.5

            # Check if the aspect ratio is within the depth range
            if min_aspect_ratio < aspect_ratio < max_aspect_ratio:
                # Draw the bounding rectangle around the hand
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                # Find convex hull of the hand contour
                hull = cv2.convexHull(simplified_contour, returnPoints=False)

                # Check if the hull has at least three points
                if len(hull) >= 3:
                    # Find convexity defects
                    defects = cv2.convexityDefects(simplified_contour, hull)

                    if defects is not None:
                        finger_count = 0

                        for i in range(defects.shape[0]):
                            s, e, _, _ = defects[i, 0]

                            start = tuple(simplified_contour[s][0])
                            end = tuple(simplified_contour[e][0])

                            # Calculate the distance between the start and end points
                            distance = np.sqrt((end[0] - start[0])**2 + (end[1] - start[1])**2)

                            # If the distance is greater than a threshold, consider it as a finger
                            if distance > 30:
                                finger_count += 1
                                cv2.circle(frame, end, 5, (0, 0, 255), -1)

                        # Display the finger count
                        cv2.putText(frame, f"Fingers: {finger_count}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Display the result
    cv2.imshow('Finger Detection', frame)

# Open the webcam (you can also use a video file)
cap = cv2.VideoCapture(0)

while True:
    # Read a frame from the webcam
    ret, frame = cap.read()

    if not ret:
        break

    # Call the function to detect fingers
    detect_fingers(frame)

    # Exit the loop on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close all windows
cap.release()
cv2.destroyAllWindows()
