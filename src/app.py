import tkinter as tk
from PIL import Image, ImageTk
import os
import ctypes
import pystray

SPI_SETDESKWALLPAPER = 20 #the code for setting the wallpaper
SPIF_UPDATEINIFILE = 0x01 #the code for updating the ini file
SPIF_SENDCHANGE = 0x02 #the code for sending a change

class Gui():

    def __init__(self):
        self.window = tk.Tk()
        self.image = Image.open("icon.png")
        self.menu = (
            pystray.MenuItem('Show', self.show_window),
            pystray.MenuItem('Quit', self.quit_window)
            )
        self.window.protocol('WM_DELETE_WINDOW', self.withdraw_window)
        self.withdraw_window()
        
        #set the tkinter icon
        self.window.iconphoto(False, tk.PhotoImage(file='icon.png'))
        self.window.title("Dall-E Background Generator")
        self.window.geometry("300x300")
        self.window.resizable(False, False)

        #create the image display widget
        self.image_display_widget = ImageDisplayWidget(self.window)
        self.image_display_widget.pack(fill=tk.BOTH, expand=True)
        #center the window
        self.window.eval('tk::PlaceWindow . center')
        


        
        print("GUI initialized!")
        self.window.mainloop()

    def quit_window(self):
        self.icon.stop()
        self.window.destroy()
        
    def show_window(self):
        self.icon.stop()
        self.window.protocol('WM_DELETE_WINDOW', self.withdraw_window)
        self.window.after(0, self.window.deiconify)

    def withdraw_window(self):
        self.window.withdraw()
        self.icon = pystray.Icon("name", self.image, "title", self.menu)
        self.icon.run()
    
class ImageDisplayWidget(tk.Frame):
    def __init__(self, parent, image_folder="./images", *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.image_folder = image_folder
        self.image_buttons = []


        self.load_images()
        self.create_widgets()

    def load_images(self):
        self.images = []
        for filename in os.listdir(self.image_folder):
            if filename.lower().endswith((".png", ".jpg", ".jpeg", ".gif")):
                image_path = os.path.join(self.image_folder, filename)
                image = Image.open(image_path)
                image.thumbnail((100, 100),Image.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                self.images.append((filename, photo))
                

    def create_widgets(self):
        for i, image_info in enumerate(self.images):
            filename, image = image_info
            if i % 2 == 0:
                row_frame = tk.Frame(self)
                row_frame.pack(side=tk.TOP, pady=5)

            button = tk.Button(row_frame, image=image, command=lambda f=filename: self.image_button_clicked(f))
            button.config(borderwidth=0, highlightthickness=0, relief=tk.FLAT)
            button.image = image  # Keep a reference to the image to prevent garbage collection
            button.pack(side=tk.LEFT, padx=5)

            if i % 2 == 1 or i == len(self.images) - 1:
                # Add a spacer for better layout
                spacer = tk.Label(row_frame, text="    ")
                spacer.pack(side=tk.RIGHT)

        # Adjust the frame height to accommodate the rows
        self.update_idletasks()
        widget_height = sum(frame.winfo_reqheight() for frame in self.winfo_children())
        self.config(height=widget_height)


    def image_button_clicked(self, filename):
        path = os.path.abspath(self.image_folder + "/" + filename)
        ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, path, SPIF_UPDATEINIFILE | SPIF_SENDCHANGE)


        




if __name__ in '__main__':
    Gui()