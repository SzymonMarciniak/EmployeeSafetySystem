import cv2 

from PoseModule.yolov7.detect import detect as PoseDetect
from tensorflow.keras.models import load_model
import tensorflow as tf
import numpy as np 


weights_pose = "PoseModule/yolov7/yolov7-w6-pose.pt"
view_img = True 
imgsz = 640 
half_precision = True 
kpt_label = True 
device = 'cpu' # GPU, if cpu = 'cpu'
conf_thres = .75
iou_thres = .45
classes = False 
agnostic_nms = False 
line_thickness = 8

empty = []

p_detect = PoseDetect(weights_pose, view_img, imgsz, half_precision, kpt_label, device, conf_thres, iou_thres,classes, agnostic_nms, line_thickness)
datasets = p_detect.setup()

model = load_model('imageclassifier.h5')

while True:
    for dataset in datasets:
        img, mask_list, helmet_list, img0 = p_detect.detect2(dataset) 

        if img != empty:
            cv2.imshow("full",img)
        
        if mask_list != empty:
            no_mask = False
            try:
                for nr, img_m in enumerate(mask_list):

                    cv2.imshow(f"mask{nr}",img_m)
                    resize = tf.image.resize(img_m, (256,256))
                    pred = model.predict(np.expand_dims(resize/255, 0))
                    print(f"Sure on {pred} %")
                    if pred < 0.5: 
                        print(f'Predicted class is Mask')
                    else:
                        print(f'Predicted class is No mask')
                        no_mask = True 
            except: print("Failed to load mask image")

            if no_mask:
                print("WARNING!!! No mask detected!!!")
            else: print("Everything is good")
        
        # if helmet_list != empty:
        #     try:
        #         cv2.imshow("helmet",helmet_list[0])
        #     except: pass
        
        if cv2.waitKey(5000) & 0xFF == ord('q'):
            break

