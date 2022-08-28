from kivy.animation import Animation
from kivy.app import App
from kivy.clock import Clock
from kivy.garden.iconfonts import icon
from kivy.properties import StringProperty, ObjectProperty, NumericProperty
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import FadeTransition, Screen
from kivy.uix.textinput import TextInput
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


class BottomLayout(BoxLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.codeInputs = None
        self.orientation = 'horizontal'
        self.spacing = .1 * self.width

    def initialize_code_inputs(self):
        showAnim = Animation(opacity=1, duration=1.0)
        codeInputs = []
        self.clear_widgets()
        for i in range(6):
            codeInputs.append(TextInput(opacity=1, multiline=False, write_tab=False))
            if i == 0:
                codeInputs[i].focus = True
            self.add_widget(codeInputs[i])
        codeInputs[0].bind(text=lambda instance, value: self.on_text_typed(instance, value, 0, codeInputs))
        codeInputs[1].bind(text=lambda instance, value: self.on_text_typed(instance, value, 1, codeInputs))
        codeInputs[2].bind(text=lambda instance, value: self.on_text_typed(instance, value, 2, codeInputs))
        codeInputs[3].bind(text=lambda instance, value: self.on_text_typed(instance, value, 3, codeInputs))
        codeInputs[4].bind(text=lambda instance, value: self.on_text_typed(instance, value, 4, codeInputs))
        codeInputs[5].bind(text=lambda instance, value: self.on_text_typed(instance, value, 5, codeInputs))

    def on_text_typed(self, instance, value, num, codeInputs):
        if len(codeInputs[num].text) > 1:
            codeInputs[num].text = value[-1]
        if int(value)
        if num != len(codeInputs) - 1:
            codeInputs[num+1].focus = True
        else:
            codeInputs[num].focus = False


class SendEmailButton(Button):
    rectColor = StringProperty('')
    recoveryEmailBox = ObjectProperty()
    infoLabel = ObjectProperty()
    bottomLayout = ObjectProperty()
    a = NumericProperty(5)

    # b = NumericProperty(5)
    # firstCycle = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ids.rectColor = self.color
        self.rectColor = "#0fafff"

    def set_info_label(self):
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
                self.bottomLayout.initialize_code_inputs()

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
