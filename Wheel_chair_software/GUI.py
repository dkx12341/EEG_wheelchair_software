import tkinter as tk
from tkinter import Listbox, Scrollbar, Label
from PIL import Image, ImageTk

import cv2
import time

from main import Main



class GraphicalUserInterface:
    
    def __init__(self, root, controller:Main):


        self.set_head_window = None
        self.set_follow_window = None
        self.controller = controller
        

        self.speed_label = None
        self.turn_label = None

        self.speed_delta = 20
        self.turn_delta = 5

        self.open_menu_window(root, controller)
        
    ###################################################################################
    #                       Window methods                                            #
    ###################################################################################
   
    def open_menu_window(self, root, controller:Main):
        self.root = root
        self.root.title("Electric Wheelchair Controller")
        self.root.geometry("1200x1000")

        #self.face_analyzer = controller.face_analyzer
       

        # Frame for listbox and scrollbar
        frame = tk.Frame(self.root)
        frame.grid(row=0, column=1, columnspan=10, padx=10, pady=10)
        
        # Scrollbar
        scrollbar = Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
     

        # Listbox to display logs
        self.log_list = Listbox(frame, width=60, height=20, yscrollcommand=scrollbar.set)
        self.log_list.pack()
        scrollbar.config(command=self.log_list.yview)

        btn_steering_btn =tk.Button(self.root, text=f"Button steering", command=lambda: (self.add_log(f"Button steering active",self.log_list), self.start_button_steering()),width=15, height=4)
        btn_steering_btn.grid(row=1, column=1, padx=5, pady=5)

        head_steering_btn =tk.Button(self.root, text=f"Head steering", command=lambda: (self.add_log(f"head steering active",self.log_list), self.start_head_steering()),width=15, height=4)
        head_steering_btn.grid(row=2, column=1, padx=5, pady=5)

        EEG_steering_btn =tk.Button(self.root, text=f"EEG steering", command=lambda: (self.add_log(f"eeg steering active",self.log_list), self.start_EEG_steering()),width=15, height=4)
        EEG_steering_btn.grid(row=3, column=1, padx=5, pady=5)

        follow_btn =tk.Button(self.root, text=f"Following silhouette", command=lambda: (self.add_log(f"following silhouette active",self.log_list), self.start_following()),width=15, height=4)
        follow_btn.grid(row=1, column=2, padx=5, pady=5)     
        
    def open_button_steering_window(self):
        self.set_button_steering_window = tk.Toplevel(self.root)
        self.set_button_steering_window.title("Button Steering")
        self.set_button_steering_window.geometry("800x600")
        self.set_button_steering_window.protocol("WM_DELETE_WINDOW", lambda: self.close_window(self.set_button_steering_window))
        self.bind_steering_keys(self.set_button_steering_window)
        
        self.speed_label = tk.Label(self.set_button_steering_window, text=f"Speed value: {self.controller.speed}", font=("Arial", 10))
        self.speed_label.grid(row=1, column=1, padx=5, pady=5)

        self.turn_label = tk.Label(self.set_button_steering_window, text=f"Turn value: {self.controller.turn}", font=("Arial", 10))
        self.turn_label.grid(row=2, column=1, padx=5, pady=5)
        
        # buttons
        speed_up_btn = self.speed_button(self.speed_delta,self.set_button_steering_window)
        speed_up_btn.grid(row=1, column=3, padx=5, pady=5)
        speed_dwn_btn = self.speed_button(-self.speed_delta,self.set_button_steering_window)
        speed_dwn_btn.grid(row=3, column=3, padx=5, pady=5)
        turn_rt_btn = self.turn_button(self.turn_delta,self.set_button_steering_window)
        turn_rt_btn.grid(row=2, column=4, padx=5, pady=5)
        turn_lt_btn =self.turn_button(-self.turn_delta,self.set_button_steering_window)
        turn_lt_btn.grid(row=2, column=2, padx=5, pady=5)
        
        
        exit_btn = tk.Button(self.set_button_steering_window, text="Exit", command= lambda:(self.close_window(self.set_button_steering_window)),width=15, height=4)
        #exit_btn.pack()
        exit_btn.grid(row=4, column=3, padx=10, pady=10)
    

    def open_head_steering_window(self):
        self.set_head_window = tk.Toplevel(self.root)
        self.set_head_window.title("Head Steering")
        self.set_head_window.geometry("1200x1000")
        self.set_head_window.protocol("WM_DELETE_WINDOW", lambda: self.close_window(self.set_head_window))
        self.bind_steering_keys(self.set_head_window)

        self.speed_label = tk.Label(self.set_head_window, text=f"Speed value: {self.controller.speed}", font=("Arial", 10))
        self.speed_label.grid(row=1, column=1, padx=5, pady=5)

        self.turn_label = tk.Label(self.set_head_window, text=f"Turn value: {self.controller.turn}", font=("Arial", 10))
        self.turn_label.grid(row=2, column=1, padx=5, pady=5)

        # Video Frame Label
        self.head_video_label = tk.Label(self.set_head_window)
        self.head_video_label.grid(row=0, column=8,rowspan=5, padx=10, pady=10)

        # Buttons
        speed_up_btn = self.speed_button(self.speed_delta, self.set_head_window)
        speed_up_btn.grid(row=1, column=3, padx=5, pady=5)

        speed_dwn_btn = self.speed_button(-self.speed_delta, self.set_head_window)
        speed_dwn_btn.grid(row=2, column=3, padx=5, pady=5)


        exit_btn = tk.Button(self.set_head_window, text="Exit",
                             command=lambda: self.close_window(self.set_head_window),
                             width=15, height=4)
        exit_btn.grid(row=4, column=3, padx=10, pady=10)

        self.update_video_frame(self.controller.face_analyzer, self.set_head_window, self.head_video_label)

    def open_follow_steering_window(self):
        self.set_follow_window = tk.Toplevel(self.root)
        self.set_follow_window.title("Silhouette following")
        self.set_follow_window.geometry("1200x1000")
        self.set_follow_window.protocol("WM_DELETE_WINDOW", lambda: self.close_window(self.set_follow_window))
        self.bind_steering_keys(self.set_follow_window)

        self.speed_label = tk.Label(self.set_follow_window, text=f"Speed value: {self.controller.speed}", font=("Arial", 10))
        self.speed_label.grid(row=1, column=1, padx=5, pady=5)

        self.turn_label = tk.Label(self.set_follow_window, text=f"Turn value: {self.controller.turn}", font=("Arial", 10))
        self.turn_label.grid(row=2, column=1, padx=5, pady=5)

        # Video Frame Label
        self.follow_video_label = tk.Label(self.set_follow_window)
        self.follow_video_label.grid(row=0, column=8,rowspan=5, padx=10, pady=10)

        # Buttons
        speed_up_btn = self.speed_button(self.speed_delta, self.set_follow_window)
        speed_up_btn.grid(row=1, column=3, padx=5, pady=5)

        speed_dwn_btn = self.speed_button(-self.speed_delta, self.set_follow_window)
        speed_dwn_btn.grid(row=2, column=3, padx=5, pady=5)


        exit_btn = tk.Button(self.set_follow_window, text="Exit",
                             command=lambda: self.close_window(self.set_follow_window),
                             width=15, height=4)
        exit_btn.grid(row=4, column=3, padx=10, pady=10)

        

        self.update_video_frame(self.controller.human_tracker, self.set_follow_window, self.follow_video_label)


    ###################################################################################
    #                       Tools                                                     #
    ###################################################################################

    def update_video_frame(self, video_frame_src, video_window, video_label):
        if video_window is None or not video_window.winfo_exists():
            return  # Window has been closed
        
        if video_frame_src.video is not None:
            try:
                # Convert frame from BGR to RGB
                frame = cv2.cvtColor(video_frame_src.video, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame)
                imgtk = ImageTk.PhotoImage(image=img)
                
                # Update label with the new image
                video_label.configure(image=imgtk)
                video_label.image = imgtk  # Keep a reference
                
            except Exception as e:
                print(f"Error updating video frame: {e}")
        
        self.update_steering_values()

        # Schedule the next frame update if window still exists
        if video_window.winfo_exists():
            video_window.after(10, lambda: self.update_video_frame(video_frame_src, video_window, video_label))


    def update_steering_values(self):
        self.speed_label.config(text = f"Speed value: {self.controller.speed}")
        self.turn_label.config(text = f"Turn value: {self.controller.turn}")
        
    def close_window(self,window):

        #stop wheelchair when closing window
        self.controller.change_speed(-self.controller.speed)
        self.controller.change_turn(-self.controller.turn)

        self.controller.stop_thread()
        window.destroy()

    def add_log(self, message, list):
        list.insert(tk.END, message)
        list.yview(tk.END)  # Auto-scroll to the latest log

    def speed_button(self, d_speed, parent_window):
        button_txt = "Speed: "
        if d_speed < 0:
            button_txt += ("-" + str(d_speed))
        else:
            button_txt += ("+" + str(d_speed))


        return tk.Button(parent_window, text=button_txt,
                                 command=lambda: (self.controller.change_speed(d_speed), self.update_steering_values()),
                                 width=15, height=4)


    def turn_button(self, d_turn,parent_window):
        button_txt = "Turn: "
        if d_turn < 0:
            button_txt += ("-" + str(d_turn))
        else:
            button_txt += ("+" + str(d_turn))


        return tk.Button(parent_window, text=button_txt,
                                 command=lambda: (self.controller.change_turn(d_turn), self.update_steering_values()),
                                 width=15, height=4)

    def bind_steering_keys(self, window):
        for key in ['w', 'W']:
            window.bind(f"<{key}>", lambda event: self.controller.change_speed(self.speed_delta) or self.update_steering_values())
        for key in ['s', 'S']:
            window.bind(f"<{key}>", lambda event: self.controller.change_speed(-self.speed_delta) or self.update_steering_values())
        for key in ['a', 'A']:
            window.bind(f"<{key}>", lambda event: self.controller.change_turn(-self.turn_delta) or self.update_steering_values())
        for key in ['d', 'D']:
            window.bind(f"<{key}>", lambda event: self.controller.change_turn(self.turn_delta) or self.update_steering_values())




    def start_button_steering(self):
        
        self.controller.start_new_thread(self.controller.button_steering)
        self.open_button_steering_window() 

    def start_head_steering(self):
        
        self.controller.start_new_thread(self.controller.head_steering)
        self.open_head_steering_window()
      
    def start_EEG_steering(self):
        self.controller.start_new_thread(self.controller.EEG_steering)

    def start_following(self):

        self.open_follow_steering_window()
        self.controller.start_new_thread(self.controller.following)
        
        
        
        



if __name__ == "__main__":
    main = Main()
    root = tk.Tk()
    
    app = GraphicalUserInterface(root,main)
    root.mainloop()