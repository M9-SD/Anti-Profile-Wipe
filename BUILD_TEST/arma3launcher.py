import os
import subprocess
import shutil
from threading import Thread
from time import sleep

"""
thefile = __file__
thefilepath = os.path.abspath(thefile)
theFolder = os.path.dirname(__file__)

print(f"{thefile=}")
print(f"{thefilepath=}")
print(f"{theFolder=}")

os.chdir(theFolder)


exePath = "C:\\Users\\M9-SD\\Documents\\Arma 3 - Scripts\\Anti-Profile-Wipe\\BUILD_TEST\\dist\\arma3launcher.exe"

exePathNew = "C:\\Users\\M9-SD\\Documents\\Arma 3 - Scripts\\Anti-Profile-Wipe\\BUILD_TEST\\dist\\arma3launcher_m9-sd.exe"

# os.rename('changemyexe.py', 'exenamechanged.py')
try:
    os.rename(exePath, exePathNew)
except Exception as error:
    print(error)
print('done rename 1')

while os.path.exists(exePath):
    pass


exePath2 = "C:\\Users\\M9-SD\\Documents\\Arma 3 - Scripts\\Anti-Profile-Wipe\\BUILD_TEST\\dist\\arma3launcher_og.exe"

exePathNew2 = "C:\\Users\\M9-SD\\Documents\\Arma 3 - Scripts\\Anti-Profile-Wipe\\BUILD_TEST\\dist\\arma3launcher.exe"

# os.rename('changemyexe.py', 'exenamechanged.py')
try:
    os.rename(exePath2, exePathNew2)
except Exception as error:
    print(error)
print('done rename 2')

while os.path.exists(exePath2):
    pass

while not os.path.exists(exePathNew2):
    pass

launcher_process = subprocess.Popen(exePathNew2)
print('done launching')

exePath3 = "C:\\Users\\M9-SD\\Documents\\Arma 3 - Scripts\\Anti-Profile-Wipe\\BUILD_TEST\\dist\\arma3launcher.exe"

exePathNew3 = "C:\\Users\\M9-SD\\Documents\\Arma 3 - Scripts\\Anti-Profile-Wipe\\BUILD_TEST\\dist\\arma3launcher_og.exe"

# os.rename('changemyexe.py', 'exenamechanged.py')
try:
    os.rename(exePath3, exePathNew3)
except Exception as error:
    print(error)
print('done rename 3')

while os.path.exists(exePath3):
    pass

while not os.path.exists(exePathNew3):
    pass


exePath4 = "C:\\Users\\M9-SD\\Documents\\Arma 3 - Scripts\\Anti-Profile-Wipe\\BUILD_TEST\\dist\\arma3launcher_m9-sd.exe"

exePathNew4 = "C:\\Users\\M9-SD\\Documents\\Arma 3 - Scripts\\Anti-Profile-Wipe\\BUILD_TEST\\dist\\arma3launcher.exe"

# os.rename('changemyexe.py', 'exenamechanged.py')
try:
    os.rename(exePath4, exePathNew4)
except Exception as error:
    print(error)
print('done rename 4')

input()
"""


def getFileDescriptor(file):
    # Open the file using its path:
    with open(file, 'rb') as f:
        # Get the file descriptor:
        fd = f.fileno()
    return fd


mainFileNamePath = "C:\\Users\\M9-SD\\Documents\\Arma 3 - Scripts\\Anti-Profile-Wipe\\BUILD_TEST\\dist\\arma3launcher.exe"

customFileDescriptor = getFileDescriptor(mainFileNamePath)
print(f"{customFileDescriptor=}")

originalFileNamePath = "C:\\Users\\M9-SD\\Documents\\Arma 3 - Scripts\\Anti-Profile-Wipe\\BUILD_TEST\\dist\\Launcher\\arma3launcher.og"

originalFileDescriptor = getFileDescriptor(originalFileNamePath)
print(f"{originalFileDescriptor=}")

customFileNamePath = "C:\\Users\\M9-SD\\Documents\\Arma 3 - Scripts\\Anti-Profile-Wipe\\BUILD_TEST\\dist\\Launcher\\arma3launcher.m9sd"

# Move custom exe to launcher folder

try:
    os.rename(mainFileNamePath, customFileNamePath)
    print("Moved custom exe to launcher folder")
except Exception as error:
    print(error)

if getFileDescriptor(customFileNamePath) == customFileDescriptor:
    print("custom balls")
else:
    print("no balls")

# Move the original exe to the main folder

try:
    os.rename(originalFileNamePath, mainFileNamePath)
    print("Moved original exe to main folder")
except Exception as error:
    print(error)

if getFileDescriptor(mainFileNamePath) == originalFileDescriptor:
    print("custom balls 2")
else:
    print("no balls 2")

# Run the original exe

# subprocess.call(['cmd', '/c', mainFileNamePath], shell=True)

input()

# Launch a new command prompt window and run the original exe
# subprocess.call(['start', 'cmd', '/c', mainFileNamePath], shell=True)


def runLauncher():
    global mainFileNamePath
    os.system(f'"{mainFileNamePath}"')


"""
thrd = Thread(
    # group=None,
    target=runLauncher,
    # name=None,
    args=(),
    # kwargs={},
)
independent = True
thrd.daemon = not independent
thrd.start()
"""


def runReset():
    global mainFileNamePath
    global originalFileNamePath
    global customFileNamePath
    # Move the original exe back to the launcher folder
    sleep(1)
    try:
        os.rename(mainFileNamePath, originalFileNamePath)
        print("Moved original exe back to launcher folder")
    except Exception as error:
        print(error)

    # Move the custom exe back to the main folder

    try:
        os.rename(customFileNamePath, mainFileNamePath)
        print("Moved custom exe back to main folder")
    except Exception as error:
        print(error)


thrd = Thread(
    # group=None,
    target=runReset,
    # name=None,
    args=(),
    # kwargs={},
)
independent = True
thrd.daemon = not independent
thrd.start()


print("running og exe")
os.system(f'"{mainFileNamePath}"')
print("ran the original exe")


# Sanity check
print("script done")

input()
