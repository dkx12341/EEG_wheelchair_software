import tkinter as tk
from tkinter import Listbox, Scrollbar, Label
from PIL import Image, ImageTk

import cv2
import time

from main import Main



class GraphicalUserInterface:
    
    def __init__(self, root, controller:Main):

        self.head_after_id = None
        self.set_head_window = None
        self.set_follow_window = None
        self.controller = controller
        self.curr_video_src = None
        self.curr_window_video_player = None

        self.open_menu_window(root, controller)
        
    ###################################################################################
    #                       Window methods                                            #
    ###################################################################################
   
    def open_menu_window(self, root, controller:Main):
        self.root = root
        self.root.title("Electric Wheelchair Controller")
        self.root.geometry("800x600")

        #self.face_analyzer = controller.face_analyzer
       

        ###################################################################################
        #                       screen layout                                             #
 
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
        self.set_speed_window = tk.Toplevel(self.root)
        self.set_speed_window.title("Button Steering")
        self.set_speed_window.geometry("800x600")
        


        ###################################################################################
        #                       screen layout                                             #


        # Frame for listbox and scrollbar
        frame_sec = tk.Frame(self.set_speed_window)
        frame_sec.grid(row=0, column=1, columnspan=10, padx=10, pady=10)

        
        # Scrollbar
        scrollbar = Scrollbar(frame_sec)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Listbox to display logs
        self.log_button_list = Listbox(frame_sec, width=50, height=10, yscrollcommand=scrollbar.set)
        self.log_button_list.pack()
        scrollbar.config(command=self.log_button_list.yview)
        
        # buttons
        speed_up_btn = tk.Button(self.set_speed_window, text=f"Speed:+20", command=lambda: (self.controller.change_speed(20) ,self.add_log(f"Speed: " + str(main.speed),self.log_button_list)),width=15, height=4)
        speed_up_btn.grid(row=1, column=3, padx=5, pady=5)
        speed_dwn_btn = tk.Button(self.set_speed_window, text=f"Speed:-20", command=lambda:(self.controller.change_speed(-20) ,self.add_log(f"Speed: " + str(main.speed),self.log_button_list)),width=15, height=4)
        speed_dwn_btn.grid(row=3, column=3, padx=5, pady=5)
        turn_rt_btn = tk.Button(self.set_speed_window, text=f"Right: 5", command=lambda: (self.controller.change_turn(5) ,self.add_log(f"Right:" + str(main.turn),self.log_button_list)),width=15, height=4)
        turn_rt_btn.grid(row=2, column=4, padx=5, pady=5)
        turn_lt_btn = tk.Button(self.set_speed_window, text=f"Left: 5", command=lambda: (self.controller.change_turn(-5) ,self.add_log(f"Left:" + str(main.turn),self.log_button_list)) ,width=15, height=4)
        turn_lt_btn.grid(row=2, column=2, padx=5, pady=5)
        
        
        exit_btn = tk.Button(self.set_speed_window, text="Exit", command= lambda:(self.controller.stop_thread(), self.set_speed_window.destroy()),width=15, height=4)
        #exit_btn.pack()
        exit_btn.grid(row=4, column=3, padx=10, pady=10)
    
    def open_head_steering_window(self):
        self.set_head_window = tk.Toplevel(self.root)
        self.set_head_window.title("Head Steering")
        self.set_head_window.geometry("1000x800")
        self.set_head_window.protocol("WM_DELETE_WINDOW", self.close_head_window)




        ###################################################################################
        #                       screen layout                                             #
 
        # Frame for listbox and scrollbar
        frame_sec = tk.Frame(self.set_head_window)
        frame_sec.grid(row=0, column=1, columnspan=5, padx=10, pady=10)

        # Scrollbar
        scrollbar = Scrollbar(frame_sec)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Listbox to display logs
        self.log_head_list = Listbox(frame_sec, width=50, height=10, yscrollcommand=scrollbar.set)
        self.log_head_list.pack()
        scrollbar.config(command=self.log_head_list.yview)

        # Buttons
        speed_up_btn = tk.Button(self.set_head_window, text="Speed:+20",
                                 command=lambda: (self.controller.change_speed(20),
                                                  self.add_log(f"Speed: {self.controller.speed}", self.log_head_list)),
                                 width=15, height=4)
        speed_up_btn.grid(row=1, column=3, padx=5, pady=5)

        speed_dwn_btn = tk.Button(self.set_head_window, text="Speed:-20",
                                  command=lambda: (self.controller.change_speed(-20),
                                                   self.add_log(f"Speed: {self.controller.speed}", self.log_head_list)),
                                  width=15, height=4)
        speed_dwn_btn.grid(row=3, column=3, padx=5, pady=5)

        exit_btn = tk.Button(self.set_head_window, text="Exit",
                             command=lambda: self.close_head_window(),
                             width=15, height=4)
        exit_btn.grid(row=4, column=3, padx=10, pady=10)

        # Video Frame Label
        self.head_video_label = tk.Label(self.set_head_window)
        self.head_video_label.grid(row=0, column=8, padx=10, pady=10)

        # Start updating the video
        #self.curr_window_video_player = self.set_head_window
        #self.curr_video_src = self.controller.face_analyzer.video 

        if self.head_after_id:
            self.set_head_window.after_cancel(self.head_after_id)
            self.head_after_id = None


        self.update_head_frame()

    ###################################################################################
    #                       Tools                                                     #
    ###################################################################################

    def update_head_frame(self):
            if self.controller.face_analyzer.video is not None:
           #if video is not None:
                frame = self.controller.face_analyzer.video  # Get the frame from the controller
                
                # Convert frame from BGR to RGB
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame)
                imgtk = ImageTk.PhotoImage(image=img)

                if self.set_head_window and self.set_head_window.winfo_exists():
                # Update label with the new image
                    self.head_video_label.configure(image=imgtk)
                    self.head_video_label.image = imgtk  


            # Schedule the next frame update
            self.head_after_id = self.set_head_window.after(10, self.update_head_frame)
            #self.set_head_window.after(10, self.update_head_frame)

    def close_head_window(self):
        if self.head_after_id:
            self.set_head_window.after_cancel(self.head_after_id)
            self.head_after_id = None
        self.controller.stop_thread()
        self.set_head_window.destroy()


    def add_log(self, message, list):
        list.insert(tk.END, message)
        list.yview(tk.END)  # Auto-scroll to the latest log

    def start_button_steering(self):
        
        self.controller.start_new_thread(self.controller.button_steering)
        self.open_button_steering_window() 

    def start_head_steering(self):
        self.open_head_steering_window()
        
        self.controller.start_new_thread(self.controller.head_steering)
      
    def start_EEG_steering(self):
        self.controller.start_new_thread(self.controller.EEG_steering)

    def start_following(self):

        self.open_silhouette_following_window()
        self.controller.start_new_thread(self.controller.following)
        
        
        
        



if __name__ == "__main__":
    main = Main()
    root = tk.Tk()
    
    app = GraphicalUserInterface(root,main)
    root.mainloop()