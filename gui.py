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
        
        # Load and validate projects from file on startup
        self.after(100, self.load_and_validate_projects)

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

    def read_projects_from_file(self):
        """Read project paths from the file"""
        filename = "laravel_projects.txt"
        projects = []
        
        if not os.path.exists(filename):
            return projects
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            # Find the separator line and get paths after it
            separator_found = False
            for line in lines:
                line = line.strip()
                if separator_found and line:  # After separator and not empty
                    # Check if it's a valid path (not a header line)
                    # A valid path should not be all equals signs and should look like a path
                    if line and not line.startswith("=") and (os.path.sep in line or (len(line) > 2 and line[1] == ':')):
                        projects.append(line)
                elif line and all(c == '=' for c in line) and len(line) >= 10:  # Separator line (all equals, at least 10 chars)
                    separator_found = True
                    
        except Exception as e:
            print(f"Error reading file: {e}")
        
        return projects
    
    def validate_projects(self, projects):
        """Check which projects still exist and return only valid ones"""
        valid_projects = []
        for project_path in projects:
            if os.path.exists(project_path) and os.path.isdir(project_path):
                valid_projects.append(project_path)
        return valid_projects
    
    def update_file_with_projects(self, projects):
        """Update the file with only valid projects"""
        filename = "laravel_projects.txt"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"Laravel Projects Scan Results\n")
                f.write(f"Scan Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total Projects Found: {len(projects)}\n")
                f.write(f"{'='*80}\n\n")
                
                for proj in projects:
                    f.write(f"{proj}\n")
        except Exception as e:
            print(f"Error updating file: {e}")
    
    def load_and_validate_projects(self):
        """Load projects from file, validate them, and display"""
        self.status_label.config(text="Loading projects from file...")
        
        # Run in thread to avoid freezing UI
        def validate_and_display():
            projects = self.read_projects_from_file()
            valid_projects = self.validate_projects(projects)
            deleted_count = len(projects) - len(valid_projects)
            
            # Update file if some projects were deleted
            if deleted_count > 0:
                self.update_file_with_projects(valid_projects)
            
            # Display valid projects in UI
            self.after(0, self.clear_results)
            
            def display_projects():
                for proj in valid_projects:
                    self.add_project_row(proj)
                
                if deleted_count > 0:
                    self.status_label.config(
                        text=f"Loaded {len(valid_projects)} projects ({deleted_count} deleted projects removed)")
                else:
                    self.status_label.config(
                        text=f"Loaded {len(valid_projects)} projects from file")
            
            self.after(0, display_projects)
        
        threading.Thread(target=validate_and_display, daemon=True).start()
    
    def save_results_to_file(self, projects, root_dir):
        """Save the scan results to a text file"""
        filename = "laravel_projects.txt"
        
        try:
            # Read existing projects to merge
            existing_projects = self.read_projects_from_file()
            
            # Combine existing and new projects, removing duplicates
            all_projects = list(set(existing_projects + projects))
            all_projects.sort()  # Sort for consistency
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"Laravel Projects Scan Results\n")
                f.write(f"Scan Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Scanned Directory: {root_dir}\n")
                f.write(f"Total Projects Found: {len(all_projects)}\n")
                f.write(f"{'='*80}\n\n")
                
                for proj in all_projects:
                    f.write(f"{proj}\n")
            
            # Update status to show file was saved
            self.after(0, lambda: self.status_label.config(
                text=f"Found {len(projects)} new projects - Total: {len(all_projects)} - Saved to {filename}"))
        except Exception as e:
            # Update status to show error
            self.after(0, lambda: self.status_label.config(
                text=f"Found {len(projects)} Laravel projects - Error saving file: {str(e)}"))

