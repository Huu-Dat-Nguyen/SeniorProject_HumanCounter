from ultralytics import YOLO
from IPython.display import Image

model = YOLO('yolov8n.pt') 

results = model.train(
    data='C:/Users/nguye/OneDrive/Desktop/2024/Fall 24/Senior Project/SeniorProject_HumanCounter/YOLO/dataset/data.yaml',  # path to the data config file
    epochs=1,                     
    imgsz=320,                      
    batch=8,                    
    workers=4,                       
    half = True
)

print(results)

model.save('./YOLO/custom_model.pt')
