"""
Action executor for Windows 11
Performs mouse, keyboard, and other computer actions
"""
import pyautogui
import time
from typing import Optional, Tuple
import logging

import config

# Configure pyautogui
pyautogui.FAILSAFE = True  # Move mouse to top-left corner to abort
pyautogui.PAUSE = 0.5  # Small pause between actions


class ActionExecutor:
    """Executes computer actions on Windows 11"""
    
    def __init__(self, screen_width: int = 1920, screen_height: int = 1080):
        """
        Initialize action executor
        
        Args:
            screen_width: Screen width in pixels
            screen_height: Screen height in pixels
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.logger = logging.getLogger(__name__)
        
        # Get actual screen size
        actual_width, actual_height = pyautogui.size()
        self.logger.info(f"Screen size: {actual_width}x{actual_height}")
    
    def click(self, x: int, y: int, button: str = 'left', clicks: int = 1) -> bool:
        """
        Click at specified coordinates
        
        Args:
            x: X coordinate
            y: Y coordinate
            button: Mouse button ('left', 'right', 'middle')
            clicks: Number of clicks (1 for single, 2 for double)
            
        Returns:
            True if successful
        """
        try:
            self.logger.info(f"Clicking at ({x}, {y}) with {button} button, {clicks} times")
            pyautogui.click(x=x, y=y, button=button, clicks=clicks)
            return True
        except Exception as e:
            self.logger.error(f"Error clicking: {e}")
            return False

    def double_click(self, x: int, y: int, button: str = 'left', interval: float = 0.12) -> bool:
        """
        Double-click at specified coordinates using an explicit click interval.

        Some native/proprietary Windows controls do not reliably recognize two
        zero-interval clicks as a double-click.
        """
        try:
            self.logger.info(
                f"Double-clicking at ({x}, {y}) with {button} button, interval={interval}"
            )
            pyautogui.doubleClick(x=x, y=y, button=button, interval=interval)
            return True
        except Exception as e:
            self.logger.error(f"Error double-clicking: {e}")
            return False
    
    def click_relative(self, x_ratio: float, y_ratio: float, 
                      button: str = 'left', clicks: int = 1) -> bool:
        """
        Click at coordinates specified as ratios (0-1) of screen size
        
        Args:
            x_ratio: X coordinate as ratio (0-1) where 0.5 is 500 on a 1000px scale
            y_ratio: Y coordinate as ratio (0-1) where 0.5 is 500 on a 1000px scale
            button: Mouse button
            clicks: Number of clicks
            
        Returns:
            True if successful
        """
        # Convert from 0-1 ratio to actual pixels
        x = int(x_ratio * self.screen_width)
        y = int(y_ratio * self.screen_height)
        
        return self.click(x, y, button, clicks)
    
    def click_normalized(self, x_norm: float, y_norm: float,
                        button: str = 'left', clicks: int = 1) -> bool:
        """
        Click at normalized coordinates (0-1000 scale)
        
        Args:
            x_norm: X coordinate on 0-1000 scale
            y_norm: Y coordinate on 0-1000 scale
            button: Mouse button
            clicks: Number of clicks
            
        Returns:
            True if successful
        """
        # Convert from 0-1000 scale to actual pixels
        x = int((x_norm / 1000.0) * self.screen_width)
        y = int((y_norm / 1000.0) * self.screen_height)
        
        return self.click(x, y, button, clicks)

    def _normalized_to_pixels(self, coordinate) -> Optional[Tuple[int, int]]:
        """Convert a validated normalized coordinate to screen pixels."""
        if not isinstance(coordinate, (list, tuple)) or len(coordinate) != 2:
            self.logger.warning("Mouse action requires a two-value coordinate")
            return None

        if not all(isinstance(value, (int, float)) and 0 <= value <= 1000 for value in coordinate):
            self.logger.warning(f"Invalid normalized coordinate: {coordinate}")
            return None

        return (
            int((coordinate[0] / 1000.0) * self.screen_width),
            int((coordinate[1] / 1000.0) * self.screen_height),
        )
    
    def move_mouse(self, x: int, y: int, duration: float = 0.5) -> bool:
        """
        Move mouse to specified coordinates
        
        Args:
            x: X coordinate
            y: Y coordinate
            duration: Time to take for movement (seconds)
            
        Returns:
            True if successful
        """
        try:
            self.logger.info(f"Moving mouse to ({x}, {y})")
            pyautogui.moveTo(x, y, duration=duration)
            return True
        except Exception as e:
            self.logger.error(f"Error moving mouse: {e}")
            return False
    
    def type_text(self, text: str, interval: float = 0.05) -> bool:
        """
        Type text using keyboard
        
        Args:
            text: Text to type
            interval: Interval between key presses (seconds)
            
        Returns:
            True if successful
        """
        try:
            self.logger.info(f"Typing text: {text[:50]}...")
            pyautogui.write(text, interval=interval)
            return True
        except Exception as e:
            self.logger.error(f"Error typing text: {e}")
            return False
    
    def press_key(self, key: str) -> bool:
        """
        Press a single key
        
        Args:
            key: Key name (e.g., 'enter', 'escape', 'tab')
            
        Returns:
            True if successful
        """
        try:
            self.logger.info(f"Pressing key: {key}")
            pyautogui.press(key)
            return True
        except Exception as e:
            self.logger.error(f"Error pressing key: {e}")
            return False
    
    def hotkey(self, *keys) -> bool:
        """
        Press a combination of keys
        
        Args:
            *keys: Keys to press together (e.g., 'ctrl', 'c')
            
        Returns:
            True if successful
        """
        try:
            self.logger.info(f"Pressing hotkey: {'+'.join(keys)}")
            pyautogui.hotkey(*keys)
            return True
        except Exception as e:
            self.logger.error(f"Error pressing hotkey: {e}")
            return False
    
    def scroll(self, clicks: int) -> bool:
        """
        Scroll the mouse wheel
        
        Args:
            clicks: Number of clicks (positive = up, negative = down)
            
        Returns:
            True if successful
        """
        try:
            self.logger.info(f"Scrolling {clicks} clicks")
            pyautogui.scroll(clicks)
            return True
        except Exception as e:
            self.logger.error(f"Error scrolling: {e}")
            return False

    def hscroll(self, clicks: int) -> bool:
        """Scroll horizontally."""
        try:
            self.logger.info(f"Horizontal scrolling {clicks} clicks")
            pyautogui.hscroll(clicks)
            return True
        except Exception as e:
            self.logger.error(f"Error horizontal scrolling: {e}")
            return False
    
    def drag(self, x: int, y: int, duration: float = config.DRAG_DURATION) -> bool:
        """
        Drag mouse to specified coordinates
        
        Args:
            x: X coordinate
            y: Y coordinate
            duration: Time to take for drag (seconds)
            
        Returns:
            True if successful
        """
        try:
            self.logger.info(f"Dragging to ({x}, {y})")
            pyautogui.dragTo(x, y, duration=duration, button='left')
            return True
        except Exception as e:
            self.logger.error(f"Error dragging: {e}")
            return False
    
    def wait(self, seconds: float) -> bool:
        """
        Wait for specified seconds
        
        Args:
            seconds: Time to wait
            
        Returns:
            True
        """
        self.logger.info(f"Waiting {seconds} seconds")
        time.sleep(seconds)
        return True
    
    def execute_computer_use_action(self, action: dict) -> bool:
        """
        Execute a computer use action from the model
        
        Args:
            action: Action dictionary with 'name' and 'arguments'
            
        Returns:
            True if successful
        """
        try:
            action_name = action.get('name') or action.get('function', {}).get('name')
            arguments = action.get('arguments') or action.get('function', {}).get('arguments', {})
            
            if isinstance(arguments, str):
                import json
                arguments = json.loads(arguments)
            
            self.logger.info(f"Executing action: {action_name} with args: {arguments}")
            
            if action_name in ['computer', 'computer_use']:
                return self._execute_computer_action(arguments)
            else:
                self.logger.warning(f"Unknown action: {action_name}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error executing action: {e}")
            return False
    
    def _execute_computer_action(self, args: dict) -> bool:
        """
        Execute a computer action
        
        Args:
            args: Action arguments with 'action' and other parameters
            
        Returns:
            True if successful
        """
        action_type = args.get('action')
        
        if action_type == 'left_click':
            coordinate = args.get('coordinate')
            if self._normalized_to_pixels(coordinate) is None:
                return False
            return self.click_normalized(coordinate[0], coordinate[1], button='left', clicks=1)
        
        elif action_type == 'left_click_drag':
            start_pixels = self._normalized_to_pixels(args.get('start_coordinate'))
            if start_pixels is None:
                return False
            pixels = self._normalized_to_pixels(args.get('coordinate'))
            if pixels is None:
                return False
            start_x, start_y = start_pixels
            if not self.move_mouse(start_x, start_y):
                return False
            x, y = pixels
            return self.drag(x, y)
        
        elif action_type == 'right_click':
            coordinate = args.get('coordinate')
            if self._normalized_to_pixels(coordinate) is None:
                return False
            return self.click_normalized(coordinate[0], coordinate[1], button='right', clicks=1)
        
        elif action_type == 'double_click':
            pixels = self._normalized_to_pixels(args.get('coordinate'))
            if pixels is None:
                return False
            x, y = pixels
            return self.double_click(x, y, button='left')

        elif action_type == 'triple_click':
            coordinate = args.get('coordinate')
            if self._normalized_to_pixels(coordinate) is None:
                return False
            return self.click_normalized(coordinate[0], coordinate[1], button='left', clicks=3)
        
        elif action_type == 'middle_click':
            coordinate = args.get('coordinate')
            if self._normalized_to_pixels(coordinate) is None:
                return False
            return self.click_normalized(coordinate[0], coordinate[1], button='middle', clicks=1)
        
        elif action_type == 'mouse_move':
            pixels = self._normalized_to_pixels(args.get('coordinate'))
            if pixels is None:
                return False
            x, y = pixels
            return self.move_mouse(x, y)
        
        elif action_type == 'type':
            text = args.get('text', '')
            return self.type_text(text)
        
        elif action_type == 'key':
            keys = args.get('keys')
            if not isinstance(keys, list) or not keys:
                self.logger.warning("Key action requires a non-empty keys list")
                return False
            keys = [str(key).lower() for key in keys]
            if len(keys) == 1:
                return self.press_key(keys[0])
            return self.hotkey(*keys)
        
        elif action_type == 'scroll':
            pixels = args.get('pixels')
            if not isinstance(pixels, (int, float)):
                self.logger.warning("Scroll action requires a numeric pixels value")
                return False
            return self.scroll(int(pixels))

        elif action_type == 'hscroll':
            pixels = args.get('pixels')
            if not isinstance(pixels, (int, float)):
                self.logger.warning("Horizontal scroll action requires a numeric pixels value")
                return False
            return self.hscroll(int(pixels))

        elif action_type == 'wait':
            seconds = args.get('time')
            if not isinstance(seconds, (int, float)) or not 0 <= seconds <= 30:
                self.logger.warning("Wait action requires time between 0 and 30 seconds")
                return False
            return self.wait(seconds)

        else:
            self.logger.warning(f"Unknown computer action: {action_type}")
            return False


if __name__ == "__main__":
    # Test the action executor
    logging.basicConfig(level=logging.INFO)
    
    executor = ActionExecutor()
    
    print("Testing action executor...")
    print("Screen size:", pyautogui.size())
    print("\nMove your mouse to the top-left corner to abort any action")
    
    time.sleep(2)
    
    # Test getting current position
    print("\nCurrent mouse position:", pyautogui.position())
