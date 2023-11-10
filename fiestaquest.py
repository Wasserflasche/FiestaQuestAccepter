import ctypes
import cv2
import numpy as np
import os
import pyautogui
import time
from ctypes import windll
from ctypes import wintypes
from multiprocessing import Process
from pynput import keyboard
from typing import Tuple

currentPath = os.path.dirname(os.path.realpath(__file__))
resoulution = (1920, 1080)

#################################################### Help Functions ####################################################### 

def CheckPixelsAbove(image: np.ndarray, max_loc: Tuple[int, int], offset: int = 15) -> bool:
    rows = image[max_loc[1]- 10 - offset:max_loc[1] - offset, max_loc[0] :max_loc[0] + 100]
    mask = cv2.inRange(cv2.cvtColor(rows, cv2.COLOR_RGB2BGR), (220, 220, 0), (255, 255, 5))
    return np.any(mask)

def OpenQuestWindow() -> Tuple[int, int]:
    baseCoords: Tuple[int, int] = (0,0)
    while baseCoords == (0,0):
        PressKey(l)
        baseCoords = GetCoordsFromDetection(cv2.imread(currentPath + "\\fiestaQuest.png"))
    return baseCoords

def ReadFromFile(fileName: str) -> str:
    with open(fileName) as file:
        return file.read()

def WriteToFile(fileName: str, input: str):
    with open(fileName, "w") as file:
        file.write(str(input))    
   
def GetCoordsFromDetection(image: np.ndarray) -> Tuple[int, int]:
    result = cv2.matchTemplate(Screenshot(), image, cv2.TM_CCOEFF_NORMED) 
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    if max_val > 0.9:
        return (max_loc)
    else:
        return (0, 0)
    
def GetCoordsFromDetectionChat(image: np.ndarray) -> Tuple[int, int]:
    screenshot = Screenshot()
    result = cv2.matchTemplate(screenshot, image, cv2.TM_CCOEFF_NORMED) 
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    if max_val > 0.9:
        x, y = max_loc
        if CheckPixelsAbove(screenshot, max_loc):
            y -= 20
        return (x, y)
    else:
        return (0, 0)  

def SaveImage(image: np.ndarray):
    cv2.imwrite(currentPath + "\\screenshot.png", image)

def Screenshot() -> np.ndarray:
    return cv2.cvtColor(np.array(pyautogui.screenshot().convert('RGB')), cv2.COLOR_RGB2BGR)
   
############################################################################################### Mouse and Keyboard ##############################################################################################################    
      
MOUSEEVENTF_RIGHTDOWN = 0x0008 
MOUSEEVENTF_RIGHTUP = 0x0010 
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_ABSOLUTE = 0x8000
one = 0x31
two = 0x32
three = 0x33
four = 0x34
five = 0x35
six = 0x36
seven = 0x37
e = 0x45
k = 0x4B
l = 0x4C
q = 0x51
s = 0x53
skills = [three, four, five, six, seven]
user32 = ctypes.WinDLL('user32', use_last_error=True)

INPUT_KEYBOARD = 1
INPUT_HARDWARE = 2

KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_KEYUP       = 0x0002
KEYEVENTF_UNICODE     = 0x0004
KEYEVENTF_SCANCODE    = 0x0008

MAPVK_VK_TO_VSC = 0

wintypes.ULONG_PTR = wintypes.WPARAM

class MOUSEINPUT(ctypes.Structure):
    _fields_ = (("dx",          wintypes.LONG),
                ("dy",          wintypes.LONG),
                ("mouseData",   wintypes.DWORD),
                ("dwFlags",     wintypes.DWORD),
                ("time",        wintypes.DWORD),
                ("dwExtraInfo", wintypes.ULONG_PTR))

class KEYBDINPUT(ctypes.Structure):
    _fields_ = (("wVk",         wintypes.WORD),
                ("wScan",       wintypes.WORD),
                ("dwFlags",     wintypes.DWORD),
                ("time",        wintypes.DWORD),
                ("dwExtraInfo", wintypes.ULONG_PTR))

    def __init__(self, *args, **kwds):
        super(KEYBDINPUT, self).__init__(*args, **kwds)
        if not self.dwFlags & KEYEVENTF_UNICODE:
            self.wScan = user32.MapVirtualKeyExW(self.wVk, MAPVK_VK_TO_VSC, 0)

class HARDWAREINPUT(ctypes.Structure):
    _fields_ = (("uMsg",    wintypes.DWORD), ("wParamL", wintypes.WORD), ("wParamH", wintypes.WORD))

class INPUT(ctypes.Structure):
    class _INPUT(ctypes.Union):
        _fields_ = (("ki", KEYBDINPUT), ("mi", MOUSEINPUT), ("hi", HARDWAREINPUT))
    _anonymous_ = ("_input",)
    _fields_ = (("type",   wintypes.DWORD),("_input", _INPUT))

LPINPUT = ctypes.POINTER(INPUT)

def _check_count(result, func, args):
    if result == 0:
        raise ctypes.WinError(ctypes.get_last_error())
    return args

user32.SendInput.errcheck = _check_count
user32.SendInput.argtypes = (wintypes.UINT,
                             LPINPUT,       
                             ctypes.c_int) 
  
def MouseClick(position: Tuple[int, int], clicks: int = 1):
    MoveMouseTo(position)
    for _ in range(clicks):
        ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        InputSleep()
        ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        InputSleep()
   
def MoveMouseTo(position: Tuple[int, int]):
    x_normalized = int(65535 * (position[0] / resoulution[0]))
    y_normalized = int(65535 * (position[1] / resoulution[1]))
    ctypes.windll.user32.mouse_event(MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE, x_normalized, y_normalized, 0, 0)   
    InputSleep()
   
def MouseRightDown():
    ctypes.windll.user32.mouse_event(MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
    InputSleep()
    
def MouseRightUp():   
    ctypes.windll.user32.mouse_event(MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)
    InputSleep()
   
def MouseMove():
    windll.user32.mouse_event(1, 100, 0, 0, 0)
    InputSleep()
    windll.user32.mouse_event(1, 100, 0, 0, 0)
    InputSleep()
    windll.user32.mouse_event(1, 100, 0, 0, 0)
   
def KeyDown(hexKeyCode):
    x = INPUT(type=INPUT_KEYBOARD,
              ki=KEYBDINPUT(wVk=hexKeyCode))
    user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(x))
    time.sleep(0.035)
   
def PressKey(hexKeyCode):
    KeyDown(hexKeyCode)
    ReleaseKey(hexKeyCode)

def ReleaseKey(hexKeyCode):
    x = INPUT(type=INPUT_KEYBOARD,
              ki=KEYBDINPUT(wVk=hexKeyCode,
                            dwFlags=KEYEVENTF_KEYUP))
    user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(x))
    time.sleep(0.035)

def InputSleep():
    time.sleep(0.02)    

def On_press(key: str):
    if any([key in z for z in [{keyboard.KeyCode(char='+')}]]):
        if ReadFromFile(currentPath + "\\stop.txt") == "0":
            WriteToFile(currentPath + "\\stop.txt", "1")
        else:
            WriteToFile(currentPath + "\\stop.txt", "0") 
    if any([key in z for z in [{keyboard.Key.shift}]]): 
        WriteToFile(currentPath + "\\stop.txt", "2")

############################################################################################### Main Functions #####################################################################################################
 
def AcceptQuests():
    baseCoords:Tuple[int, int] = OpenQuestWindow()
    coords:Tuple[int, int] = (baseCoords[0] + 200, baseCoords[1] + 60)
    MouseClick(coords)
    MouseClick((coords[0], coords[1] + 45))
    MouseClick((baseCoords[0] + 75, baseCoords[1] + 540))
    ClickTrough()

def ClickTrough():
    image: np.ndarray = cv2.imread(currentPath + "\\fiestaQuest2.png")
    while True:
        time.sleep(0.1)
        position: Tuple[int, int] = GetCoordsFromDetectionChat(image)
        if position != (0,0):
            MouseClick(position)
        else:
            time.sleep(0.1)
            break

def DetectFinishedQuest(baseCoords: Tuple[int, int]) -> bool:
    image: np.ndarray = Screenshot()
    rows: np.ndarray = image[baseCoords[1] + 90 :baseCoords[1] + 260, baseCoords[0] + 383 : baseCoords[0] + 448]
    mask: np.ndarray = cv2.inRange(cv2.cvtColor(rows, cv2.COLOR_RGB2BGR), (220,0,0), (230,13,3))
    if np.any(mask):
        y, x = np.where(mask)
        MouseClick((baseCoords[0] + x[0] + 383, baseCoords[1] + y[0] + 90))
        return True
    else:
        return False

def FiestaQuestAccepter():
    WriteToFile(currentPath + "\\stop.txt", "1")
    while True:
        if ReadFromFile(currentPath + "\\stop.txt") == "0":
            AcceptQuests()
        elif ReadFromFile(currentPath + "\\stop.txt") == "1":    
            time.sleep(0.1)
        elif ReadFromFile(currentPath + "\\stop.txt") == "2":    
            FinishQuests()

def FinishQuests():
    if FinishedQuest():
        ClickTrough()
    else:
        WriteToFile(currentPath + "\\stop.txt", "1")

def FinishedQuest() -> bool:
    baseCoords: Tuple[int, int] = OpenQuestWindow()
    for _ in range(5):
        if DetectFinishedQuest(baseCoords):
            MouseClick((baseCoords[0] + 60, baseCoords[1] + 537))
            return True
        else:
            ScrollQuest(baseCoords)     
    return False

def ScrollQuest(baseCoords: Tuple[int, int]):
    MouseClick((baseCoords[0] + 500, baseCoords[1] + 230), 7)

############################################################################################### Start ##############################################################################################################
       
if __name__ == '__main__':    
    processListener = keyboard.Listener(on_press=On_press)
    processBot = Process(target = FiestaQuestAccepter)
    processBot.start()
    processListener.start()
    processBot.join()
    processListener.join()
