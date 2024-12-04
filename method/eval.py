from ultralytics import YOLO

model_path = r'C:\Users\nguye\OneDrive\Desktop\2024\Fall 24\Senior Project\SeniorProject_HumanCounter\models\pt\custom_model.pt'
model = YOLO(model_path)

image_path = r'C:\Users\nguye\OneDrive\Desktop\2024\Fall 24\Senior Project\SeniorProject_HumanCounter\test_images\test4.jpg'
results = model.predict(image_path)

results[0].show()
