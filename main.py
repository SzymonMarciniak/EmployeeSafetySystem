from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.garden.iconfonts import register, iconfonts

from os.path import dirname, join

from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.utils import rgba

iconfonts.register("default_font", 'fonts/Material-Design-Iconic-Font.ttf', 'fonts/zmd.fontd')


class MainScreen(BoxLayout):
    pass


class SimpleInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class LoginButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_pressed(self):
        # rectColor = self.root.ids.rectColor
        # rectColor.rgba = rgba('#0a5bab')
        pass

    def on_released(self):
        # rectColor = self.root.ids.rectColor
        # rectColor.rgba = rgba('#0f87ff')
        pass


class EmployeeSafetySystemApp(App):
    def __init__(self, **kwargs):
        super(EmployeeSafetySystemApp, self).__init__()
        self.hoverEventObjects = None
        Window.bind(mouse_pos=self.on_mouse_pos)

    def build(self):
        Window.size = (400, 750)
        return MainScreen()

    def on_mouse_pos(self, window, pos):
        """
        Tracks mouse position on the screen and changes cursor accordingly to desired value while hovering specific
        objects
        """
        self.hoverEventObjects = [self.root.ids.loginBox, self.root.ids.passwordBox, self.root.ids.loginBtn,
                                  self.root.ids.registerBtn]
        changed = False
        for hoverObj in self.hoverEventObjects:
            if hoverObj.collide_point(*pos):
                changed = True
                Window.set_system_cursor('hand')
            else:
                if changed:
                    return
                Window.set_system_cursor('arrow')
        changed = False


EmployeeSafetySystemApp().run()
