from kivy.animation import Animation
from kivy.app import App
from kivy.properties import StringProperty, ObjectProperty, ColorProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.screenmanager import FadeTransition
from kivy.uix.textinput import TextInput

from modules.checkers import checkDataCorrectness


class LoginScreenLayout(BoxLayout):
    def __init__(self, **kwargs):
        super(LoginScreenLayout, self).__init__(**kwargs)


class RegisterScreenLayout(BoxLayout):
    def __init__(self, **kwargs):
        super(RegisterScreenLayout, self).__init__(**kwargs)


class SimpleInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class LoginButton(Button):
    rectColor = StringProperty('')
    loginBox = ObjectProperty()
    passwordBox = ObjectProperty()
    errorBox = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ids.rectColor = self.color
        self.rectColor = "#0fafff"

    def on_pressed(self):
        self.rectColor = "#0f87ff"
        checkDataCorrectness(self.loginBox.text, self.passwordBox.text, self.errorBox)

    def on_released(self):
        self.rectColor = "#0fafff"


class RegisterButton(Button):
    rectColor = StringProperty('')
    loginBox = ObjectProperty()
    newPasswordBox = ObjectProperty()
    repeatPasswordBox = ObjectProperty()
    nameBox = ObjectProperty()
    errorBox = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ids.rectColor = self.color
        self.rectColor = "#0fafff"

    def on_pressed(self):
        self.rectColor = "#0f87ff"
        checkDataCorrectness(self.loginBox.text, self.newPasswordBox.text, self.errorBox, self.repeatPasswordBox.text,
                             self.nameBox.text)

    def on_released(self):
        self.rectColor = "#0fafff"


class ResetPasswordButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_press(self):
        App.get_running_app().root.transition = FadeTransition()
        App.get_running_app().root.current = 'forgot_password_screen'


class SwitchRegisterButton(Button):
    transitionColor = ColorProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_press(self):
        self.color = [0, 0, 0, .7]

    def on_release(self):
        self.color = "#0fafff"
