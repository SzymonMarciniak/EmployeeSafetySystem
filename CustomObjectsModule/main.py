import os 
os.system("python Modules/yolov7/detect.py --weights Modules/yolov7/yolov7_covidmask.pt --conf 0.59 --img-size 640 --source 0 --view-img --no-trace")

