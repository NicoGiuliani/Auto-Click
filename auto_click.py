#!python3

from datetime import datetime
import keyboard
import pyautogui
import pygetwindow
import pynput
import time
import sys


cmdWindow = pygetwindow.getWindowsWithTitle('C:\\Windows\\System32\\cmd.exe')[0]
startPoints = []
endPoints   = []
rightClicks = []
clickTime   = []

defaultTimes = {
    "postClick" : 1,
    "postDrag"  : 1,
    "dragDrop"  : 1,
    "drag"      : 1.5
}

eventList = []

############################## EVENT HANDLERS ##############################

def on_click(x, y, button, pressed):
    if pressed:
        if button == pynput.mouse.Button.left:
            startPoints.append((x, y))
            rightClicks.append((0))
            clickTime.append(datetime.now())
        else:
            rightClicks.append((x, y))
            clickTime.append(datetime.now())
    else:
        if button == pynput.mouse.Button.left:
            endPoints.append((x, y))
        else:
            startPoints.append((0))
            endPoints.append((0))
  
############################################################################
  
def GetButtonCoordinates():
    mouseListener = pynput.mouse.Listener(on_click=on_click)
    mouseListener.start()
    currentMessage = ""
    
    print("\nBegin setting actions\n")

    while True:
        thisKey = keyboard.read_key()
        if thisKey == "`":
            keyboard.press("backspace")
            mouseListener.stop()
            # print("\nCaptured:\n")
            # print(f"Start points:\t{startPoints}")
            # print(f"End points:\t{endPoints}")
            # print(f"Right clicks:\t{rightClicks}")
            # print(f"Wait times:\t{extraWait}")
            break
        elif thisKey == "esc":
            print("\nExiting....")
            sys.exit()
    
    cmdWindow.activate()

###########################################################################


GetButtonCoordinates()
shouldSkip = False
dragEvent = False
selectedRange = ""

numClicks = len(startPoints)
for i in range(numClicks):
    position = startPoints[i]
    endPosition = endPoints[i]
    clickNum = "0" * (2 - len(str(i + 1))) + str(i + 1)
    
    if shouldSkip:
        shouldSkip = not shouldSkip
        continue
    
    # Checks for right click
    if position == 0 and endPosition == 0:      
        eventList.append(["Right click", rightClicks[i][0], rightClicks[i][1], defaultTimes['postClick'], 0])
        continue
    
    # Checks for double click
    if i + 1 < numClicks and position == startPoints[i + 1]:
        timeDifference = (clickTime[i + 1] - clickTime[i]).total_seconds()
        # print(f"Difference: {timeDifference}")
        if timeDifference < 0.55:
            shouldSkip = True
            eventList.append(["Double click", position, defaultTimes['postClick'], 0])
            continue
            
    # Checks for drag
    if position != endPosition:
        # Checks for drag/drop
        if dragEvent:
            xValues = [selectedRange[0][0], selectedRange[1][0]]
            yValues = [selectedRange[0][1], selectedRange[1][1]]
            
            lowX  = min(xValues)
            lowY  = min(yValues)
            highX = max(xValues)
            highY = max(yValues)
            
            if (position[0] > lowX and position[0] < highX and position[1] > lowY and position[1] < highY):
                eventList.append(["Drag drop", position, endPosition, defaultTimes['postClick'], 0])
                continue
                
        dragEvent = True
        selectedRange = [position, endPosition]
        eventList.append(["Drag", position, endPosition, defaultTimes['postDrag'], 0])
        continue
    
    eventList.append(["Click", position, defaultTimes['postClick'], 0])


waitTimes = [0] * len(eventList)
print("Recorded actions:")
for i in range(len(eventList)):
    waitTimes[i] = eventList[i][-1]
    j = "0" * (2 - len(str(i + 1))) + str(i + 1)
    thisEvent = str(eventList[i][0]) + (" " * (12 - len(str(eventList[i][0]))))
    print(f"{j}. {thisEvent} - {waitTimes[i]} seconds")

while True:
    try:
        numIterations = int(input("\nFor how many iterations would you like to run this sequence? "))
        if numIterations < 0:
            raise Exception() 
        break
    except Exception:
        print("\nInvalid input.")
        pass
    
while True:
    try:
        response = input("\nWould you like to modify the wait times (y/n)? ")
        if response == 'y':
            print("\nEnter wait times in seconds for each action (leave blank to represent 0)\n")
            for i in range(len(waitTimes)):
                while True:
                    try:
                        j = "0" * (2 - len(str(i + 1))) + str(i + 1)
                        response = input(f"{j}: ")
                        if len(response) == 0:
                            response = 0
                        waitTimes[i] = float(response)
                        if waitTimes[i] < 0:
                            raise Exception()
                        break
                    except Exception:
                        print("Invalid input\n")
            
            print("\nRecorded actions:")
            for i in range(len(eventList)):
                j = "0" * (2 - len(str(i + 1))) + str(i + 1)
                thisEvent = str(eventList[i][0]) + (" " * (12 - len(str(eventList[i][0]))))
                print(f"{j}. {thisEvent} - {waitTimes[i]} seconds")
                
            response = input("\nDoes this look correct (y/n)? ")
            if response.lower() == "y":
                for x in range(len(eventList)):
                    eventList[x][-1] = waitTimes[x]
                print("\nWait times modified")
                break   
            else:
                waitTimes = [0] * len(eventList)
        elif response == 'n':
            break
        else:
            pass
    except Exception:
        print("\nInvalid input.")
        pass

input("\nPress 'Enter' to begin")

for iteration in range(numIterations):
    print("\n" + "-" * 75 + "\n")
    print(f"Iteration: {str(iteration + 1)}")
    
    for i in range(len(eventList)):
        clickNum = "0" * (2 - len(str(i + 1))) + str(i + 1)
        print(f"\n{clickNum}", end=': ')
        
        if eventList[i][0] == "Click":
            print(f"Click\t\t{eventList[i][1]}")
            pyautogui.click(eventList[i][1])
            time.sleep(eventList[i][2])
            print(f"    Waiting {eventList[i][3]} seconds")
            time.sleep(eventList[i][3])
        elif eventList[i][0] == "Right click":
            print(f"Right click\t\t({eventList[i][1]}, {eventList[i][2]})")
            pyautogui.click(button='right', x=eventList[i][1], y=eventList[i][2])
            time.sleep(eventList[i][3])
            print(f"    Waiting {eventList[i][4]} seconds")
            time.sleep(eventList[i][4])
        elif eventList[i][0] == "Double click":
            print(f"Double click\t{eventList[i][1]}")
            pyautogui.doubleClick(eventList[i][1])
            time.sleep(eventList[i][2])
            print(f"    Waiting {eventList[i][3]} seconds")
            time.sleep(eventList[i][3])
        elif eventList[i][0] == "Drag":
            print(f"Drag\t\t{eventList[i][1]} to {eventList[i][2]}")
            pyautogui.click(eventList[i][1])
            time.sleep(eventList[i][3])
            pyautogui.dragTo(eventList[i][2], duration=eventList[i][3])
            time.sleep(eventList[i][3])
            print(f"    Waiting {eventList[i][4]} seconds")
            time.sleep(eventList[i][4])
        elif eventList[i][0] == "Drag drop":
            print(f"Drag/Drop\t\t{eventList[i][1]} to {eventList[i][2]}")
            pyautogui.mouseDown(eventList[i][1])
            pyautogui.dragTo(eventList[i][2], duration=eventList[i][3])
            pyautogui.mouseUp()
            time.sleep(eventList[i][3])
            print(f"    Waiting {eventList[i][4]} seconds")
            time.sleep(eventList[i][4])
            
print("\nComplete")   
cmdWindow.activate()

