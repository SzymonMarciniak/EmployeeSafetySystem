from kivy.app import App
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.garden.iconfonts import iconfonts

# SECTION FOR MODULES IMPORT, CONTAIN PARTS OF APP
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.stacklayout import StackLayout

from modules import dbactions
from modules import auth_view_logics

hoverEventObjects = None


class ScreenManagement(ScreenManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    # def on_enter(self, *args):
    #     global hoverEventObjects
    #     hoverEventObjects = [self.ids.loginBox, self.ids.passwordBox, self.ids.loginBtn,
    #                          self.ids.registerBtn] self
    #     print(hoverEventObjects)


class MainScreen(StackLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for i in range(50):
            box = Button(size_hint=[.5, .2], text="Work in progress")
            self.add_widget(box)


class EmployeeSafetySystemApp(App):
    def __init__(self, **kwargs):
        super(EmployeeSafetySystemApp, self).__init__(**kwargs)
        Window.bind(mouse_pos=self.on_mouse_pos)
        LabelBase.register(name='Lato',
                           fn_regular='fonts/Lato-Regular.ttf',
                           fn_bold='fonts/Lato-Bold.ttf')
        iconfonts.register("default_font", 'fonts/Material-Design-Iconic-Font.ttf', 'fonts/zmd.fontd')
        db, cursor = dbactions.connectToDatabase(True)
        db.close()

    def build(self):
        Window.size = (400, 750)
        return ScreenManagement()

    def on_mouse_pos(self, window, pos):
        """
        Tracks mouse position on the screen and changes cursor accordingly to desired value while hovering specific
        objects
        """
        global hoverEventObjects
        hoverEventObjects = [self.root.ids.loginBox, self.root.ids.passwordBox, self.root.ids.loginBtn,
                             self.root.ids.registerBtn]
        changed = False
        for hoverObj in hoverEventObjects:
            if hoverObj.collide_point(*pos):
                changed = True
                Window.set_system_cursor('hand')
            else:
                if changed:
                    return
                Window.set_system_cursor('arrow')
        changed = False


if __name__ == "__main__":
    EmployeeSafetySystemApp().run()
