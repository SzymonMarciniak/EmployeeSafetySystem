import argparse

from Modules.yolov7.detect import detect 

source = "0" # 0 == webcam

parser = argparse.ArgumentParser()
parser.add_argument('--weights', nargs='+', type=str, default='yolov7-w6-pose.pt', help='model.pt path(s)')
parser.add_argument('--source', type=str, default='/home/szymon/Downloads/tokio.mp4', help='source') 
parser.add_argument('--img-size', nargs= '+', type=int, default=640, help='inference size (pixels)')
parser.add_argument('--conf-thres', type=float, default=0.25, help='object confidence threshold')
parser.add_argument('--iou-thres', type=float, default=0.45, help='IOU threshold for NMS')
parser.add_argument('--device', default='', help='cuda device, i.e. 0 or 0,1,2,3 or cpu')
parser.add_argument('--view-img', default=True, action='store_true', help='display results')
parser.add_argument('--save-txt', action='store_true', help='save results to *.txt')
parser.add_argument('--save-txt-tidl', action='store_true', help='save results to *.txt in tidl format')
parser.add_argument('--save-bin', action='store_true', help='save base n/w outputs in raw bin format')
parser.add_argument('--save-conf', action='store_true', help='save confidences in --save-txt labels')
parser.add_argument('--save-crop', action='store_true', help='save cropped prediction boxes')
parser.add_argument('--nosave', default=True, action='store_true', help='do not save images/videos')
parser.add_argument('--classes', nargs='+', type=int, help='filter by class: --class 0, or --class 0 2 3')
parser.add_argument('--agnostic-nms', action='store_true', help='class-agnostic NMS')
parser.add_argument('--augment', action='store_true', help='augmented inference')
parser.add_argument('--update', action='store_true', help='update all models')
parser.add_argument('--project', default='runs/detect', help='save results to project/name')
parser.add_argument('--name', default='exp', help='save results to project/name')
parser.add_argument('--exist-ok', action='store_true', help='existing project/name ok, do not increment')
parser.add_argument('--line-thickness', default=8, type=int, help='bounding box thickness (pixels)')
parser.add_argument('--hide-labels', default=False, action='store_true', help='hide labels')
parser.add_argument('--hide-conf', default=False, action='store_true', help='hide confidences')
parser.add_argument('--kpt-label', default=True, action='store_true', help='use keypoint labels')
opt = parser.parse_args()
print(opt)

detect(opt, source)