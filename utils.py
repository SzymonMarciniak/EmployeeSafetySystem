import math 

def CenterOfLine(xx, yy, width, height):
    x0 = xx[0] * width  
    x1 = xx[1] * width
    y0 = yy[0] * height
    y1 = yy[1] * height

    x = ((x0 + x1) / 2) 
    y = ((y0 + y1) / 2) 
    return x,y