from kivy.properties import ObjectProperty, NumericProperty
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.screenmanager import Screen
from tensorflow.keras.models import load_model
from kivy.uix.stacklayout import StackLayout
from kivy.graphics.texture import Texture
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.clock import Clock
from functools import partial
import threading
import tensorflow as tf
import numpy as np
import time
import cv2

from modules.dbactions import connectToDatabase, closeDatabaseConnection
from PoseModule.yolov7.detect import detect as PoseDetect
from PoseModule.yolov7.utils.datasets import LoadImages
from alarms.alarms import Alarms
from modules import global_vars

alarms = Alarms()


class CamerasScreen(Screen):
    def __init__(self, **kwargs):
        super(CamerasScreen, self).__init__(**kwargs)

    def on_pre_enter(self):
        if not global_vars.already_loaded_cameras:
            global_vars.already_loaded_cameras = True
            global_vars.cameras_layout.load_cameras()
        


class CameraView(Image):
    cameraID = NumericProperty()

    def __init__(self, last_alarm=0, **kwargs):
        super(CameraView, self).__init__(**kwargs)
        self.last_alarm = last_alarm


class CamerasLayout(StackLayout):
    def __init__(self, **kwargs):
        super(CamerasLayout, self).__init__(**kwargs)
        global_vars.cameras_layout = self

    def load_cameras(self):

        db, cursor = connectToDatabase()
        cursor.execute("SELECT generated_id FROM cameras WHERE workspace_id=%s", (global_vars.choosenWorkplace,))
        results = cursor.fetchall()
        
        self.clear_widgets()

        for row in results:
            rlayout = RLayout(cameraID=row[0])
            rlayout.cameraID = row[0]
            rlayout.source = 'img/test.png'
            self.add_widget(rlayout)
        closeDatabaseConnection(db, cursor)


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
mask_model = load_model('models/mask_binar_classifier.h5')
helmet_model = load_model('models/helmet_binar_classifier.h5')
vest_model = load_model('models/vest_binar_classifier.h5')
cap_model = load_model('models/cap_binar_classifier.h5')
failed_load_camera_img = 'img/no_camera.jpg'

iteration_started = False


class RLayout(RelativeLayout):
    camera_view_parent = ObjectProperty()
    cameraID = NumericProperty()


    def __init__(self, **kwargs):
        super(RLayout, self).__init__(**kwargs)
        global cam_view
        camera = CameraView(cameraID=self.cameraID)
        self.camera_view_parent.add_widget(camera)
        cam_view.append(camera)

        self.rules_list = ''
        self.action_list = ''
        self.notification_enabled = True
        self.AI_enabled = True
        self.load_data_from_database()

        global iteration_started
        if not iteration_started:
            timer = threading.Timer(0, self.set_interval)
            timer.setDaemon(True)
            timer.start()
            threading.Timer(2.0, self.print_test).start()
            # threading.Thread(target=self.iterate_images).start()
            iteration_started = True

    def print_test(self):
        print('test')

    def load_data_from_database(self):
        db, cursor = connectToDatabase()
        cursor.execute(
            f"SELECT state_activation FROM workplaces WHERE id = {global_vars.choosenWorkplace}")
        self.AI_enabled = cursor.fetchall()[0][0]
        cursor.execute(
                    f"SELECT rules FROM cameras WHERE workspace_id = {global_vars.choosenWorkplace}")
        self.rules_list = cursor.fetchall()
        print(self.rules_list)
        cursor.execute(
            f"SELECT actions FROM cameras WHERE workspace_id = {global_vars.choosenWorkplace}")
        self.action_list = cursor.fetchall()
        cursor.execute(
            f"SELECT state_notifications FROM workplaces WHERE id = {global_vars.choosenWorkplace}")
        self.notification_enabled = cursor.fetchall()[0][0]
        closeDatabaseConnection(db, cursor)

    
    def set_interval(self):
        #Clock.schedule_interval(RLayout.iterate_images, 5)
        while True:
            self.iterate_images()
            
    def ai_singe_camera_prediction(self, object_name, object_lists, model, nr0, cam_view, alignment, equation, reverse):
        print(time.time())
        if alignment is None:
            is_danger = RLayout.do_predictions(
                object_lists, object_name, nr0, model
            )
        elif equation is None:
            is_danger = RLayout.do_predictions(
                object_lists, object_name, nr0, model, alignment=alignment
            )
        else:
            is_danger = RLayout.do_predictions(
                object_lists, object_name, nr0, model, equation, alignment=alignment, reverse=reverse)

        if is_danger:
            RLayout.do_alert(
                self.action_list, object_name, nr0)
            alert_color = [1, 1, 0, 1]
            cam_id = cam_view[0].cameraID
            for cam_layout in global_vars.cameras_layout.children:
                if cam_layout.cameraID == cam_id:
                    cam_layout.ids.alert_indicator.alert_color = alert_color
        else:
            cam_id = cam_view[0].cameraID
            for cam_layout in global_vars.cameras_layout.children:
                if cam_layout.cameraID == cam_id:
                    cam_layout.ids.alert_indicator.alert_color = [0, 1, 0, 1]

    def ai_single_camera_prediction_fall(self, diff_x_lists, diff_y_lists, diff_z_lists, diff_x, diff_y, diff_z, cam_view, nr0):
        fall = False
        diff_x_list = diff_x_lists[nr0]
        diff_y_list = diff_y_lists[nr0]
        diff_z_list = diff_z_lists[nr0]
        for diff_x in diff_x_list:
            if diff_x > 80:
                fall = True
        for diff_y in diff_y_list:
            if diff_y > 0:
                fall = True
        for diff_z in diff_z_list:
            if 0.2 < diff_z < 0.4:
                fall = True
        if fall:
            cam_id = cam_view[nr0].cameraID
            action = str(self.action_list[nr0][0])
            if "2" in action:
                action = 2
            elif "1" in action:
                action = 1
            else:
                action = 3
            db, cursor = connectToDatabase()
            cursor.execute("INSERT INTO logs VALUES (null, %s, %s, %s, %s, now(), 0)",
                           (global_vars.choosenWorkplace, cam_id, "Fall",
                            global_vars.actions_dict[int(action)]))
            db.commit()
            closeDatabaseConnection(db, cursor)
            print(
                f"On camera of id: {cam_id} detect FALL!!!")
            # alarms.flash_alarm_on(2)
            # alarms.start_buzzer()
            alert_color = [1, 0, 0, 1]
            cam_id = cam_view[0].cameraID
            for cam_layout in global_vars.cameras_layout.children:
                if cam_layout.cameraID == cam_id:
                    cam_layout.ids.alert_indicator.alert_color = alert_color
        else:
            cam_id = cam_view[0].cameraID
            for cam_layout in global_vars.cameras_layout.children:
                if cam_layout.cameraID == cam_id:
                    cam_layout.ids.alert_indicator.alert_color = [0, 1, 0, 1]

    
    def iterate_images(self):
        global cam_nr

        if self.AI_enabled:
            img_list, mask_lists, helmet_cap_lists, vest_lists, img0_list = [], [], [], [], []
            diff_x_lists, diff_y_lists, diff_z_lists = [], [], []
            if global_vars.AI_run:
                for dataset in datasets:
                    try:
                        img, mask_list, helmet_cap_list, vest_list, img0, diff_x, diff_y, diff_z = p_detect.detect2(
                            dataset)
                        img_list.append(img)
                        mask_lists.append(mask_list)
                        helmet_cap_lists.append(helmet_cap_list)
                        vest_lists.append(vest_list)
                        img0_list.append(img0)
                        diff_x_lists.append(diff_x)
                        diff_y_lists.append(diff_y)
                        diff_z_lists.append(diff_z)
                    except Exception as err:
                        print("Failed to load camera or video is over", err)

                

                if self.notification_enabled:
                    cam_id = None
                    for nr0, img in enumerate(img_list):
                        if nr0 + 1 <= len(cam_view):
                            if abs(cam_view[nr0].last_alarm - time.time()) > 10:
                                cam_view[nr0].last_alarm = time.time()
                                alert_color = [0, 1, 0, 1]
                                if "1" in self.rules_list[nr0][0]:
                                    threading.Thread(target=self.ai_singe_camera_prediction, args=("mask", mask_lists, mask_model, nr0, cam_view)).start()
                                if "2" in self.rules_list[nr0][0]:
                                    threading.Thread(target=self.ai_singe_camera_prediction, args=("helmet", helmet_cap_lists, helmet_model, nr0, cam_view)).start()
                                # if helmets detecting do not detect caps
                                elif "3" in self.rules_list[nr0][0]:
                                    threading.Thread(target=self.ai_singe_camera_prediction, args=("cap", helmet_cap_lists, cap_model, nr0, cam_view, 0.2)).start()
                                if "4" in self.rules_list[nr0][0]:
                                    threading.Thread(target=self.ai_singe_camera_prediction, args=("vest", vest_lists, vest_model, nr0, cam_view, 0.5, 10 ** 15, True)).start()
                                if "7" in self.rules_list[nr0][0]:
                                    threading.Thread(target=self.ai_single_camera_prediction_fall, args=(diff_x_lists, diff_y_lists, diff_z_lists, diff_x, diff_y, diff_z, cam_view, nr0))
                                   
                print("BEFORE")
                for nr, camera_image in enumerate(cam_view):
                    self.send_data_to_camera_view(camera_image, img_list, nr, datasets)
                    cam_nr = 0
        else:
            for camera_image in cam_view:
                Clock.schedule_once(lambda dt: self.set_image_source(camera_image, failed_load_camera_img))

    
    def send_data_to_camera_view(self, camera_image, img_list, nr, datasets):
        global cam_nr
        if cam_nr < len(datasets):
            cam_nr += 1
            if isinstance(datasets[nr], LoadImages):
                try:
                    if img_list[nr].any():
                        print(camera_image)
                        img = img_list[nr]
                        Clock.schedule_once(lambda dt: self.set_image_texture(camera_image, img))
                    else:
                        Clock.schedule_once(lambda dt: self.set_image_source(camera_image, failed_load_camera_img))
                except:
                    Clock.schedule_once(lambda dt: self.set_image_source(camera_image, failed_load_camera_img))
            else:
                try:
                    if img_list[nr].any():
                        img = img_list[nr]
                        img = np.array(img)
                        img = np.rot90(img, 2)
                        Clock.schedule_once(lambda dt: self.set_image_texture(camera_image, img,))
                    else:
                        Clock.schedule_once(lambda dt: self.set_image_source(camera_image, failed_load_camera_img))
                except:
                    Clock.schedule_once(lambda dt: self.set_image_source(camera_image, failed_load_camera_img))
        else:
            Clock.schedule_once(lambda dt: self.set_image_source(camera_image, failed_load_camera_img))



    def set_image_texture(self, camera_image, img):
        print("AFTER: ", camera_image)
        buffer = cv2.flip(img, 0).tobytes()
        texture = Texture.create(
            size=(img.shape[1], img.shape[0]), colorfmt='bgr')
        texture.blit_buffer(
            buffer, colorfmt='bgr', bufferfmt='ubyte')
        
        camera_image.texture = texture
        # camera_image.canvas.ask_update()

    
    def set_image_source(self, camera_image, source):
        camera_image.source = source
        # camera_image.canvas.ask_update()


    @staticmethod
    def do_predictions(object_lists, object_name, nr0, model, equation=1, alignment=0, reverse=False):
        danger = False
        if object_lists != empty:
            try:
                entire_img = object_lists[nr0]
                if entire_img != empty:
                    for crop_image in entire_img:
                        resize = tf.image.resize(crop_image, (256, 256))
                        pred = model.predict(np.expand_dims(resize / 255, 0))
                        if pred < ((0.5 + alignment) * equation):
                            # print(f'Predicted class is {object_name}')
                            pass
                        else:
                            # print(f'Predicted class is No {object_name}')
                            danger = True
            except Exception as err:
                print(f"Failed to load {object_name} image --- {err}")
        if reverse:
            danger = not danger
        return danger

    @staticmethod
    def do_alert(action_list, object_name, nr0):
        cam_id = cam_view[nr0].cameraID
        action = str(action_list[nr0][0])
        if "2" in action:
            action = 2
            # alarms.flash_alarm_on(2)
            # alarms.start_buzzer()
        elif "1" in action:
            action = 1
            # alarms.flash_alarm_on(1)
        else:
            action = 3
        print(
            f"On camera of id: {cam_id} detect no {object_name}, action {action}!!!")
        db, cursor = connectToDatabase()
        reason = "No " + object_name
        cursor.execute("INSERT INTO logs VALUES (null, %s, %s, %s, %s, now(), 0)",
                       (global_vars.choosenWorkplace, cam_id, reason, global_vars.actions_dict[int(action)]))
        db.commit()
        closeDatabaseConnection(db, cursor)
        print(f"On camera of id: {cam_id} detect no {object_name}!!!")


class PopupContent(BoxLayout):
    generatedID = NumericProperty()

    def __init__(self, **kwargs):
        super(PopupContent, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.add_widget(Label(text=("Camera ID: " + str(self.generatedID))))
        self.add_widget(Label(text=("Camera name: " + global_vars.cameras_dict[self.generatedID])))


class InfoButton(Button):
    def __init__(self, **kwargs):
        super(InfoButton, self).__init__(**kwargs)

    def on_press(self):
        generatedID = self.parent.parent.parent.parent.parent.cameraID
        content = PopupContent(generatedID=generatedID)
        popup = Popup(title='Info about camera', content=content,
                      auto_dismiss=True, size_hint=[None, None], size=[500, 300])
        popup.open()


