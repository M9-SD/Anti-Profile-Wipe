"""
    This script gets packed into an exe and replaces the default Arma 3 launcher executable.
"""

# Import dependencies:

import os
import datetime
import winreg
import subprocess
from send2trash import send2trash as recycle
from win10toast import ToastNotifier
from time import sleep
from threading import Thread

# CONFIGURE SETTINGS:

SETTING_MAX_BACKUPS = 5  # Oldest backup will be deleted after this number is reached
# TODO: Pull settings from programData config

# Define functions:


def getArma3Location():
    # Open the Arma 3 key in the Windows registry:
    path = None
    try:
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Wow6432Node\bohemia interactive\arma 3")
    except OSError:
        # key not found
        return None
    # Get the installation directory value:
    try:
        path = winreg.QueryValueEx(key, "main")[0]
    except OSError:
        # value not found
        return None
    # TODO: If path is none, try using config entry
    return path


def createFolder(folder_path):
    if not os.path.exists(folder_path):
        os.mkdir(folder_path)


def countFolders(path):
    count = 0
    for name in os.listdir(path):
        if os.path.isdir(os.path.join(path, name)):
            count += 1
    return count


def createUniqueFolderName(backupFolder_auto):
    # Construct folder name from precise date/time:
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y-%m-%d @ %H.%M.%S.%f")[:-3]
    am_pm = now.strftime("%p")
    timestamp = timestamp + " " + am_pm
    folderName = f"Arma 3 Profile Backup [{timestamp}]"
    print(f"{folderName=}")
    return folderName


def findOldestFolder(path):
    oldest_folder = None
    oldest_time = float('inf')
    # Iterate through folders in superficial directory:
    for dirname in os.listdir(path):
        if os.path.isdir(os.path.join(path, dirname)):
            # Compare date/time last modified:
            modified_time = os.path.getmtime(os.path.join(path, dirname))
            if modified_time < oldest_time:
                oldest_time = modified_time
                oldest_folder = dirname
    return oldest_folder


def deleteOldestBackup(backupFolder_auto):
    global expiredBackup
    expiredBackup = findOldestFolder(backupFolder_auto)
    expiredBackupPath = f"{backupFolder_auto}\\{expiredBackup}"
    if os.path.exists(expiredBackupPath):
        # Use send2trash package to bypass os.remove() permission error:
        recycle(expiredBackupPath)
        global backupExpired
        backupExpired = True


def cleanBackupFolder(backupFolder_auto):
    # Check if over max backup count and delete oldest:
    folderCount = countFolders(backupFolder_auto)
    print(f"{folderCount=}")
    print(f"{SETTING_MAX_BACKUPS=}")
    if folderCount < SETTING_MAX_BACKUPS or folderCount == 0:
        return
    deleteOldestBackup(backupFolder_auto)


def createBackupDirectory():
    # Create backup folders in user documents:
    userFolder = os.path.expanduser('~')
    documentsFolder = f"{userFolder}\\Documents"
    if not os.path.exists(documentsFolder):
        return
    print(f"{documentsFolder=}")
    backupFolder = f"{documentsFolder}\\Arma 3 - Profile Backups"
    createFolder(backupFolder)
    print(f"{backupFolder=}")
    backupFolder_auto = f"{backupFolder}\\Automatic"
    createFolder(backupFolder_auto)
    print(f"{backupFolder_auto=}")
    backupFolder_manual = f"{backupFolder}\\Manual"
    createFolder(backupFolder_manual)
    print(f"{backupFolder_manual=}")
    return (userFolder, documentsFolder, backupFolder, backupFolder_auto, backupFolder_manual)


def roboCopy(source, destination):  # Cannot use xcopy due to file path length limit
    # Define the robocopy command with the desired flags:
    command = ["robocopy", source, destination, "/e",  # /copy:ALL requires "Manage Auditing" user right
               "/copy:DAT", "/dcopy:T", "/r:1", "/w:1", "/log:profileBackupLog.txt"]  # Debug log
    # Execute the command using subprocess.run(), without showing the cmd window:
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    subprocess.run(command, capture_output=True,
                   creationflags=subprocess.CREATE_NO_WINDOW, startupinfo=startupinfo)


def backupProfiles(documentsFolder, backupFolder_auto):
    # Create a unique folder name with timestamp:
    global createdBackup
    createdBackup = createUniqueFolderName(backupFolder_auto)
    newBackupFolder = f"{backupFolder_auto}\\{createdBackup}"
    # Copy profiles to new backup folder:
    dP = "Arma 3"  # Default profile
    cP = "Arma 3 - Other Profiles"  # Custom profiles
    # Use windows command line to bypass shutil permissionError:
    roboCopy(f"{documentsFolder}\\{dP}", f"{newBackupFolder}\\{dP}")
    roboCopy(f"{documentsFolder}\\{cP}", f"{newBackupFolder}\\{cP}")
    global backupCreated
    backupCreated = True


def getUserName():
    # Use windows command line to retrieve the current user
    result = subprocess.run(
        ['cmd', '/c', 'echo', '%USERNAME%'], capture_output=True, text=True)
    # Extract username from output
    username = result.stdout.strip()
    print(f"{username=}")
    return username


def getUserSID():
    # Retrive current user
    username = getUserName()
    # Insert user into command string
    command = f'wmic useraccount where name="{username}" get sid'
    # Run cmd and extract UserSID for recycling bin path
    result = subprocess.run(command, capture_output=True, text=True)
    print(f"{result}")
    if result.returncode == 0:
        output = result.stdout.strip()
        print("Output:", output)
    else:
        print("Error:", result.stderr.strip())
    return output


def getFileDescriptor(file):
    # Open the file using its path:
    with open(file, 'rb') as f:
        # Get the file descriptor:
        fd = f.fileno()
    return fd


def runLauncherReset():
    global A3_normalLauncherPath
    global A3_defaultLauncherTempPath
    global A3_customLauncherTempPath
    # Move the original exe back to the launcher folder:
    sleep(1)  # May need to adjust or wait for program exit...
    try:
        os.rename(A3_normalLauncherPath, A3_defaultLauncherTempPath)
        print("Moved original exe back to launcher folder")
    except Exception as error:
        print(error)
    # Move the custom exe back to the main folder:
    try:
        os.rename(A3_customLauncherTempPath, A3_normalLauncherPath)
        print("Moved custom exe back to main folder")
    except Exception as error:
        print(error)


def launcherHotPotato():
    """
        Arma 3 Launcher only initializes its settings if the exe is named exactly right,
        so the launcherHotPotato() function will swap the exe's with a bit of tomfoolery.
        During this switcharoo maneuver, the defauly launcher will start. After that, the
        backup process will continue to execute and notify the user of changes to backups.
    """
    # First, figure out where Arma 3 is installed:
    A3_directory = getArma3Location()
    # Define the folder(s) that will be used:
    A3_launcherFolder = f"{A3_directory}\\Launcher"
    # Define the file paths to be used:
    global A3_normalLauncherPath
    global A3_customLauncherTempPath
    global A3_defaultLauncherTempPath
    A3_normalLauncherPath = f"{A3_directory}\\arma3launcher.exe"
    A3_customLauncherTempPath = f"{A3_launcherFolder}\\arma3launcher.m9sd"
    A3_defaultLauncherTempPath = f"{A3_launcherFolder}\\arma3launcher.og"
    # Move custom exe to launcher folder:
    try:
        os.rename(A3_normalLauncherPath, A3_customLauncherTempPath)
        print("Moved custom exe to launcher folder")
    except Exception as error:
        print(error)
    # Move the original exe to the main folder:
    try:
        os.rename(A3_defaultLauncherTempPath, A3_normalLauncherPath)
        print("Moved original exe to main folder")
    except Exception as error:
        print(error)
    # Run delayed exe reset thread to avoid mitosis:
    thrd = Thread(
        target=runLauncherReset,
        args=()
    )
    independent = True
    thrd.daemon = not independent
    thrd.start()
    # Spark up the actual launcher using cmd:
    os.system(f'"{A3_normalLauncherPath}"')


def startBackupProcess():
    # Initialize notification variables:
    global backupExpired
    global backupCreated
    backupExpired = False
    backupCreated = False
    global expiredBackup
    global createdBackup
    expiredBackup = ""
    createdBackup = ""
    # Create backup directory in user documents:
    userFolder, documentsFolder, backupFolder, backupFolder_auto, backupFolder_manual = createBackupDirectory()
    # Cleanup expired backups:
    cleanBackupFolder(backupFolder_auto)
    # Create new backup:
    backupProfiles(documentsFolder, backupFolder_auto)
    # Notify user of changes:
    if backupCreated or backupExpired:
        notificationTtl = "Arma 3 profile(s) backed up"
        notificationMsg = "\n"
        if backupCreated:
            # notificationMsg = notificationMsg + "Backup created: " + createdBackup + "\n\n" // Character limited
            # Shortened message:
            notificationMsg = notificationMsg + \
                "1 backup created (documents folder)." + "\n"
        if backupExpired:
            notificationMsg = notificationMsg + \
                "1 backup expired (recycling bin)." + "\n"
        toaster = ToastNotifier()
        toaster.show_toast(title=notificationTtl,
                           msg=notificationMsg, duration=30, threaded=True)


def main():
    # Reconfigure current working directory:
    os.chdir(os.path.dirname(__file__))
    # Start backup process in parallel:
    thrd = Thread(
        target=startBackupProcess,
        args=()
    )
    independent = True
    thrd.daemon = not independent
    thrd.start()
    # Open default arma 3 launcher:
    launcherHotPotato()


if __name__ == "__main__":
    main()
    # input()
