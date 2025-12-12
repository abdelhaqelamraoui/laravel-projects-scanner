import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from datetime import datetime

from scanner import scan_for_laravel_projects
from utils import open_folder, open_in_vscode


class LaravelScannerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Laravel Projects Scanner")
        self.geometry("800x500")

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

        # Create scrollable frame for results
        results_frame = tk.Frame(self)
        results_frame.pack(pady=5, fill=tk.BOTH, expand=True)
        
        # Canvas and scrollbar for scrolling
        self.results_canvas = tk.Canvas(results_frame)
        scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=self.results_canvas.yview)
        self.results_scrollable_frame = tk.Frame(self.results_canvas)
        
        def on_frame_configure(event):
            self.results_canvas.configure(scrollregion=self.results_canvas.bbox("all"))
        
        self.results_scrollable_frame.bind("<Configure>", on_frame_configure)
        
        self.canvas_window = self.results_canvas.create_window((0, 0), window=self.results_scrollable_frame, anchor="nw")
        self.results_canvas.configure(yscrollcommand=scrollbar.set)
        
        # Bind mouse wheel scrolling
        def _on_mousewheel(event):
            self.results_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        self.results_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Update canvas width when window resizes
        def configure_canvas_width(event):
            canvas_width = event.width
            self.results_canvas.itemconfig(self.canvas_window, width=canvas_width)
        self.results_canvas.bind('<Configure>', configure_canvas_width)
        
        self.results_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Store project rows for selection
        self.project_rows = []

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

        # Clear previous results
        for widget in self.results_scrollable_frame.winfo_children():
            widget.destroy()
        self.project_rows = []
        
        self.status_label.config(text="Scanning...")
        self.scan_btn.config(state=tk.DISABLED)

        # Run scan in another thread to avoid freezing UI
        threading.Thread(target=self.scan_and_display,
                         args=(root_dir,), daemon=True).start()

    def scan_and_display(self, root_dir):
        projects = scan_for_laravel_projects(root_dir)
        
        # Clear previous results in UI thread
        self.after(0, self.clear_results)
        
        # Create rows for each project (fix lambda closure issue)
        def add_all_projects():
            for proj in projects:
                self.add_project_row(proj)
        
        self.after(0, add_all_projects)

        # Save results to file
        self.save_results_to_file(projects, root_dir)

        self.after(0, lambda: self.scan_btn.config(state=tk.NORMAL))
    
    def clear_results(self):
        """Clear all project rows"""
        for widget in self.results_scrollable_frame.winfo_children():
            widget.destroy()
        self.project_rows = []
    
    def add_project_row(self, project_path):
        """Add a row with a VSCode button and project path"""
        row_frame = tk.Frame(self.results_scrollable_frame, relief=tk.RAISED, borderwidth=1)
        row_frame.pack(fill=tk.X, padx=2, pady=1)
        
        # VSCode button
        vscode_btn = tk.Button(
            row_frame, 
            text="Open in VSCode", 
            command=lambda p=project_path: open_in_vscode(p),
            width=15
        )
        vscode_btn.pack(side=tk.LEFT, padx=5, pady=2)
        
        # Project path label (selectable)
        path_label = tk.Label(
            row_frame, 
            text=project_path, 
            anchor="w",
            cursor="hand2"
        )
        path_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        path_label.bind("<Button-1>", lambda e, p=project_path: self.select_project(p))
        path_label.bind("<Double-1>", lambda e, p=project_path: open_folder(p))
        
        # Store row reference
        self.project_rows.append({
            'frame': row_frame,
            'path': project_path,
            'selected': False
        })
        
        # Update canvas scroll region
        self.results_canvas.update_idletasks()
        self.results_canvas.configure(scrollregion=self.results_canvas.bbox("all"))
    
    def select_project(self, project_path):
        """Select/deselect a project row"""
        for row in self.project_rows:
            if row['path'] == project_path:
                row['selected'] = not row['selected']
                if row['selected']:
                    row['frame'].config(bg='lightblue')
                else:
                    row['frame'].config(bg='SystemButtonFace')
                break

    def save_results_to_file(self, projects, root_dir):
        """Save the scan results to a text file"""
        filename = "laravel_projects.txt"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"Laravel Projects Scan Results\n")
                f.write(f"Scan Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Scanned Directory: {root_dir}\n")
                f.write(f"Total Projects Found: {len(projects)}\n")
                f.write(f"{'='*80}\n\n")
                
                for proj in projects:
                    f.write(f"{proj}\n")
            
            # Update status to show file was saved
            self.after(0, lambda: self.status_label.config(
                text=f"Found {len(projects)} Laravel projects - Saved to {filename}"))
        except Exception as e:
            # Update status to show error
            self.after(0, lambda: self.status_label.config(
                text=f"Found {len(projects)} Laravel projects - Error saving file: {str(e)}"))

