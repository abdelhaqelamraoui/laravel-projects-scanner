import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox

from scanner import scan_for_laravel_projects
from utils import open_folder


class LaravelScannerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Laravel Projects Scanner")
        self.geometry("600x400")

        self.create_widgets()

    def create_widgets(self):
        self.path_label = tk.Label(self, text="Select folder to scan:")
        self.path_label.pack(pady=5)

        self.path_entry = tk.Entry(self, width=50)
        self.path_entry.pack(pady=5)

        self.browse_btn = tk.Button(
            self, text="Browse", command=self.browse_folder)
        self.browse_btn.pack(pady=5)

        self.scan_btn = tk.Button(self, text="Scan", command=self.start_scan)
        self.scan_btn.pack(pady=10)

        self.results_listbox = tk.Listbox(self, width=80, height=15)
        self.results_listbox.pack(pady=5)
        self.results_listbox.bind("<Double-1>", self.open_selected_project)

        self.status_label = tk.Label(self, text="")
        self.status_label.pack(pady=5)

    def browse_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, folder_selected)

    def start_scan(self):
        root_dir = self.path_entry.get()
        if not root_dir or not os.path.isdir(root_dir):
            messagebox.showerror("Error", "Please select a valid directory")
            return

        self.results_listbox.delete(0, tk.END)
        self.status_label.config(text="Scanning...")
        self.scan_btn.config(state=tk.DISABLED)

        # Run scan in another thread to avoid freezing UI
        threading.Thread(target=self.scan_and_display,
                         args=(root_dir,), daemon=True).start()

    def scan_and_display(self, root_dir):
        projects = scan_for_laravel_projects(root_dir)
        self.results_listbox.delete(0, tk.END)

        for proj in projects:
            self.results_listbox.insert(tk.END, proj)

        self.status_label.config(
            text=f"Found {len(projects)} Laravel projects")
        self.scan_btn.config(state=tk.NORMAL)

    def open_selected_project(self, event):
        selected_index = self.results_listbox.curselection()
        if selected_index:
            path = self.results_listbox.get(selected_index)
            open_folder(path)
            path = self.results_listbox.get(selected_index)
            open_folder(path)
            open_folder(path)
