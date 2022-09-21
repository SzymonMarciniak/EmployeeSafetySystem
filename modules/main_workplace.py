from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.uix.button import Button
from kivy.uix.screenmanager import FadeTransition


class MenuButtonActive(Button):
    main_screen_sm = ObjectProperty()

    def on_press(self):
        self.main_screen_sm.transition = FadeTransition()
        self.main_screen_sm.current = "SetupScreen"
