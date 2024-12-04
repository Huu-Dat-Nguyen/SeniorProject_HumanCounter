
from roboflow import Roboflow
rf = Roboflow(api_key="pczbJGsmqdG2lshooCer")
project = rf.workspace("leo-ueno").project("people-detection-o4rdr")
version = project.version(8)
dataset = version.download("yolov11")
print("done")