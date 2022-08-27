import asyncio
import threading
import time

from kivy.animation import Animation
from kivy.app import App
from kivy.garden.iconfonts import icon
from kivy.properties import StringProperty, ObjectProperty, NumericProperty
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import FadeTransition, Screen
from kivy.utils import rgba

from modules import globals
from modules.dbactions import connectToDatabase, closeDatabaseConnection, checkIsEmailInDatabase


class ForgotPasswordScreen(Screen):
    recoveryEmailBox = ObjectProperty()
    sendRecoveryEmailButton = ObjectProperty()
    backToLoginBtn = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_pre_enter(self):
        globals.hoverEventObjects = [self.recoveryEmailBox, self.sendRecoveryEmailButton, self.backToLoginBtn]


def sendRecoveryEmail():
    print("SENT")


class InfoLabel(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class SendEmailButton(Button):
    rectColor = StringProperty('')
    recoveryEmailBox = ObjectProperty()
    infoLabel = ObjectProperty()
    a = NumericProperty(5)
    # b = NumericProperty(5)
    # firstCycle = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ids.rectColor = self.color
        self.rectColor = "#0fafff"

    def set_info_label(self):
        print("znów here hehe" + str(self.a))
        anim = Animation(a=0, duration=self.a)
        self.infoLabel.opacity = 1
        self.infoLabel.color = rgba("08c48c")

        def on_ref_pressed(smth, obj):
            print("RESEND MESSAGE")
            sendRecoveryEmail()
            self.set_info_label()

        def finish_callback(animation, clock):
            self.infoLabel.text = "[size=24]%s[/size] Recovery E-mail successfully sent! [ref=xd][u]Send again[" \
                                  "/ref][/u]" \
                                  % (icon('zmdi-check-circle'))
            self.infoLabel.bind(on_ref_press=on_ref_pressed)

        anim.bind(on_complete=finish_callback)
        anim.start(self)

    def on_pressed(self):
        self.rectColor = "#0f87ff"
        if checkIsEmailInDatabase(self.recoveryEmailBox.text):
            self.set_info_label()
            self.disabled = True
            self.disabled_color = self.color
            self.recoveryEmailBox.disabled = True
            rmAnim = Animation(opacity=0, duration=1.0)

            def actually_remove_widget(instance, obj):
                self.remove_widget(self)

            rmAnim.bind(on_complete=actually_remove_widget)
            rmAnim.start(self)
            globals.hoverEventObjects.pop(1)
            sendRecoveryEmail()

        else:
            self.infoLabel.opacity = 1
            self.infoLabel.color = rgba("c92a1e")
            self.infoLabel.text = "[size=24]%s[/size] E-Mail address not found! Make sure the address is correct" \
                                  % icon('zmdi-alert-circle')

    def on_a(self, instance, value):
        self.infoLabel.text = "[size=24]%s[/size] Recovery E-mail successfully sent! Send again (%ds)" \
                              % (icon('zmdi-check-circle'), round(value))

    def on_released(self):
        self.rectColor = "#0fafff"


class BackToLoginButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_press(self):
        self.color = [0, 0, 0, .7]

    def on_release(self):
        self.color = "#0fafff"
