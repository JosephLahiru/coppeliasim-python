import cv2
import numpy as np

# Define the lower and upper boundaries of the object in HSV color space
lower_bound = np.array([20, 100, 100])
upper_bound = np.array([30, 255, 255])
# Tracking the color Yellow

# Initialize the video capture device
cap = cv2.VideoCapture(0)

# Define the kernel for morphological operations
kernel = np.ones((5, 5), np.uint8)

# Define the screen dimensions
screen_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
screen_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

# Define the robot movement speed and direction
move_speed = 0.5
move_direction = 0

# Start a loop to continuously process the video frames
while True:
    # Read a frame from the video capture device
    ret, frame = cap.read()

    # Convert the color space from BGR to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Create a mask based on the defined lower and upper boundaries
    mask = cv2.inRange(hsv, lower_bound, upper_bound)

    # Apply morphological operations to remove noise
    mask = cv2.erode(mask, kernel, iterations=1)
    mask = cv2.dilate(mask, kernel, iterations=2)
    mask = cv2.erode(mask, kernel, iterations=1)

    # Find the contours of the object in the masked image
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # If at least one contour is found, track the largest one
    if len(contours) > 0:
        max_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(max_contour)

        # Calculate the centroid of the object
        cx = int(x + w / 2)
        cy = int(y + h / 2)

        # Draw a rectangle around the object
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Move the robot towards the object based on its position on the screen
        if cx < screen_width / 3:
            move_direction = -1
            print("Moving left")
        elif cx > 2 * screen_width / 3:
            move_direction = 1
            print("Moving right")
        else:
            move_direction = 0
        
    # Show the resulting image
    cv2.imshow('frame', frame)
    cv2.imshow('mask', mask)

    # Wait for a key press to exit the loop
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture device and destroy the windows
cap.release()
cv2.destroyAllWindows()
