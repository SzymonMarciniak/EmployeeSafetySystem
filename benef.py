# import os 

# viedos = os.listdir("/media/szymon/TOSHIBA EXT/Monitoring/01-03-2023")

# for vid in viedos:
#     pass


from PoseModule.yolov7.detect import detect as PoseDetect
from PoseModule.yolov7.utils.datasets import LoadImages
import cv2 

cam_view = []
cam_list = []
cam_nr = 0
first_time = True
weights_pose = "PoseModule/yolov7/yolov7-w6-pose.pt"
view_img = True
imgsz = 640
half_precision = True
kpt_label = True
device = ''  # GPU, if cpu = 'cpu'
conf_thres = .75
iou_thres = .45
classes = False
agnostic_nms = False
line_thickness = 8
empty = []
p_detect = PoseDetect(weights_pose, view_img, imgsz, half_precision, kpt_label, device, conf_thres, iou_thres, classes,
                      agnostic_nms, line_thickness)
datasets = p_detect.setup()



p = 0

while True:
    for nr, dataset in enumerate(datasets):
        img0, mask_list, helmet_list, vest_list, im0s, diff_x_list, diff_y_list, diff_z_list, x_list, y_list = p_detect.detect2(datasets[-1])

        if p%3==0:
            
            for nr2, (x,y) in enumerate(zip(x_list, y_list)):
                print(f"{nr2} ---> x:{x} y:{y}")

            cv2.imshow(f'Frame',img0)
        p+=1


        if cv2.waitKey(25) & 0xFF == ord('q'):
            break

