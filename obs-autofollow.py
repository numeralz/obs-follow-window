

import time
import pyautogui
import logging
from obswebsocket import obsws, requests
from pygetwindow import getActiveWindow
import math

# Configuration

# Output Size
taskBarHeight = 48
targetHeight = 1080
targetWidth = 1920
host = "localhost"
port = 4455
password = ""

running = True
connected = False

screenWidth, screenHeight = pyautogui.size()
scale = ( targetHeight / (screenHeight-taskBarHeight) )

ws = obsws(host, port, password)

def find_display_source_id():
    try:
        # Get a list of all sources
        current_scene = ws.call(requests.GetCurrentScene())
        # print(current_scene)

        # Get the sources in the current scene
        sources = current_scene.get_sources()

        print(sources)

        # Iterate through the sources and find the one with the name "Display"
        display_source_id = None
        
        for source in sources.getSources():
            if source['name'] == "Display":
                display_source_id = source['sourceId']
                break

        return display_source_id
    except:
        return


# active title
def get_active_window_title():
    window = getActiveWindow()
    return window.title if window else None
    
prevWindow = getActiveWindow()
prevLeft = prevWindow.left
prevTop = 0
sceneId = 0

def obsSetPosition(x):
    x = round(x)
    # print(f"set x: {x}")
    res = ws.call(requests.SetSceneItemTransform(
        sceneName="Desktop",
        sceneItemId=sceneId,
        sceneItemTransform={ "positionX": -x }
    ))

def obsSetY(y):
    y = round(y)
    # print(f"set y: {y}")
    res = ws.call(requests.SetSceneItemTransform(
        sceneName="Desktop",
        sceneItemId=sceneId,
        sceneItemTransform={"positionY": -y  }
    ))



# Main loop
prev_x = 0

# disconnect
def onConnectionClosed(args):
    print("Connection closed")
    connected = False

ws.on_disconnect = onConnectionClosed
lastActiveWindow = None

targetX =0

def mainLoop():
    global connected
    global running
    global prev_x
    global prevLeft
    global sceneId
    global lastActiveWindow
    global targetX

    while True:

        # Connect/Reconnect
        while not connected:
            print("Connecting...")
            try:
                ws.connect()
                connected = True
                obsSetY(0)

                print("Connected")

                sceneId = ws.call(requests.GetSceneItemId(
                    sceneName="Desktop",
                    sourceName="Display"
                )).getSceneItemId()
                
                res = ws.call(requests.SetSceneItemTransform(
                    sceneName="Desktop",
                    sceneItemId=sceneId,
                    sceneItemTransform={"scaleX": scale, "scaleY": scale, "cropLeft": 0, "cropRight": 0, "cropBottom": 48 }
                ))
            except:
                print("...failed to connect")
                time.sleep(1) 

        # Connected
        try:
            x, y = pyautogui.position()
            activeWindow = getActiveWindow()

            if(activeWindow != lastActiveWindow):
                lastActiveWindow = activeWindow
                # print(activeWindow)

            if( lastActiveWindow ):

                # skip following task manager, program manager, obs
                if (
                    lastActiveWindow and
                    lastActiveWindow.title != "Program Manager" and
                    lastActiveWindow.title != "Task Switching" and
                    not lastActiveWindow.title.startswith("OBS")
                ):
                    activeLeft = lastActiveWindow.left * scale
                    activeWidth = lastActiveWindow.width * scale

                    if( activeWidth < 1 ):
                        continue

                    offset = 0
                    relXPercent = 0

                    # window is wider than target?
                    if(activeWidth > targetWidth):
                        numChunks = math.ceil(activeWidth / targetWidth)
                        relX = x - lastActiveWindow.left
                        relXPercent = (relX / (lastActiveWindow.width)) - 0.5
                        relXPercent = round( relXPercent*numChunks) / numChunks
                        relXPercent = min(0.5,max(-0.5, relXPercent))

                    newLeft = activeLeft + (0.5+relXPercent) * (activeWidth - targetWidth)
                    newLeft = round(min(max(newLeft, 0), (screenWidth*scale - targetWidth) )) 
                
            if prevLeft != newLeft:
                prevLeft = newLeft
                targetX = newLeft

            # Take a step halfway to the target
            if( abs(prev_x - targetX) > 2 ):
                prev_x = prev_x + (targetX - prev_x) * 0.5
                obsSetPosition(prev_x)
            else:
                prev_x = targetX

            # Take a quick nap
            time.sleep(1/60)

        except KeyboardInterrupt:
            print("Exiting")
            running = False
            break
        except Exception as e:
            print(e)
            time.sleep(1)

mainLoop()