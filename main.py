from kivy.app import App 
import math
from kivy.metrics import dp
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, BooleanProperty, ListProperty
from kivy.graphics.vertex_instructions import Line, Rectangle, Ellipse
from kivy.graphics.context_instructions import Color


class MainWindow(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.x1, self.x2, self.y1, self.y2 = 10,100,50,200
        self.chose = "None"
        with self.canvas:
            Color(200/255,200/255,200/255)
            self.main_room = Line(width=1.5)

        self.points = []
        self.end_points = []
    
    def create_room_activate(self):
        self.chose = "new_room"
    
    def create_room_function(self):
        x1, y1 = self.points[0]

        if self.end_points:
            x2, y2 = self.end_points
        else:
            x2, y2 = x1, y1


        #self.main_room.points = dp(cx1)*self.width, dp(cy2)*self.width, dp(cx1)*self.width, dp(cy1)*self.width, dp(cx2)*self.width, dp(cy1)*self.width, dp(cx2)*self.width, dp(cy2)*self.width, dp(cx1)*self.width, dp(cy2)*self.width
        self.main_room.points = x1,y2,x1,y1,x2,y1,x2,y2,x1,y2 
        print(f"Distance: x:{int(math.sqrt((x2-x1)**2)/10)}m y:{int(math.sqrt((y2-y1)**2)/10)}m")
    
    def create_door_activate(self):
        self.chose = "create_door"

        
    

    
    def on_touch_down(self, touch):
        
        if super(MainWindow, self).on_touch_down(touch): #If clicking not in create room zone 
            return False

        if self.chose == "new_room":
            touch.grab(self)
            self.points = []
            self.points.append(touch.pos)
            self.create_room_function()
            return True
        else:print("pass ")

    
    def on_touch_move(self, touch):
        if self.chose == "new_room":
            if touch.grab_current is self:
                self.end_points = touch.pos
                self.create_room_function()
                return True
        return super(MainWindow, self).on_touch_move(touch)

        





class EmployeeSystemApp(App):
    pass

EmployeeSystemApp().run()






















