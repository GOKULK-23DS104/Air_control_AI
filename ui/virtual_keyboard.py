import cv2
import pyautogui

class VirtualKeyboard:
    def __init__(self):
        # QWERTY Layout
        self.keys = [
            ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
            ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
            ['Z', 'X', 'C', 'V', 'B', 'N', 'M', 'BACK'],
            ['SPACE']
        ]
        
        # Sizing and styling
        self.key_w = 60
        self.key_h = 60
        self.padding = 10
        self.start_y = 150 # Start a bit lower on the screen
        
        self.hitboxes = []
        
    def _calculate_hitboxes(self, frame_w):
        self.hitboxes = []
        y = self.start_y
        
        for row in self.keys:
            # Calculate total row width to center it
            row_width = 0
            for key in row:
                if key == 'SPACE':
                    row_width += 300
                elif key == 'BACK':
                    row_width += 100
                else:
                    row_width += self.key_w
            row_width += (len(row) - 1) * self.padding
            
            x = int((frame_w - row_width) / 2)
            
            for key in row:
                w = self.key_w
                if key == 'SPACE':
                    w = 300
                elif key == 'BACK':
                    w = 100
                    
                self.hitboxes.append({
                    'key': key,
                    'x': x,
                    'y': y,
                    'w': w,
                    'h': self.key_h
                })
                x += w + self.padding
            y += self.key_h + self.padding

    def draw(self, frame):
        h, w, _ = frame.shape
        if not self.hitboxes:
            self._calculate_hitboxes(w)
            
        # Create a transparent overlay for the "glass" look
        overlay = frame.copy()
        
        # Futuristic Colors (BGR format)
        bg_color = (60, 30, 10)      # Dark translucent cyan/blue background
        border_color = (255, 200, 50) # Bright neon cyan/blue border
        text_color = (255, 255, 255) # White text
        
        for box in self.hitboxes:
            bx, by, bw, bh = box['x'], box['y'], box['w'], box['h']
            
            # Draw semi-transparent filled background
            cv2.rectangle(overlay, (bx, by), (bx + bw, by + bh), bg_color, -1)
            
        # Blend the overlay with the original frame
        cv2.addWeighted(overlay, 0.4, frame, 0.6, 0, frame)
        
        for box in self.hitboxes:
            bx, by, bw, bh = box['x'], box['y'], box['w'], box['h']
            
            # Draw solid glowing border directly on the blended frame
            cv2.rectangle(frame, (bx, by), (bx + bw, by + bh), border_color, 2)
            
            # Add Key Text
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.8
            thickness = 2
            
            text_size = cv2.getTextSize(box['key'], font, font_scale, thickness)[0]
            text_x = bx + int((bw - text_size[0]) / 2)
            text_y = by + int((bh + text_size[1]) / 2)
            
            cv2.putText(frame, box['key'], (text_x, text_y), font, font_scale, text_color, thickness)
            
    def check_click(self, x, y):
        """
        Checks if the (x, y) coordinate falls inside any key.
        Returns True if a key was pressed, False otherwise.
        """
        for box in self.hitboxes:
            if box['x'] <= x <= box['x'] + box['w'] and box['y'] <= y <= box['y'] + box['h']:
                key = box['key']
                if key == 'SPACE':
                    pyautogui.press('space')
                elif key == 'BACK':
                    pyautogui.press('backspace')
                else:
                    pyautogui.press(key.lower())
                return True
        return False
