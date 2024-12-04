import cv2
import argparse
from ultralytics import YOLO
import supervision as sv
import numpy as np
from scipy.spatial import distance

total_objects_detected = 0
tracked_objects = {}  

def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="YOLOv8 live object detection and counting")
    parser.add_argument(
        "--webcam-resolution",
        default=[1280, 720],
        nargs=2,
        type=int,
        help="Set the webcam resolution as width and height (default: 1280x720)."
    )
    return parser.parse_args()

def calculate_centroid(box: np.ndarray) -> tuple:
    """
    Calculate the centroid of a bounding box.
    """
    x1, y1, x2, y2 = box
    return ((x1 + x2) / 2, (y1 + y2) / 2)

def is_new_object(centroid, tracked_objects, threshold=50):
    """
    Determine if the detected object is new based on its centroid and tracked objects.
    """
    for obj_id, obj_centroid in tracked_objects.items():
        if distance.euclidean(centroid, obj_centroid) < threshold:
            return False
    return True

def track_and_count_objects(detections: sv.Detections):
    """
    Track objects and count only new detections.
    """
    global total_objects_detected, tracked_objects
    new_objects = 0

    for box in detections.xyxy:
        centroid = calculate_centroid(box)
        if is_new_object(centroid, tracked_objects):
            tracked_objects[total_objects_detected] = centroid
            total_objects_detected += 1
            new_objects += 1
        else:
            for obj_id in tracked_objects:
                if distance.euclidean(centroid, tracked_objects[obj_id]) < 50:
                    tracked_objects[obj_id] = centroid
                    break

    return new_objects

def get_contrast_color(background_color: tuple) -> tuple:
    """
    Calculate a contrasting color for text based on the background color.
    """
    r, g, b = background_color
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    return (255, 255, 255) if luminance < 0.5 else (0, 0, 0)

def display_object_count(frame, current_count: int, total_count: int):
    """
    Display the current and total object counts in the top-right corner of the frame.
    """
    text_current = f"Current: {current_count}"
    text_total = f"Total: {total_count}"
    font_scale = 1
    font_thickness = 2

    background_color = frame[10, -10]  
    text_color = get_contrast_color(background_color)

    text_size_current = cv2.getTextSize(text_current, cv2.FONT_HERSHEY_SIMPLEX, font_scale, font_thickness)[0]
    text_size_total = cv2.getTextSize(text_total, cv2.FONT_HERSHEY_SIMPLEX, font_scale, font_thickness)[0]

    text_x = frame.shape[1] - max(text_size_current[0], text_size_total[0]) - 10
    text_y_current = 30
    text_y_total = 60

    cv2.putText(
        frame, text_current, (text_x, text_y_current),
        cv2.FONT_HERSHEY_SIMPLEX, font_scale, text_color, font_thickness
    )
    cv2.putText(
        frame, text_total, (text_x, text_y_total),
        cv2.FONT_HERSHEY_SIMPLEX, font_scale, text_color, font_thickness
    )

def main():
    args = parse_arguments()
    frame_width, frame_height = args.webcam_resolution

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)

    path = r'C:\Users\nguye\OneDrive\Desktop\2024\Fall 24\Senior Project\SeniorProject_HumanCounter\models\pt\yolov8l.pt'
    path = r'C:\Users\nguye\OneDrive\Desktop\2024\Fall 24\Senior Project\SeniorProject_HumanCounter\models\pt\custom_model.pt'
    model = YOLO(path)

    box_annotator = sv.BoxAnnotator(
        thickness=2,
        color=sv.ColorPalette.DEFAULT
    )

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read from webcam.")
            break

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        results = model(frame_rgb)

        if len(results[0].boxes) == 0:
            print("No detections in this frame.")
            current_count = 0
            annotated_frame = frame  
        else:
            detections = sv.Detections(
                xyxy=np.array([box.xyxy[0].cpu().numpy() for box in results[0].boxes]),
                confidence=np.array([box.conf[0].cpu().numpy() for box in results[0].boxes]),
                class_id=np.array([int(box.cls[0].cpu().numpy()) for box in results[0].boxes]),  # Cast class_id to int
            )

            current_count = track_and_count_objects(detections)

            annotated_frame = box_annotator.annotate(
                scene=frame,
                detections=detections
            )

        display_object_count(annotated_frame, current_count, total_objects_detected)

        cv2.imshow("YOLOv8 Object Detection", annotated_frame)

        if cv2.waitKey(30) == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
