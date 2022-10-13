from kivy.animation import Animation
from kivy.app import App
from kivy.clock import Clock
from kivy.properties import ObjectProperty, NumericProperty, StringProperty
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import FadeTransition, Screen

from modules.dbactions import connectToDatabase, closeDatabaseConnection
from modules import global_vars
from modules.cameras import CamerasLayout

choices = {
    1: 'cameras_screen',
    2: 'alerts_screen',
    3: 'dev',
    4: 'rules_screen',
    5: 'SetupScreen',
    6: 'dev',
    7: 'login_screen'
}


class MainWorkplaceScreen(Screen):
    upper_menu = ObjectProperty()
    bottom_menu = ObjectProperty()
    hello_text = StringProperty()

    def __init__(self, **kwargs):
        super(MainWorkplaceScreen, self).__init__(**kwargs)
        userName = global_vars.userID
        self.hello_text = f"Hello {userName}"

    def on_pre_enter(self):
        global_vars.hoverEventObjects = []
        for children in self.upper_menu.children:
            global_vars.hoverEventObjects.append(children)
        for children in self.bottom_menu.children:
            global_vars.hoverEventObjects.append(children)

        userid = global_vars.userID
        db, cursor = connectToDatabase()
        cursor.execute("SELECT name FROM accounts WHERE id=%s", (userid,))
        userData = cursor.fetchone()
        closeDatabaseConnection(db, cursor)

        userName = ""
        for l in userData[0]:
            if l == " ":
                break 
            userName += l
        self.hello_text = f"Hello {userName}"


class CamerasGrid(GridLayout):

    def __init__(self, **kwargs):
        super(CamerasGrid, self).__init__(**kwargs)


class MenuButton(Button):
    main_screen_sm = ObjectProperty()
    bottom_menu = ObjectProperty()
    upper_menu = ObjectProperty()
    active = False
    sID = NumericProperty()

    def on_press(self):
        anim = Animation(canva_s1=1, duration=.3, transition='in_out_quad')
        anim.start(self)
        for children in self.upper_menu.children:
            if children == self:
                continue
            if children.active is True:
                anim = Animation(canva_s1=0, duration=.3, transition='in_out_quad')
                anim.start(children)
        for children in self.bottom_menu.children:
            if children == self:
                continue
            if children.active is True:
                anim = Animation(canva_s1=0, duration=.3, transition='in_out_quad')
                anim.start(children)
        self.active = True
        if self.sID == 7:
            global_vars.userID = None
            app = App.get_running_app()
            app.root.transition = FadeTransition()
            app.root.current = choices.get(self.sID)
            self.active = False
            return
        self.main_screen_sm.transition = FadeTransition()
        self.main_screen_sm.current = choices.get(self.sID)
