import tkinter as tk
from tkinter import Listbox, Scrollbar

class LogViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Log Viewer")
        self.root.geometry("800x600")

        # Frame for listbox and scrollbar
        frame = tk.Frame(self.root)
        frame.pack(pady=10)

        # Scrollbar
        scrollbar = Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Listbox to display logs
        self.log_list = Listbox(frame, width=100, height=20, yscrollcommand=scrollbar.set)
        self.log_list.pack()
        scrollbar.config(command=self.log_list.yview)

        # Buttons to add logs
        for i in range(1, 6):
            btn = tk.Button(self.root, text=f"Log {i}", command=lambda i=i: self.add_log(f"Log message {i}"))
            btn.pack()

    def add_log(self, message):
        self.log_list.insert(tk.END, message)
        self.log_list.yview(tk.END)  # Auto-scroll to the latest log

if __name__ == "__main__":
    root = tk.Tk()
    app = LogViewerApp(root)
    root.mainloop()
