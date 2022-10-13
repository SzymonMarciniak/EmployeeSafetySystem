from kivy.properties import ObjectProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.stacklayout import StackLayout
from kivy.graphics.texture import Texture
from PoseModule.yolov7.utils.datasets import LoadStreams, LoadImages
import cv2
import numpy as np
from kivy.clock import Clock
from tensorflow.keras.models import load_model

from modules.dbactions import connectToDatabase, closeDatabaseConnection
from PoseModule.yolov7.detect import detect as PoseDetect
cam_nr = 0
first_time = True

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
        
        
        Clock.schedule_interval(self.iterate_images, .5)


    @staticmethod
    def iterate_images(dt):
        global cam_nr

        img_list, mask_lists, helmet_lists, img0_list = [], [], [], []

        for dataset in datasets:
            img, mask_list, helmet_list, img0 = p_detect.detect2(dataset)
            img_list.append(img)
            mask_lists.append(mask_list)
            helmet_lists.append(helmet_list)
            img0_list.append(img0)
        print(f"RRRRRRR {len(img_list)} ------ {img_list[0]}")
        for nr, camera_image in enumerate(cam_view):
            if cam_nr < len(datasets):
                cam_nr += 1
                if isinstance(datasets[nr], LoadImages):
                    try:
                        if img_list[nr].any():
                            img = img_list[nr]
                            buffer = cv2.flip(img, 0).tobytes()
                            print(f"fopopopoo {img.shape[1], img.shape[0]}")
                            texture = Texture.create(size=(img.shape[1], img.shape[0]), colorfmt='bgr')
                            texture.blit_buffer(buffer, colorfmt='bgr', bufferfmt='ubyte')
                            camera_image.texture = texture
                        else:
                            camera_image.source = 'img/pl.png'
                    except Exception as err: 
                        print(f"OUT OFF INDEXX {err}")
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
                    except Exception as err: 
                        print(f"OUT OFF INDEXX {err}")
                        camera_image.source = 'img/pl.png'

            else:
                camera_image.source = 'img/pl.png'
        cam_nr = 0
        
        
        


    @staticmethod
    def check_available_cameras(cam_list: list):

        for i in range(0,50):
            cap = cv2.VideoCapture(i) 
            if cap is None or not cap.isOpened(): print("Ignore this")  
            else: cam_list.append(i)
        return cam_list



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
