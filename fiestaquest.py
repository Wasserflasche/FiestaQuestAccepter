import ctypes
import cv2
import os
import time
import pytesseract
import numpy as np
from ctypes import windll
from multiprocessing import Process
from pynput import keyboard
from typing import Dict, List, Tuple
import pyautogui

pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
currentPath = os.path.dirname(os.path.realpath(__file__))
resoulution = (1920, 1080)
#################################################### Help Functions ####################################################### 
        
def ReadFromFile(fileName: str):
    with open(fileName) as file:
        return file.read()

def WriteToFile(fileName: str, input: str):
    with open(fileName, "w") as file:
        file.write(str(input))  
   
def GetBoxes(lower: Tuple [int, int, int], upper: Tuple [int, int, int]):
    return pytesseract.image_to_data(cv2.inRange(Screenshot(), lower, upper), output_type='dict')   
   
def GetCoordsFromBoxes(boxes: Dict[str, List[int]], index: int):
    x, y, w, h = (boxes['left'][index],boxes['top'][index],boxes['width'][index],boxes['height'][index],)
    return (x + w // 2, y + h // 2)   
   
def GetCoordsFromDetection(image: np.ndarray):
    result = cv2.matchTemplate(Screenshot(), image, cv2.TM_CCOEFF_NORMED) 
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    x, y = max_loc
    return(x,y)   
 
def Screenshot():
    return pyautogui.screenshot().convert("RGB")
    
############################################################################################### Mouse and Keyboard ##############################################################################################################    
   
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_ABSOLUTE = 0x8000   
  
def Click(position, count:int = 1):
    MoveMouseTo(position) 
    for i in range(count):        
        MouseClick()   
  
def MouseClick():
    ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.1)
    ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
   
def MoveMouseTo(position: Tuple[int, int]):
    x_normalized = int(65535 * (position[0] / resoulution[0]))
    y_normalized = int(65535 * (position[1] / resoulution[1]))
    ctypes.windll.user32.mouse_event(MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE, x_normalized, y_normalized, 0, 0)   
    time.sleep(0.05)
   
def MouseRightDown():
    ctypes.windll.user32.mouse_event(MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
    time.sleep(0.05)
    
def MouseRightUp():   
    ctypes.windll.user32.mouse_event(MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)
    time.sleep(0.05)
   
def MouseMove(count:int):
    for i in range(count):
        windll.user32.mouse_event(1, 100, 0, 0, 0)
        time.sleep(0.05)  
  
Keyboard: keyboard.Controller = keyboard.Controller()    
   
def PressKey(key: str):
    Keyboard.press(key) 

def On_press(key: str):
    if any([key in z for z in [{keyboard.Key.shift, keyboard.KeyCode(char='+')}, {keyboard.Key.shift, keyboard.KeyCode(char='Ö')}]]):
        if ReadFromFile(currentPath + "\\stop.txt") == "0":
            WriteToFile(currentPath + "\\stop.txt", "1")
        else:
            WriteToFile(currentPath + "\\stop.txt", "0") 
    if any([key in z for z in [{keyboard.Key.shift, keyboard.KeyCode(char='ä')}, {keyboard.Key.shift, keyboard.KeyCode(char='Ä')}]]): 
        WriteToFile(currentPath + "\\stop.txt", "2")
        
############################################################################################### Main Functions #####################################################################################################
 
def AcceptQuests():
    DetectQuest()
    while True:
        time.sleep(0.1)
        position = DetectPosition()
        if position != (0,0):
            Click(position)
        else:
            AcceptQuest()
            break
 
def AcceptQuest():
    boxes = GetBoxes((246, 255, 0), (255, 255, 5))
    for i in range(len(boxes['text'])):
        if boxes['text'][i].strip().lower() != "" and boxes['text'][i].strip().lower() != " ":
            Click(GetCoordsFromBoxes(boxes, i))
            break
 
def DetectPosition():
    boxes = GetBoxes((246, 255, 0), (255, 255, 5))
    for i in range(len(boxes['text'])):
        if boxes['text'][i].strip().lower() == 'weiter' or boxes['text'][i].strip().lower() == 'quest':
            return GetCoordsFromBoxes(boxes, i)
    return (0,0) 
 
def DetectQuest():
    PressKey("l")
    baseCoords = GetCoordsFromDetection(cv2.imread(currentPath + "fiestaQuest.png"))
    coords = (baseCoords[0] + 200, baseCoords[1] + 119)
    Click(coords)
    Click((coords[0], coords[1] + 45))
    Click((baseCoords[0] + 75, baseCoords[1] + 540))
     
def DetectQuestFinish():
    boxes = GetBoxes((120, 0, 0), (255, 30, 30))
    for i in range(len(boxes['text'])):
        if boxes['text'][i].strip().lower() == "belohnung":
            Click(GetCoordsFromBoxes(boxes, i))
            return True 
    return False

def FiestaBot():
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
        while True:
            position = DetectPosition()
            if position != (0,0):
                Click(position)
            else:
                AcceptQuest()
                break
    else:
        WriteToFile(currentPath + "\\stop.txt", "1")

def FinishedQuest():
    PressKey("l")
    for _ in range(5):
        if DetectQuestFinish():
            coords = GetCoordsFromDetection(cv2.imread(currentPath + "fiestaQuest.png"))
            Click((coords[0] + 70, coords[1] + 540))
            return True
        else:
            ScrollQuest()     
    return False

def ScrollQuest():
    coords = GetCoordsFromDetection(cv2.imread(currentPath + "fiestaQuest.png"))
    Click((coords[0] + 500, coords[1] + 235), 7)

############################################################################################### Start ##############################################################################################################
       
if __name__ == '__main__':    
    processListener = keyboard.Listener(on_press=On_press)
    processBot = Process(target = FiestaBot)
    processBot.start()
    processListener.start()
    processBot.join()
    processListener.join()
