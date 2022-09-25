import binhex

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.video import Video
from kivy.uix.videoplayer import VideoPlayer


class CameraView(BoxLayout):
    def __init__(self, **kwargs):
        super(CameraView, self).__init__(**kwargs)
        video = VideoPlayer(source="videos/test.mp4")
        video.options = {'eos': 'loop'}
        self.add_widget(video)


class PopupContent(BoxLayout):
    def __init__(self, **kwargs):
        super(PopupContent, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.add_widget(Label(text="ID: 7"))
        self.add_widget(Label(text="Room ID: 3"))
        self.add_widget(Label(text="Rules: 4"))


class InfoButton(Button):
    def __init__(self, **kwargs):
        super(InfoButton, self).__init__(**kwargs)

    def on_press(self):
        content = PopupContent()
        popup = Popup(title='Info about camera', content=content, auto_dismiss=True, size_hint=[.7, .7])
        popup.open()
