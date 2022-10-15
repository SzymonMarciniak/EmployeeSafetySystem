from kivy.properties import ObjectProperty, NumericProperty, ListProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.stacklayout import StackLayout
from kivy.graphics.texture import Texture
from PoseModule.yolov7.utils.datasets import LoadImages
import cv2
import numpy as np
from kivy.clock import Clock
import time
from tensorflow.keras.models import load_model
import tensorflow as tf
from modules import global_vars
from modules.dbactions import connectToDatabase, closeDatabaseConnection
from PoseModule.yolov7.detect import detect as PoseDetect



print("9999999999999999999999")
cam_nr = 0
first_time = True
weights_pose = "PoseModule/yolov7/yolov7-w6-pose.pt"
view_img = True 
imgsz = 640 
half_precision = True 
kpt_label = True 
device = '' # GPU, if cpu = 'cpu'
conf_thres = .75
iou_thres = .45
classes = False 
agnostic_nms = False 
line_thickness = 8
empty = []
p_detect = PoseDetect(weights_pose, view_img, imgsz, half_precision, kpt_label, device, conf_thres, iou_thres,classes, agnostic_nms, line_thickness)
datasets = p_detect.setup()
model = load_model('imageclassifier.h5')

class CameraView(Image):
    cameraID = NumericProperty()

    def __init__(self, **kwargs):
        super(CameraView, self).__init__(**kwargs)
        

class CamerasLayout(StackLayout):
    def __init__(self, **kwargs):
        super(CamerasLayout, self).__init__(**kwargs)
        self.load_cameras()

    def load_cameras(self):
        db, cursor = connectToDatabase()
        cursor.execute("SELECT generated_id FROM cameras")
        results = cursor.fetchall()
        for row in results:
            rlayout = RLayout(cameraID=row[0])
            rlayout.cameraID = row[0]
            rlayout.source = 'img/pl.png'
            self.add_widget(rlayout)
        closeDatabaseConnection(db, cursor)

cam_view = []
cam_list = []

class RLayout(RelativeLayout):
    camera_view_parent = ObjectProperty()
    cameraID = NumericProperty()
    
    def __init__(self, **kwargs):
        super(RLayout, self).__init__(**kwargs)
        global cam_view
        camera = CameraView(cameraID=self.cameraID)
        self.camera_view_parent.add_widget(camera)
        cam_view.append(camera)
        

    @staticmethod
    def set_interval():
        Clock.schedule_interval(RLayout.iterate_images, 5)

    @staticmethod
    def iterate_images(dt):
        global cam_nr

        img_list, mask_lists, helmet_lists, img0_list = [], [], [], []

        if global_vars.AI_run:
            for dataset in datasets:
                try:
                    img, mask_list, helmet_list, img0 = p_detect.detect2(dataset)
                    img_list.append(img)
                    mask_lists.append(mask_list)
                    helmet_lists.append(helmet_list)
                    img0_list.append(img0) 
                except:
                    pass 
            
            for nr0, mask_list in enumerate(mask_lists):
                is_mask = True
                if mask_list != empty:
                    try:
                        for nr, img_m in enumerate(mask_lists[1]):
                            resize = tf.image.resize(img_m, (256,256))
                            pred = model.predict(np.expand_dims(resize/255, 0))
                            if pred < 0.5: 
                                print(f'Predicted class is Mask')
                            else:
                                print(f'Predicted class is No mask')
                                is_mask = False
                    except: print("Failed to load mask image")
                else: pass
            
                
                if not is_mask:
                    cam_id = cam_view[nr0].cameraID
                    print(f"On camera if id: {cam_id} detect no mask!!!") 
                    alert_color = [1,1,0,1]

            for nr, camera_image in enumerate(cam_view):
                if cam_nr < len(datasets):
                    cam_nr += 1
                    if isinstance(datasets[nr], LoadImages):
                        try:
                            if img_list[nr].any():
                                img = img_list[nr]
                                buffer = cv2.flip(img, 0).tobytes()
                                texture = Texture.create(size=(img.shape[1], img.shape[0]), colorfmt='bgr')
                                texture.blit_buffer(buffer, colorfmt='bgr', bufferfmt='ubyte')
                                camera_image.texture = texture
                            else:
                                camera_image.source = 'img/pl.png'
                        except: 
                            camera_image.source = 'img/pl.png'
                    else:
                        try:
                            if img0_list[nr]:
                                img = img0_list[nr]
                                img = np.array(img)
                                img = np.rot90(img, 2)
                                buffer = img.tobytes()
                                texture = Texture.create(size=(640,480 ), colorfmt='bgr')
                                texture.blit_buffer(buffer, colorfmt='bgr', bufferfmt='ubyte')
                                camera_image.texture = texture
                            else:
                                camera_image.source = 'img/pl.png'
                        except: 
                            camera_image.source = 'img/pl.png'
                else:
                    camera_image.source = 'img/pl.png'
            cam_nr = 0
     

class PopupContent(BoxLayout):
    def __init__(self, **kwargs):
        super(PopupContent, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.add_widget(Label(text="Camera ID: 7"))
        self.add_widget(Label(text="Room ID: 3"))
        self.add_widget(Label(text="Rules: 4"))


class InfoButton(Button):
    def __init__(self, **kwargs):
        super(InfoButton, self).__init__(**kwargs)

    def on_press(self):
        content = PopupContent()
        popup = Popup(title='Info about camera', content=content, auto_dismiss=True, size_hint=[.7, .7])
        popup.open()
