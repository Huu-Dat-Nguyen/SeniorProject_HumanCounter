import torch
from ultralytics import YOLO
from torchviz import make_dot

model = YOLO('./YOLO/custom_model.pt')


dummy_input = torch.randn(1, 3, 320, 320)


torch.onnx.export(
    model.model,           
    dummy_input,           
    "custom_model.onnx",     
    opset_version=11,      
    input_names=['input'], 
    output_names=['output'], 
    dynamic_axes={'input': {0: 'batch_size'}, 'output': {0: 'batch_size'}}  
)

print("Model exported to 'custom_model.onnx'")
