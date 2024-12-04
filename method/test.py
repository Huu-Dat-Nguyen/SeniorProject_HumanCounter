from ultralytics import YOLO
import cv2
import os

# Load the YOLO model (replace with your specific model if trained)
model_path = 'YOLO/yolo11n.pt'  # Path to your model
model = YOLO(model_path)  # Load your custom trained model

# Path to your dataset YAML (not used in this code snippet)
dataset_yaml = "YOLO/People Detection.v8i.yolov11/data.yaml"

# Directory containing images to test
test_images_dir = "YOLO/People Detection.v8i.yolov11/test"

# Get all images in the test directory
image_files = [f for f in os.listdir(test_images_dir) if f.endswith(('.jpg', '.png', '.jpeg'))]

# Create output directory if it doesn't exist
output_dir = "output_images"
os.makedirs(output_dir, exist_ok=True)

# Iterate through each image file
for image_file in image_files:
    # Load image
    img_path = os.path.join(test_images_dir, image_file)
    img = cv2.imread(img_path)

    # Check if the image was loaded successfully
    if img is None:
        print(f"Error loading image {img_path}. Skipping...")
        continue

    # Perform detection on the image
    results = model(img)
    results[0].show()

    # Render results on the image
    frame_with_detections = results[0].plot()  # Get the plot of results

    # Display the frame with detections
    cv2.imshow('Detection Results', frame_with_detections)

    # Save the result
    output_path = os.path.join(output_dir, image_file)
    cv2.imwrite(output_path, frame_with_detections)

    # Wait for a key press or for 1 second before moving to the next image
    key = cv2.waitKey(1000)  # 1000 ms = 1 second
    if key == ord('q'):
        break

# Destroy all OpenCV windows
cv2.destroyAllWindows()
