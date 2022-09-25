from kivy.animation import Animation
from kivy.clock import Clock
from kivy.properties import ObjectProperty, NumericProperty
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import FadeTransition

choices = {
    1: 'cameras_screen',
    2: 'dev',
    3: 'dev',
    4: 'rules_screen',
    5: 'SetupScreen',
    6: 'dev'
}


class CamerasGrid(GridLayout):

    def __init__(self, **kwargs):
        super(CamerasGrid, self).__init__(**kwargs)


class MenuButton(Button):
    main_screen_sm = ObjectProperty()
    # canva_s1 = NumericProperty()
    # canva_s2 = NumericProperty()
    active = False
    sID = NumericProperty()

    def on_press(self):
        anim = Animation(canva_s1=1, duration=.3, transition='in_out_quad')
        anim.start(self)
        for children in self.parent.children:
            if children == self:
                continue
            if children.active is True:
                anim = Animation(canva_s1=0, duration=.3, transition='in_out_quad')
                anim.start(children)
        self.active = True
        if self.sID != 7:
            self.main_screen_sm.transition = FadeTransition()
            self.main_screen_sm.current = choices.get(self.sID)
