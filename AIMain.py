from PoseModule.yolov7.detect import detect as PoseDetect
from detect import detect as ObjectsDetect



source = "0" # 0 == webcam
weights_pose = "PoseModule/yolov7/yolov7-w6-pose.pt"
weights_custom = "models/yolov7_covidmask.pt"
view_img = True 
imgsz = 640 
half_precision = True 
kpt_label = True 
device = '0' # GPU, if cpu = 'cpu'
conf_thres = .25
iou_thres = .45
classes = False 
agnostic_nms = False 
line_thickness = 8
trace = True 

PoseDetect(weights_pose, view_img, imgsz, half_precision, kpt_label, source, device, conf_thres, iou_thres,classes, agnostic_nms, line_thickness)
#ObjectsDetect(source, weights_custom, view_img, imgsz, trace, device, conf_thres, iou_thres, classes, agnostic_nms, imgsz)
