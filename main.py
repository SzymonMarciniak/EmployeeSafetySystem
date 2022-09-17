from kivy import Config
from kivy.app import App
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.garden.iconfonts import iconfonts
from kivy.lang import Builder
from kivy.properties import OptionProperty

from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.stacklayout import StackLayout

# SECTION FOR MODULES IMPORT, CONTAIN PARTS OF APP
from modules import dbactions
from modules import auth_view_logics
from modules import globals
from modules import recovery_email
from modules import workplace_chooser
from modules import new_workplace


class ScreenManagement(ScreenManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class MainScreen(StackLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for i in range(50):
            box = Button(size_hint=[.5, .2], text="Work in progress")
            self.add_widget(box)


class EmployeeSafetySystemApp(App):
    size = OptionProperty('S', options=['S', 'L', 'XL'])

    def __init__(self, **kwargs):
        super(EmployeeSafetySystemApp, self).__init__(**kwargs)
        Window.bind(mouse_pos=self.on_mouse_pos)
        Window.size = (400, 750)
        self.width, self.height = Window.size
        self.size = (
            'S' if self.width < 1050 else
            'L'
        )
        Window.bind(size=self.update_layout)
        LabelBase.register(name='Lato',
                           fn_regular='fonts/Lato-Regular.ttf',
                           fn_bold='fonts/Lato-Bold.ttf')
        iconfonts.register("default_font", 'fonts/Material-Design-Iconic-Font.ttf', 'fonts/zmd.fontd')
        Config.set('kivy', 'default_font', 'Lato')
        db, cursor = dbactions.connectToDatabase(True)
        db.close()

    def update_layout(self, win, size):
        width, height = size
        self.width = width
        self.height = height
        App.get_running_app().root.get_screen("choose_workplace_screen").ids.test_label.f_width = width
        App.get_running_app().root.get_screen("choose_workplace_screen").ids.test_label.f_height = height
        self.size = (
            'S' if width < 1050 else
            'L'
        )

    def build(self):
        Builder.load_file("main.kv")
        return ScreenManagement()

    def on_mouse_pos(self, window, pos):
        """
        Tracks mouse position on the screen and changes cursor accordingly to desired value while hovering specific
        objects
        """
        changed = False
        for hoverObj in globals.hoverEventObjects:
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
