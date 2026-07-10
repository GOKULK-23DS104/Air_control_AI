from __future__ import annotations

import cv2
import pyautogui
import math
import time

from core.camera import Camera
from core.hand_tracker import HandTracker
from core.smoother import PointSmoother
from controllers.mouse_controller import MouseController
from ui.virtual_keyboard import VirtualKeyboard
from utils.logger import get_logger


logger = get_logger(__name__)


def main() -> None:
    camera = Camera()
    tracker = HandTracker()
    smoother = PointSmoother()
    mouse = MouseController()

    logger.info("AirControlAI starting")
    
    if not camera.is_available():
        logger.error("Camera is not available.")
        return
        
    logger.info("Hand tracker ready: %s", tracker.is_available())
    if tracker.load_error is not None:
        logger.warning("Hand tracker unavailable: %s", tracker.load_error)
        return
        
    logger.info("Mouse controller ready: %s", mouse.is_available())
    logger.info("Smoother window: %s", smoother.window_size)
    
    screen_w, screen_h = pyautogui.size()
    
    # State for clicking
    last_click_time = 0
    click_cooldown = 0.5 # half a second between clicks
    
    virtual_keyboard = VirtualKeyboard()
    show_keyboard = False
    
    logger.info("Entering main application loop. Press 'q' in the window to quit, 'k' to toggle keyboard.")
    
    while True:
        success, frame = camera.read()
        if not success or frame is None:
            logger.warning("Failed to read from camera.")
            time.sleep(0.1)
            continue
            
        # Flip the frame horizontally for a more intuitive mirror view
        frame = cv2.flip(frame, 1)
        
        # Detect hands
        result = tracker.detect(frame)
        
        # Check if landmarks were found
        hand_landmarks_list = None
        
        if tracker._tasks_mode:
            if hasattr(result, 'hand_landmarks') and result.hand_landmarks:
                hand_landmarks_list = result.hand_landmarks
        else:
            if hasattr(result, 'multi_hand_landmarks') and result.multi_hand_landmarks:
                hand_landmarks_list = result.multi_hand_landmarks
                
        if hand_landmarks_list:
            # Only use the first detected hand
            hand_landmarks = hand_landmarks_list[0]
            
            # Legacy mode returns objects with .landmark attribute containing the points
            if hasattr(hand_landmarks, 'landmark'):
                landmarks = hand_landmarks.landmark
            else:
                landmarks = hand_landmarks # Tasks mode is usually a list of normalized landmarks
                
            if len(landmarks) > 20:
                # Get tips and PIP joints to check if fingers are folded
                index_tip = landmarks[8]
                index_pip = landmarks[6]
                middle_tip = landmarks[12]
                middle_pip = landmarks[10]
                ring_tip = landmarks[16]
                ring_pip = landmarks[14]
                pinky_tip = landmarks[20]
                pinky_pip = landmarks[18]
                thumb_tip = landmarks[4]
                
                # A finger is considered extended if its tip is higher (smaller Y) than its PIP joint
                index_extended = index_tip.y < index_pip.y
                middle_folded = middle_tip.y > middle_pip.y
                ring_folded = ring_tip.y > ring_pip.y
                pinky_folded = pinky_tip.y > pinky_pip.y
                
                # The clutch is engaged ONLY if pointing (Index extended, others folded)
                is_pointing = index_extended and middle_folded and ring_folded and pinky_folded
                
                if is_pointing:
                    # Convert normalized coordinates to screen coordinates
                    target_x = int(index_tip.x * screen_w)
                    target_y = int(index_tip.y * screen_h)
                    
                    # Smooth the movement
                    smoothed_x, smoothed_y = smoother.update((target_x, target_y))
                    
                    # Move the mouse
                    try:
                        mouse.move_to(int(smoothed_x), int(smoothed_y))
                    except pyautogui.FailSafeException:
                        logger.info("Failsafe triggered. Exiting.")
                        break
                        
                    # Calculate distance between thumb and index for pinch gesture (click)
                    dist = math.hypot(index_tip.x - thumb_tip.x, index_tip.y - thumb_tip.y)
                    
                    # If distance is small enough, it's a pinch
                    if dist < 0.05: # Threshold can be adjusted
                        current_time = time.time()
                        if current_time - last_click_time > click_cooldown:
                            if show_keyboard:
                                frame_x = int(index_tip.x * frame.shape[1])
                                frame_y = int(index_tip.y * frame.shape[0])
                                handled = virtual_keyboard.check_click(frame_x, frame_y)
                                if not handled:
                                    mouse.click()
                            else:
                                mouse.click()
                            last_click_time = current_time
                            
                    # Draw circles on tips for visual feedback
                    h, w, _ = frame.shape
                    cx_idx, cy_idx = int(index_tip.x * w), int(index_tip.y * h)
                    cx_th, cy_th = int(thumb_tip.x * w), int(thumb_tip.y * h)
                    cv2.circle(frame, (cx_idx, cy_idx), 10, (255, 0, 0), cv2.FILLED)
                    cv2.circle(frame, (cx_th, cy_th), 10, (0, 255, 0), cv2.FILLED)
                    if dist < 0.05:
                        # Draw a red line connecting them to signify a click
                        cv2.line(frame, (cx_idx, cy_idx), (cx_th, cy_th), (0, 0, 255), 3)
                else:
                    # Reset the smoother if not pointing to avoid rubber-banding when pointing resumes
                    smoother.reset()
                    
        # Draw virtual keyboard if toggled
        if show_keyboard:
            virtual_keyboard.draw(frame)
            
        # Display the frame
        cv2.imshow("AirControlAI - Camera Feed", frame)
        
        # Break loop on 'q' press, toggle on 'k'
        key_pressed = cv2.waitKey(1) & 0xFF
        if key_pressed == ord('q'):
            logger.info("Quit command received.")
            break
        elif key_pressed == ord('k'):
            show_keyboard = not show_keyboard
            
    # Cleanup
    camera.release()
    tracker.close()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
