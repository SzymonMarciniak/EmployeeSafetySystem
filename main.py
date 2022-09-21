from kivy.app import App 
import math
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics.vertex_instructions import Line
from kivy.graphics.context_instructions import Color

from utils import CenterOfLine

class SetupScreen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.chose = "None"
        with self.canvas:
            Color(200/255,200/255,200/255)
            self.main_room = Line(width=1.5)
            self.bind(size=self.rooms_refresh)
            Color(100/250,100/250,100/250)
            self.main_door = Line(width=8,cap="square")
            self.bind(size=self.doors_refresh)

        self.points = []
        self.end_points = []

        self.double = True
        self.rooms = 0

        self.rooms_points = []
        self.doors_points = []

        self.rooms_list = []
        self.door_list = []
    
    def create_room_activate(self):
        self.chose = "new_room"

    def rooms_refresh(self, *args):
        for id, line in enumerate(self.rooms_list):
            p = len(self.rooms_list) 
            if p != id:
                ckx1, cky1, ckx2, cky2 = self.rooms_points[id]
                x1, x2 = ckx1 * self.width, ckx2 * self.width
                y1, y2 = cky1 * self.height, cky2 * self.height
                line.points = x1,y2,x1,y1,x2,y1,x2,y2,x1,y2 
    
    def create_room_function(self, *args):
        self.kx1, self.ky1 = self.points
        self.x1 = self.width * self.kx1
        self.y1 = self.height * self.ky1

        if self.end_points:
            self.kx2, self.ky2 = self.end_points
            self.x2 = self.width * self.kx2
            self.y2 = self.height * self.ky2
        else:
            self.x2, self.y2 = self.x1, self.y1
        
        self.main_room.points = self.x1,self.y2,self.x1,self.y1,self.x2,self.y1,self.x2,self.y2,self.x1,self.y2 
        #center_x_top, center_y_top = CenterOfLine((self.kx2, self.kx1),(self.ky2,self.ky1), self.width, self.height)
        # center_x_left, center_y_left = CenterOfLine((self.kx1,self.ky2),(self.kx1,self.ky1), self.width, self.height)
        print(f"Distance: x:{float(math.sqrt((self.kx2-self.kx1)**2)/10) * 1000:.1f}m y:{float(math.sqrt((self.ky2-self.ky1)**2)/10) * 1000:.1f}m")
        #Label(text=f"{float(math.sqrt((self.kx2-self.kx1)**2)/10) * 1000:.1f}", pos_hint={'x': center_x_top, 'y': center_y_top }, color=[0.56, 0.56, 0.24, 1], font_size='20sp')
           
    
    def create_door_activate(self):
        self.chose = "create_door"
    
    def doors_refresh(self, *args):
        for id, door in enumerate(self.door_list):
            p = len(self.door_list) 
            if p != id: 
                ckx1, cky1, ckx2, cky2 = self.doors_points[id]
                x1, x2 = ckx1 * self.width, ckx2 * self.width
                y1, y2 = cky1 * self.height, cky2 * self.height
                door.points = x1, y1, x2, y2
    
    def create_door_function(self, *args):

        self.kx1, self.ky1 = self.points
        self.x1 = self.width * self.kx1
        self.y1 = self.height * self.ky1

        if self.end_points:
            self.kx2, self.ky2 = self.end_points
            self.x2 = self.width * self.kx2
            self.y2 = self.height * self.ky2
        else:
            self.x2, self.y2 = self.x1, self.y1
        
        self.main_door.points = self.x1, self.y1, self.x2, self.y2


    def on_touch_down(self, touch):
        if super(SetupScreen, self).on_touch_down(touch): #If clicking not in create room zone 
            self.up = False
            return False

        self.up = True
        if self.chose == "new_room":
            with self.canvas:
                Color(200/255,200/255,200/255)
                line = Line(width=1.5)
            self.rooms_list.append(line)
            touch.grab(self)
            x =  touch.pos[0]/ self.width
            y = touch.pos[1] / self.height
            self.points = (x, y)
            self.end_points = (x,y)
            self.create_room_function()

        elif self.chose == "create_door":
            with self.canvas:
                Color(0/255,0/255,0/255)
                door = Line(width=8, cap="square")
            self.door_list.append(door)
            touch.grab(self)
            x =  touch.pos[0]/ self.width
            y = touch.pos[1] / self.height
            self.points = (x, y)
            self.end_points = (x,y)
            self.create_door_function()

    def on_touch_move(self, touch):
        if self.chose == "new_room":
            if touch.grab_current is self:
                x =  touch.pos[0]/ self.width
                y = touch.pos[1] / self.height
                self.end_points = (x,y)
                self.create_room_function()

        elif self.chose == "create_door":
            if touch.grab_current is self:
                x =  touch.pos[0]/ self.width
                y = touch.pos[1] / self.height
                self.end_points = (x,y)
                self.create_door_function()

        return super(SetupScreen, self).on_touch_move(touch)
    
    def on_touch_up(self, touch):
        if not self.up: #If clicking not in create room zone 
            return False 
            
        if self.chose == "new_room":
            self.double = not self.double  
            if self.double:
                self.rooms_points.append([self.kx1,self.ky1,self.kx2,self.ky2])
                self.rooms += 1
                self.main_room.points = 0,0
                self.rooms_refresh()
        
        if self.chose == "create_door":
            self.double = not self.double  
            if self.double:
                self.doors_points.append([self.kx1,self.ky1,self.kx2,self.ky2])
                self.rooms += 1
                self.main_door.points = 0,0
                self.doors_refresh()
        

        

class EmployeeSystemApp(App):
    pass

EmployeeSystemApp().run()






















