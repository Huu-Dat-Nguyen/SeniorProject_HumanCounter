from ultralytics import YOLO

model = YOLO('YOLO/yolo11n.pt')
results = model('YOLO/bus.jpg')
results[0].show()