from tkinter import Tk, Toplevel, Label, Button, filedialog, Frame, ttk, messagebox
from PIL import Image, ImageTk
import os
import shutil
import winreg
import ctypes as ct

# allow this script to be called from any folder

os.chdir(os.path.dirname(__file__))

# define this script with a new app ID for custom icon:

myappid = 'M9-SD.A3-Auto-Backup.Installer.1-0-0'
ct.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)


class App(Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("Image and Text Display")

        # create a label for the image
        self.image_label = Label(self)
        self.image_label.grid(row=0, column=0, padx=5, pady=5)

        # create a label for the text
        self.text_label = Label(self, text="Initializing...")
        self.text_label.grid(row=0, column=1, padx=5, pady=5)

        # create a progress bar
        self.progress_bar = ttk.Progressbar(
            self, orient="horizontal", mode="determinate")
        self.progress_bar.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

        # load the image
        self.image = Image.open("M9-SD_Logo.png")
        self.image = self.image.resize((200, 200))
        self.photo = ImageTk.PhotoImage(self.image)
        self.image_label.configure(image=self.photo)

        # update the text label and progress bar
        self.update_display("Stage 1", 10)

    def update_display(self, text, progress):
        self.text_label.configure(text=text)
        self.progress_bar.configure(value=progress)
        self.update()


# create the GUI
if False:
    app = App()
    app.mainloop()

#######################################################################################################


def dark_title_bar(window):
    """
    FROM:
    https://gist.github.com/Olikonsti/879edbf69b801d8519bf25e804cec0aa
    MORE INFO:
    https://docs.microsoft.com/en-us/windows/win32/api/dwmapi/ne-dwmapi-dwmwindowattribute
    """
    window.update()
    DWMWA_USE_IMMERSIVE_DARK_MODE = 20
    set_window_attribute = ct.windll.dwmapi.DwmSetWindowAttribute
    get_parent = ct.windll.user32.GetParent
    hwnd = get_parent(window.winfo_id())
    rendering_policy = DWMWA_USE_IMMERSIVE_DARK_MODE
    value = 2
    value = ct.c_int(value)
    set_window_attribute(hwnd, rendering_policy,
                         ct.byref(value), ct.sizeof(value))


def replaceExeTest(a3folder):
    print(a3folder)
    a3launcherpath = a3folder + "\\" + "arma3launcher.exe"
    print(a3launcherpath)
    a3launcherpath_renamed = a3folder + "\\" + "arma3launcher_og.exe"
    print(a3launcherpath_renamed)
    if not os.path.exists(a3launcherpath_renamed):
        os.rename(a3launcherpath, a3launcherpath_renamed)
        print("os.rename(a3launcherpath, a3launcherpath_renamed)")
    if os.path.exists(a3launcherpath):
        os.remove(a3launcherpath)
        print("os.remove(a3launcherpath)")
    shutil.copy2("A3-Profile-Backup-Launcher.exe", a3launcherpath)
    print("replaced")


def startWizard(a3folder):
    pass
    print("starting wizard...")

    replaceExeTest(a3folder)


def checkAndInstall():
    def find_arma3_path():
        # open the Arma 3 key in the Windows registry
        try:
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Wow6432Node\bohemia interactive\arma 3")
        except OSError:
            # key not found
            return None

        # get the installation directory value
        try:
            path = winreg.QueryValueEx(key, "main")[0]
        except OSError:
            # value not found
            return None

        return path

    # function to display the installation directory selection dialog
    def select_install_dir(parentWindow):
        # root = Tk()
        # root.withdraw()
        # root.iconbitmap("M9-SD_icon2.ico")
        windowTitle = "A3 Auto Backup Installer | Please select Arma 3’s installation directory."
        # root.title(windowTitle)
        path = filedialog.askdirectory(
            title=windowTitle, mustexist=True, parent=parentWindow)
        # root.destroy()
        return path

    # attempt to find the Arma 3 installation directory using the registry
    path = find_arma3_path()

    # if the installation directory is not found, prompt the user to select it manually or retry the search

    def pathErrorDialogue():
        # create a custom dialog box with a message and two buttons

        # root = Tk()
        # root.iconbitmap("M9-SD_icon2.ico")
        # root.withdraw()

        # dialog = Toplevel(root)
        dialog = Tk()

        def quit_me():
            print('quit')
            dialog.quit()
            dialog.destroy()
            print("quit")
            # global path
            # path=True

        dialog.protocol("WM_DELETE_WINDOW", quit_me)
        dialog.resizable(False, False)
        dialog.configure(bg="#191919")
        dialog.iconbitmap("M9-SD_icon2.ico")
        dialog.title("A3 Auto Backup Installer | Error")
        dark_title_bar(dialog)

        # Get the screen width and height

        # screen_width = root.winfo_screenwidth()
        # screen_height = root.winfo_screenheight()

        screen_width = dialog.winfo_screenwidth()
        screen_height = dialog.winfo_screenheight()

        print(F"{screen_width=}")
        print(F"{screen_height=}")

        xAdj = (135 / 2560) * screen_width
        yAdj = (120 / 1440) * screen_height

        # Calculate the x and y coordinates for the Toplevel window
        x = int((screen_width / 2) - (dialog.winfo_reqwidth() / 2) - xAdj)
        y = int((screen_height / 2) - (dialog.winfo_reqheight() / 2 + yAdj))

        # Set the Toplevel window's position
        dialog.geometry("+{}+{}".format(x, y))

        # Display the Toplevel window
        # dialog.deiconify()

        Label(dialog, font=("Helvetica", 21), text="INSTALLER ERROR",
              bg="#191919", fg="#fd462d").pack(padx=0, pady=(20, 20))

        border_color = Frame(dialog, background="#2b2b2b")
        border_color.pack(padx=25, pady=0)

        Label(border_color, font=("Segoe UI", 11), relief="solid", highlightcolor="red", highlightbackground="red", bg="#202020", fg="#FFFFFF", bd=0,
              text="\n     Could not locate Arma 3, verify it's installed and try again.     \n     Otherwise, manually select Arma 3's installation directory.     \n").pack(padx=1, pady=1)

        # create a style for the buttons
        # style = ttk.Style()
        # style.configure("test.TButton", activebackground='#666666', bg='#333333', fg="#FFFFFF")

        # function to retry the search when the retry button is clicked

        def retry():
            global path
            dialog.destroy()
            path = find_arma3_path()
            if path:
                dialog.quit()
                # start installer gui
                startWizard(path)
            else:
                dialog.quit()
                # re-open error gui
                pathErrorDialogue()

        # function to select the installation directory when the select button is clicked
        def select():
            global path
            # dialog.destroy()
            path = select_install_dir(dialog)
            print(path)
            if path and os.path.isfile(os.path.join(path, "arma3launcher.exe")):
                print("good path")
                dialog.destroy()
                dialog.quit()
                # start installer gui
                startWizard(path)
            else:
                print("bad path")
                if path == "":
                    # user canceled manual directory selection
                    pass
                else:
                    # user selected an invalid directory
                    errorMessage = f"arma3launcher.exe not found in directory:\n\n{path}\n\nPlease try again."
                    messagebox.showerror(
                        parent=dialog, title="A3 Auto Backup Installer | Error", message=errorMessage)

                # root.quit()
                # re-open error gui
                # pathErrorDialogue()

        # bind the buttons to their respective functions
        # retry_button.config(command=retry)
        # select_button.config(command=select)

        def OnPressed_retry_button(event):
            retry_button.config(bg='#666666', fg='white')
            retry()

        def OnHover_retry_button(event):
            retry_button.config(bg='#454545', fg='white')

        def OnLeave_retry_button(event):
            retry_button.config(bg='#333333', fg='white')

        def OnPressed_select_button(event):
            select_button.config(bg='#666666', fg='white')
            select()

        def OnHover_select_button(event):
            select_button.config(bg='#454545', fg='white')

        def OnLeave_select_button(event):
            select_button.config(bg='#333333', fg='white')

        retryBtnBaseBd = Frame(dialog, background="#9b9b9b")
        retryBtnBaseBd.pack(side="left", padx=25, pady=(20, 25))

        selectBtnBaseBd = Frame(dialog, background="#9b9b9b")
        selectBtnBaseBd.pack(side="right", padx=25, pady=(20, 25))

        retry_button = Label(retryBtnBaseBd, font=(
            "Helvetica", 12), text='Retry Installer', bg='#333333', fg='white', relief='solid', bd=0.1)
        retry_button.bind('<Button-1>', OnPressed_retry_button)
        retry_button.bind('<Enter>', OnHover_retry_button)
        retry_button.bind('<Leave>', OnLeave_retry_button)
        retry_button.pack(padx=1, pady=1, ipadx=16, ipady=8)

        select_button = Label(selectBtnBaseBd, font=(
            "Helvetica", 12), text='Select Directory', bg='#333333', fg='white', relief='solid', bd=0.1)
        select_button.bind('<Button-1>', OnPressed_select_button)
        select_button.bind('<Enter>', OnHover_select_button)
        select_button.bind('<Leave>', OnLeave_select_button)
        select_button.pack(side="right", padx=1, pady=1, ipadx=16, ipady=8)

        dialog.mainloop()

    if not path or path is None:
        if path is None:
            print("null path")
        pathErrorDialogue()

    else:
        print("Arma 3 is installed at:", path)
        # start installer gui
        startWizard(path)


def main():
    # check if/where arma 3 is installed (& look for launcher executable)
    # if found, start main installer gui loop
    checkAndInstall()


if __name__ == '__main__':
    main()
