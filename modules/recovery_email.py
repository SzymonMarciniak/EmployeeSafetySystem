import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from random import randint

from kivy.animation import Animation
from kivy.app import App
from kivy.clock import Clock
from kivy.garden.iconfonts import icon
from kivy.metrics import sp
from kivy.properties import StringProperty, ObjectProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import FadeTransition, Screen
from kivy.uix.textinput import TextInput
from kivy.utils import rgba

from modules import globals
from modules.dbactions import connectToDatabase, closeDatabaseConnection, checkIsEmailInDatabase

clientID = None


class ForgotPasswordScreen(Screen):
    recoveryEmailBox = ObjectProperty()
    sendRecoveryEmailButton = ObjectProperty()
    backToLoginBtn = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_pre_enter(self):
        globals.hoverEventObjects = [self.recoveryEmailBox, self.sendRecoveryEmailButton, self.backToLoginBtn]


def sendRecoveryEmail(userMail):
    print("SENT")
    systemMail = "employeesafetysystem@ess.com"

    db, cursor = connectToDatabase()
    cursor.execute("SELECT id, name FROM accounts WHERE login=%s", (userMail,))
    results = cursor.fetchone()
    userID = results[0]
    fullName = results[1]
    generatedCode = ''.join(str(randint(0, 9)) for n in range(6))

    cursor.execute("SELECT id FROM pswdresets WHERE expDate > UNIX_TIMESTAMP() AND userID=%s AND used=0", (userID,))
    results = cursor.fetchone()
    if results is None:
        cursor.execute("INSERT INTO pswdresets VALUES(null, %s, %s, UNIX_TIMESTAMP(), UNIX_TIMESTAMP() + %s, 0)",
                       (userID, generatedCode, 300))
        db.commit()
    else:
        cursor.execute("UPDATE pswdresets SET initDate=UNIX_TIMESTAMP(), expDate=UNIX_TIMESTAMP() + %s, code=%s WHERE "
                       "userID=%s AND used=0",
                       (300, generatedCode, userID))
        db.commit()
    closeDatabaseConnection(db, cursor)

    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Password recovery | EmployeeSafetySystem"
    msg['From'] = systemMail
    msg['To'] = userMail

    text = "Employee Safety System\n\nHello, %s!\nWe received password reset request for your account\nIf you want to" \
           "proceed, please input following code on the screen: %s \nNot your request? " \
           "Ignore this message" % (fullName.split()[0], ' '.join(generatedCode))
    html = """
    <html>
        <head></head>
        <body>
            <h1 style="text-align: center">Employee Safety System</h1>
            <h1 style="text-align: center">Hello, %s!</h1>
            <p style="text-align: center">We received password reset request for your account<br>
                                          If you want to proceed, please input following code in the app:</p>
            <h3 style="text-align: center">%s</h3>
            <p style="text-align: center">Not your request? Ignore this message</p>
        </body>
    </html>                           
    """ % (fullName.split()[0], ' '.join(generatedCode))

    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')
    msg.attach(part1)
    msg.attach(part2)
    smtp = smtplib.SMTP('localhost')
    smtp.sendmail(systemMail, userMail, msg.as_string())
    global clientID
    clientID = userID


class InfoLabel(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class CodeInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.pos_hint = {'center_x': 0.5, 'center_y': 0.5}


class SubmitCodeButton(Button):
    def __init__(self, **kwargs):
        super(SubmitCodeButton, self).__init__(**kwargs)
        self.markup = True
        self.font_size = 32
        self.background_color = rgba('#ececec')
        self.text = "%s" % icon('zmdi-chevron-right')
        self.size_hint_x = 1.5

    def on_press(self):
        print("CODE VALIDATION")
        db, cursor = connectToDatabase()
        code = ''
        global clientID
        for i, child in enumerate(self.parent.children):
            if i == 0:
                continue
            code += child.text
        cursor.execute("SELECT id FROM pswdresets WHERE userid=%s AND code=%s AND expDate > UNIX_TIMESTAMP()"
                       "AND used=0", (clientID, code[::-1]))
        results = cursor.fetchone()
        if results is None:
            self.parent.parent.parent.infoLabel.text = "[size=24]%s[/size] Provided code is invalid. " \
                                                           "Recheck your input" % icon('zmdi-alert-circle')
            self.parent.parent.parent.infoLabel.color = rgba("c92a1e")
        else:
            cursor.execute("UPDATE pswdresets SET used=1 WHERE userid=%s AND code=%s AND expDate > UNIX_TIMESTAMP()"
                           "AND used=0", (clientID, code[::-1]))
            db.commit()
            self.parent.parent.parent.infoLabel.text = "[size=24]%s[/size] Code valid, redirecting..."\
                                                       % icon('zmdi-check-circle')
            self.parent.parent.parent.infoLabel.color = rgba("08c48c")
            App.get_running_app().root.transition = FadeTransition()
            App.get_running_app().root.current = 'new_password_screen'
        closeDatabaseConnection(db, cursor)


class BottomLayout(BoxLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.codeInputs = None
        self.orientation = 'horizontal'
        self.spacing = .1 * self.width
        self.alreadyChanged = False

    def initialize_code_inputs(self):
        self.padding = -1 * .05 * self.width, 0
        showAnim = Animation(opacity=1, duration=1.0)
        codeInputs = []
        self.clear_widgets()
        for i in range(6):
            inputC = CodeInput(opacity=1, multiline=False, write_tab=False)
            inputC.input_filter = 'int'
            inputC.cursor_color = [1, 1, 1, 0]
            inputC.cursor_blink = False
            inputC.halign = 'center'
            codeInputs.append(inputC)
            if i == 0:
                inputC.focus = True
            inputC.font_name = 'Lato'
            inputC.font_size = sp(32)
            self.add_widget(inputC)
        submitBtn = SubmitCodeButton()
        self.add_widget(submitBtn)
        codeInputs[0].bind(text=lambda instance, value: self.on_text_typed(instance, value, 0, codeInputs))
        codeInputs[1].bind(text=lambda instance, value: self.on_text_typed(instance, value, 1, codeInputs))
        codeInputs[2].bind(text=lambda instance, value: self.on_text_typed(instance, value, 2, codeInputs))
        codeInputs[3].bind(text=lambda instance, value: self.on_text_typed(instance, value, 3, codeInputs))
        codeInputs[4].bind(text=lambda instance, value: self.on_text_typed(instance, value, 4, codeInputs))
        codeInputs[5].bind(text=lambda instance, value: self.on_text_typed(instance, value, 5, codeInputs))

    def on_text_typed(self, instance, value, num, codeInputs):
        if len(instance.text) < 1:
            instance.text = value
        else:
            instance.text = value[-1]
        if num != len(codeInputs) - 1:
            codeInputs[num + 1].focus = True
        else:
            instance.focus = False


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
            # sendRecoveryEmail(self.recoveryEmailBox.text)
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

            globals.hoverEventObjects.pop(1)
            Clock.schedule_once(lambda dt: rmAnim.start(self))
            sendRecoveryEmail(self.recoveryEmailBox.text)

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
