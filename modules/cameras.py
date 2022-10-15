from kivy.properties import ObjectProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.stacklayout import StackLayout

from modules.dbactions import connectToDatabase, closeDatabaseConnection


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


class RLayout(RelativeLayout):
    camera_view_parent = ObjectProperty()
    cameraID = NumericProperty()

    def __init__(self, **kwargs):
        super(RLayout, self).__init__(**kwargs)
        camera = CameraView(cameraID=self.cameraID)
        self.camera_view_parent.add_widget(camera)
        self.iterate_images()

    def iterate_images(self):
        for camera_image in self.camera_view_parent.children:
            camera_image.source = 'img/test.png'


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
