import tkinter as tk
from tkinter import Listbox, Scrollbar, Label
from main import Main

class GraphicalUserInterface:
    
    def __init__(self, root, controller:Main):
        self.root = root
        self.root.title("Electric Wheelchair Controller")
        self.root.geometry("800x600")

        # Frame for listbox and scrollbar
        frame = tk.Frame(self.root)
        frame.grid(row=0, column=1, columnspan=10, padx=10, pady=10)
        
        # Scrollbar
        scrollbar = Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.controller = controller
        # Listbox to display logs
        self.log_list = Listbox(frame, width=60, height=20, yscrollcommand=scrollbar.set)
        self.log_list.pack()
        scrollbar.config(command=self.log_list.yview)

        btn_steering_btn =tk.Button(self.root, text=f"Button steering", command=lambda: (self.add_log(f"Button steering active"), self.start_button_steering()),width=15, height=4)
        btn_steering_btn.grid(row=1, column=1, padx=5, pady=5)

        head_steering_btn =tk.Button(self.root, text=f"Head steering", command=lambda: (self.add_log(f"head steering active"), self.start_head_steering()),width=15, height=4)
        head_steering_btn.grid(row=2, column=1, padx=5, pady=5)

        EEG_steering_btn =tk.Button(self.root, text=f"EEG steering", command=lambda: (self.add_log(f"eeg steering active"), self.start_EEG_steering()),width=15, height=4)
        EEG_steering_btn.grid(row=3, column=1, padx=5, pady=5)
        
        # Buttons to add logs
        
    
    def add_log(self, message):
        self.log_list.insert(tk.END, message)
        self.log_list.yview(tk.END)  # Auto-scroll to the latest log

    def open_button_steering_window(self):
        self.set_speed_window = tk.Toplevel(self.root)
        self.set_speed_window.title("Button Steering")
        self.set_speed_window.geometry("800x600")
        
        # Frame for listbox and scrollbar
        frame_sec = tk.Frame(self.set_speed_window)
        frame_sec.grid(row=0, column=1, columnspan=10, padx=10, pady=10)

        
        # Scrollbar
        scrollbar = Scrollbar(frame_sec)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Listbox to display logs
        self.log_list = Listbox(frame_sec, width=50, height=10, yscrollcommand=scrollbar.set)
        self.log_list.pack()
        scrollbar.config(command=self.log_list.yview)
        
        # buttons
        speed_up_btn = tk.Button(self.set_speed_window, text=f"Speed:+20", command=lambda: (self.controller.change_speed(20) ,self.add_log(f"Speed: " + str(main.speed))),width=15, height=4)
        speed_up_btn.grid(row=1, column=3, padx=5, pady=5)
        speed_dwn_btn = tk.Button(self.set_speed_window, text=f"Speed:-20", command=lambda:(self.controller.change_speed(-20) ,self.add_log(f"Speed: " + str(main.speed))),width=15, height=4)
        speed_dwn_btn.grid(row=3, column=3, padx=5, pady=5)
        turn_rt_btn = tk.Button(self.set_speed_window, text=f"Right: 5", command=lambda: (self.controller.change_turn(5) ,self.add_log(f"Right:" + str(main.turn))),width=15, height=4)
        turn_rt_btn.grid(row=2, column=4, padx=5, pady=5)
        turn_lt_btn = tk.Button(self.set_speed_window, text=f"Left: 5", command=lambda: (self.controller.change_turn(-5) ,self.add_log(f"Left:" + str(main.turn))) ,width=15, height=4)
        turn_lt_btn.grid(row=2, column=2, padx=5, pady=5)
        
        
        exit_btn = tk.Button(self.set_speed_window, text="Exit", command= lambda:(self.controller.stop_thread(), self.set_speed_window.destroy()))
        #exit_btn.pack()
        exit_btn.grid(row=4, column=3, padx=10, pady=10)
    

    def open_head_steering_window(self):
        self.head_steering_window = tk.Toplevel(self.root)
        self.head_steering_window.title("Head steering")
        self.head_steering_window.geometry("800x600")
        
        # Frame for listbox and scrollbar
        frame_hd = tk.Frame(self.head_steering_window)
        frame_hd.grid(row=0, column=1, columnspan=3, padx=10, pady=10)

        
        # Scrollbar
        scrollbar = Scrollbar(frame_hd)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        
        # Listbox to display logs
        self.log_list = Listbox(frame_hd, width=50, height=10, yscrollcommand=scrollbar.set)
        self.log_list.pack()
        scrollbar.config(command=self.log_list.yview)
        
        # buttons

        exit_btn = tk.Button(self.head_steering_window, text="Exit", command= lambda:(self.controller.stop_thread(), self.head_steering_window.destroy()))
        #exit_btn.pack()
        exit_btn.grid(row=4, column=3, padx=10, pady=10)
        


    def start_button_steering(self):
        
        self.controller.start_new_thread(self.controller.button_steering)
        self.open_button_steering_window() 

    def start_head_steering(self):
        self.controller.start_new_thread(self.controller.head_steering)
        self.open_head_steering_window() 

    def start_EEG_steering(self):
        self.controller.start_new_thread(self.controller.EEG_steering)



if __name__ == "__main__":
    main = Main()
    root = tk.Tk()
    
    app = GraphicalUserInterface(root,main)
    root.mainloop()