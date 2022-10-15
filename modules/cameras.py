from kivy.properties import ObjectProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.stacklayout import StackLayout
from tensorflow.keras.models import load_model
from kivy.graphics.texture import Texture
from kivy.clock import Clock
import tensorflow as tf
import cv2
import numpy as np

from modules.dbactions import connectToDatabase, closeDatabaseConnection
from PoseModule.yolov7.detect import detect as PoseDetect
from PoseModule.yolov7.utils.datasets import LoadImages
from modules import global_vars

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

mask_model = load_model('models/mask_binar_classifier.h5')
helmet_model = load_model('models/helmet_binar_classifier.h5')

failed_load_camera_img = 'img/pl.png'

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
            rlayout.source = 'img/test.png'
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
                    print("Failed to load camera or video is over") 

            
            db, cursor = connectToDatabase()
            cursor.execute(f"SELECT rules FROM cameras WHERE workspace_id = {global_vars.choosenWorkplace}")
            rules_list = cursor.fetchall()
            closeDatabaseConnection(db, cursor)

            for nr0, img in enumerate(img_list):
                if "1" in rules_list[nr0]:
                    object_name = "mask"
                    object_lists = mask_lists
                    model = mask_model

                    is_danger = RLayout.do_predictions(object_lists, object_name, nr0, model)

                    if is_danger:
                        cam_id = cam_view[nr0].cameraID
                        print(f"On camera of id: {cam_id} detect no {object_name}!!!") 
                        alert_color = [1,1,0,1]
                
                if "2" in rules_list[nr0]:
                    object_name = "helmet"
                    object_lists = helmet_lists
                    model = helmet_model

                    is_danger = RLayout.do_predictions(object_lists, object_name, nr0, model)

                    if is_danger:
                        cam_id = cam_view[nr0].cameraID
                        print(f"On camera of id: {cam_id} detect no {object_name}!!!") 
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
                                camera_image.source = failed_load_camera_img
                        except: 
                            camera_image.source = failed_load_camera_img
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
                                camera_image.source = failed_load_camera_img
                        except: 
                            camera_image.source = failed_load_camera_img
                else:
                    camera_image.source = failed_load_camera_img
            cam_nr = 0

    @staticmethod
    def do_predictions(object_lists, object_name, nr0, model):
        danger = False
        if object_lists != empty:
            try:
                entire_img = object_lists[nr0]
                if entire_img != empty:
                    for crop_image in entire_img:
                        resize = tf.image.resize(crop_image, (256,256))
                        pred = model.predict(np.expand_dims(resize/255, 0))
                        print(f"\n\n\n {pred}")
                        if pred < 0.5: 
                            print(f'Predicted class is {object_name}')
                        else:
                            print(f'Predicted class is No {object_name}')
                            danger = True
            except Exception as err: 
                print(f"Failed to load {object_name} image --- {err}")
        return danger


class PopupContent(BoxLayout):
    generatedID = NumericProperty()

    def __init__(self, **kwargs):
        super(PopupContent, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.add_widget(Label(text=str(self.generatedID)))
        self.add_widget(Label(text="Room ID: 3"))
        self.add_widget(Label(text="Rules: 4"))


class InfoButton(Button):
    def __init__(self, **kwargs):
        super(InfoButton, self).__init__(**kwargs)

    def on_press(self):
        content = PopupContent(generatedID=self.parent.generatedID)
        popup = Popup(title='Info about camera', content=content, auto_dismiss=True, size_hint=[.7, .7])
        popup.open()
