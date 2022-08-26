from kivy.animation import Animation
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import StringProperty, ObjectProperty, ColorProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.screenmanager import FadeTransition, Screen
from kivy.uix.textinput import TextInput
import win32api, win32con

from modules.checkers import checkDataCorrectness
from modules import globals


class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    loginBox = ObjectProperty()
    passwordBox = ObjectProperty()
    registerBtn = ObjectProperty()
    loginBtn = ObjectProperty()
    resetPswdBtn = ObjectProperty()

    def on_pre_enter(self):
        Clock.schedule_once(self.callback)
        # It is necessary to call function one frame later.
        # Calling it right away is causing an error because
        # the IDs are not yet initalized

    def callback(self, dt):
        globals.hoverEventObjects = [self.loginBox, self.passwordBox, self.loginBtn,
                                     self.registerBtn, self.resetPswdBtn]


class RegisterScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    newLoginBox = ObjectProperty()
    newPasswordBox = ObjectProperty()
    repeatPasswordBox = ObjectProperty()
    nameBox = ObjectProperty()
    registerBtn = ObjectProperty()
    loginBtn = ObjectProperty()
    resetPswdBtn = ObjectProperty()

    def on_pre_enter(self):
        Clock.schedule_once(self.callback)

    def callback(self, dt):
        globals.hoverEventObjects = [self.registerBtn, self.loginBtn, self.resetPswdBtn]


class LoginScreenLayout(BoxLayout):
    def __init__(self, **kwargs):
        super(LoginScreenLayout, self).__init__(**kwargs)


class RegisterScreenLayout(BoxLayout):
    def __init__(self, **kwargs):
        super(RegisterScreenLayout, self).__init__(**kwargs)


class SimpleInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    activated = False

    def on_entered(self):
        caps_status = win32api.GetKeyState(win32con.VK_CAPITAL)
        if caps_status == 0 and self.activated:
            current_app = App.get_running_app()
            current_app.root.ids.capsLockLabel.text = ''
            current_app.root.get_screen('register_screen').ids.capsLockLabel_newPasswordBox.text = ''
            current_app.root.get_screen('register_screen').ids.capsLockLabel_repeatPasswordBox.text = ''
            self.activated = False
            print(0)
        elif caps_status == 1 and not self.activated:
            current_app = App.get_running_app()
            current_app.root.ids.capsLockLabel.text = 'Caps ON'
            current_app.root.get_screen('register_screen').ids.capsLockLabel_newPasswordBox.text = 'Caps ON'
            current_app.root.get_screen('register_screen').ids.capsLockLabel_repeatPasswordBox.text = 'Caps ON'
            self.activated = True
            print(1)


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


class ChangeLanguage(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.english = True

    def on_press(self):
        if self.english:
            self.background_down = 'img/pl.png'
            self.background_normal = 'img/pl.png'
            self.english = False
        else:
            self.background_down = 'img/gb.png'
            self.background_normal = 'img/gb.png'
            self.english = True
