import pygetwindow as gw
import win32api
from pynput.keyboard import Key, Controller

class OsCordinator():

    def __init__(self=None):
        self.ignore_list = ["","Program Manager", "Windows Input Experience" , "Settings"]

    def get_program_display_number(self, program_title):
        windows = gw.getWindowsWithTitle(program_title)
        try:
            if windows:
                window = windows[0]
                hwnd = window._hWnd
                monitor_info = win32api.GetMonitorInfo(win32api.MonitorFromWindow(hwnd))
                #monitor = monitor_info.get("Monitor")
                monitor_number = monitor_info['Device'][-1]
                #print(monitor_number)
                return int(monitor_number)
        except:
            return 0

        return 0

    def get_program_with_max_size(self, display_number=1):
        programs = gw.getAllTitles()
        #print(programs)
        max_area = 0
        max_program = None

        for program in programs:
            window = gw.getWindowsWithTitle(program)[0]
            if window.title in self.ignore_list:
                continue
            program_display_number = self.get_program_display_number(window.title) 
            
            if program_display_number == display_number:
                area = window.width * window.height
                print(window.title + ":" + str(program_display_number)+"  #"+str(area))
                if area > max_area:
                    max_area = area
                    max_program = program
                    window.activate()

        return max_program

    def move_window_to_display(self):
        keyboard = Controller()

        keyboard.press(Key.cmd)
        keyboard.press(Key.shift)
        keyboard.press(Key.left)
        keyboard.release(Key.cmd)
        keyboard.release(Key.shift)
        keyboard.release(Key.left)
    
    def do_swapping(self, monitor_number):
        max_program = self.get_program_with_max_size(monitor_number)
        print("Program with maximum size:", max_program)
        if not max_program is None:
            self.move_window_to_display()




def main():
   oc = OsCordinator()
   oc.do_swapping(2)

if __name__ == "__main__":
   main()


