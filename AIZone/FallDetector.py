import math

class FallDetector:
    
    @staticmethod
    def calculate_center_line_points(landmarks: list) -> tuple:
        """
        Calculate body center line points 

        Parameters
        ----------
        landmarks: list
            points of: left shouder, right shouder, left ankle, right ankle
        
        Raises
        ------
        landmarks: list
            The landmarks must be list 
        landmarks: list 
            The landmarks list must have 4 body points

        Returns
        -------
        center_line_points: list 
            List with 2 points to form a line
        """
        if type(landmarks) != list:
            raise ValueError("Incorrect value type. Must be list.")

        if len(landmarks) != 4:
            raise ValueError("You must give 4 body points.")

        left_shouder, right_shouder, left_ankle, right_ankle = landmarks 
        center_line_points =((abs(int((left_shouder[0] - right_shouder[0]) /2) - left_shouder[0]), abs(int(left_shouder[1] - right_shouder[1]) - right_shouder[1])),\
             (abs(int((left_ankle[0] - right_ankle[0]) /2) - left_ankle[0]), abs(int(left_ankle[1] - right_ankle[1]) - right_ankle[1])))
        return center_line_points
    
    @staticmethod
    def calculate_angle_with_OX(line_points: tuple) -> int:
        """
        Calculate angle between the line and the x axis

        Parametrs
        ---------
        line_points: tuple
            2 points belong to line

        Return
        ------
        degress: int 
            Degrees between the line and the x axis
        """
        point_1, point_2 = line_points
        y = abs(point_1[1]-point_2[1])
        x = abs(point_1[0]-point_2[0])
        if x == 0:
            x = 0.001
        A = y / x

        alpha = math.atan(A)
        

        degress = abs(int(math.degrees(alpha)))
        if degress > 360:
            z = degress // 360
            degress = degress - z*360
        return degress

    def check_body_position(self, landmarks, min_angle=60):
        """
        Detect fall if person falls on the left or right

        Params
        ------
        landmarks: list
            points of: left shouder, right shouder, left ankle, right ankle
        min_angle: int, optional
            max angle betwen person and floor
        """
        center_line_points = self.calculate_center_line_points(landmarks)
        alpha = self.calculate_angle_with_OX(center_line_points)
        
        if (min_angle > alpha): 
            print(f"Fall, alpha: {alpha}")
        else:
            print(f"No fall, alpha: {alpha}") 
 


