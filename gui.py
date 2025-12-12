import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from datetime import datetime
import shutil

from scanner import scan_for_laravel_projects
from utils import open_folder, open_in_vscode, open_url


class LaravelScannerApp(tk.Tk):
    # Laravel & Material Design Color Palette
    LARAVEL_RED = "#FF2D20"
    LARAVEL_RED_DARK = "#E6291C"
    LARAVEL_RED_LIGHT = "#FF5A4F"
    MATERIAL_WHITE = "#FFFFFF"
    MATERIAL_GRAY_50 = "#FAFAFA"
    MATERIAL_GRAY_100 = "#F5F5F5"
    MATERIAL_GRAY_200 = "#EEEEEE"
    MATERIAL_GRAY_300 = "#E0E0E0"
    MATERIAL_GRAY_600 = "#757575"
    MATERIAL_GRAY_700 = "#616161"
    MATERIAL_GRAY_800 = "#424242"
    MATERIAL_GRAY_900 = "#212121"
    MATERIAL_BLUE = "#2196F3"
    MATERIAL_GREEN = "#4CAF50"
    MATERIAL_ORANGE = "#FF9800"
    
    def __init__(self):
        super().__init__()
        self.title("Laravel Projects Scanner")
        self.geometry("900x550")
        
        # Configure main window styling
        self.configure(bg=self.MATERIAL_GRAY_50)
        
        self.create_widgets()
        
        # Load saved folder path on startup
        self.load_saved_folder_path()
        
        # Load and validate projects from file on startup
        self.after(100, self.load_and_validate_projects)

    def create_widgets(self):
        # Header frame with Laravel red background (compact)
        header_frame = tk.Frame(self, bg=self.LARAVEL_RED, height=50)
        header_frame.pack(fill=tk.X, side=tk.TOP)
        header_frame.pack_propagate(False)
        
        # Title in header (compact)
        title_label = tk.Label(
            header_frame,
            text="Laravel Projects Scanner",
            font=("Segoe UI", 16, "bold"),
            bg=self.LARAVEL_RED,
            fg=self.MATERIAL_WHITE,
            pady=12
        )
        title_label.pack()
        
        # Main content frame (compact padding)
        content_frame = tk.Frame(self, bg=self.MATERIAL_GRAY_50)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
        
        # Input section with card-like appearance (compact)
        input_card = tk.Frame(content_frame, bg=self.MATERIAL_WHITE, relief=tk.FLAT)
        input_card.pack(fill=tk.X, pady=(0, 10))
        
        # Add padding inside card (compact)
        input_inner = tk.Frame(input_card, bg=self.MATERIAL_WHITE)
        input_inner.pack(fill=tk.X, padx=12, pady=12)
        
        self.path_label = tk.Label(
            input_inner,
            text="Select folder to scan:",
            font=("Segoe UI", 10),
            bg=self.MATERIAL_WHITE,
            fg=self.MATERIAL_GRAY_800,
            anchor="w"
        )
        self.path_label.pack(fill=tk.X, pady=(0, 6))

        # Entry field with Material Design styling (compact)
        entry_frame = tk.Frame(input_inner, bg=self.MATERIAL_WHITE)
        entry_frame.pack(fill=tk.X, pady=(0, 8))
        
        self.path_entry = tk.Entry(
            entry_frame,
            width=50,
            font=("Segoe UI", 9),
            bg=self.MATERIAL_GRAY_100,
            fg=self.MATERIAL_GRAY_900,
            relief=tk.FLAT,
            borderwidth=0,
            insertbackground=self.LARAVEL_RED
        )
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6, padx=(0, 8))
        
        # Material Design button style (compact, same height)
        self.browse_btn = self.create_material_button(
            entry_frame,
            text="Browse",
            command=self.browse_folder,
            bg_color=self.MATERIAL_GRAY_300,
            hover_color=self.MATERIAL_GRAY_200,
            height=32
        )
        self.browse_btn.pack(side=tk.LEFT)

        # Action buttons frame (compact)
        buttons_frame = tk.Frame(input_inner, bg=self.MATERIAL_WHITE)
        buttons_frame.pack(fill=tk.X, pady=(4, 0))
        
        self.scan_btn = self.create_material_button(
            buttons_frame,
            text="Scan Projects",
            command=self.start_scan,
            bg_color=self.LARAVEL_RED,
            hover_color=self.LARAVEL_RED_DARK,
            fg_color=self.MATERIAL_WHITE,
            font_size=10,
            height=32
        )
        self.scan_btn.pack(side=tk.LEFT, padx=(0, 8))
        
        # Button to remove vendor packages from selected projects (compact, same height)
        self.remove_vendor_btn = self.create_material_button(
            buttons_frame,
            text="Remove Vendor Packages",
            command=self.remove_vendor_packages,
            bg_color=self.MATERIAL_ORANGE,
            hover_color="#F57C00",
            fg_color=self.MATERIAL_WHITE,
            state=tk.DISABLED,
            height=32
        )
        self.remove_vendor_btn.pack(side=tk.LEFT)

        # Footer frame for status and credits (packed first to reserve space)
        footer_frame = tk.Frame(content_frame, bg=self.MATERIAL_GRAY_50, height=30)
        footer_frame.pack(side=tk.BOTTOM, fill=tk.X)
        footer_frame.pack_propagate(False)
        
        # Results section with card-like appearance (compact)
        # Use a container frame to properly manage space
        results_container = tk.Frame(content_frame, bg=self.MATERIAL_GRAY_50)
        results_container.pack(fill=tk.BOTH, expand=True, pady=(0, 0))
        
        results_card = tk.Frame(results_container, bg=self.MATERIAL_WHITE, relief=tk.FLAT)
        results_card.pack(fill=tk.BOTH, expand=True)
        
        # Results header (compact)
        results_header = tk.Frame(results_card, bg=self.MATERIAL_GRAY_100, height=32)
        results_header.pack(fill=tk.X, side=tk.TOP)
        results_header.pack_propagate(False)
        
        results_title = tk.Label(
            results_header,
            text="Laravel Projects",
            font=("Segoe UI", 10, "bold"),
            bg=self.MATERIAL_GRAY_100,
            fg=self.MATERIAL_GRAY_800,
            anchor="w",
            padx=12
        )
        results_title.pack(side=tk.LEFT, fill=tk.Y)
        
        # Create scrollable frame for results (compact)
        results_frame = tk.Frame(results_card, bg=self.MATERIAL_WHITE)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        
        # Canvas and scrollbar for scrolling
        self.results_canvas = tk.Canvas(
            results_frame,
            bg=self.MATERIAL_WHITE,
            highlightthickness=0
        )
        scrollbar = ttk.Scrollbar(
            results_frame,
            orient="vertical",
            command=self.results_canvas.yview
        )
        self.results_scrollable_frame = tk.Frame(
            self.results_canvas,
            bg=self.MATERIAL_WHITE
        )
        
        def on_frame_configure(event):
            self.results_canvas.configure(scrollregion=self.results_canvas.bbox("all"))
        
        self.results_scrollable_frame.bind("<Configure>", on_frame_configure)
        
        self.canvas_window = self.results_canvas.create_window(
            (0, 0),
            window=self.results_scrollable_frame,
            anchor="nw"
        )
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

        # Footer inner frame for proper layout
        footer_inner = tk.Frame(footer_frame, bg=self.MATERIAL_GRAY_50)
        footer_inner.pack(fill=tk.BOTH, expand=True, padx=12, pady=4)
        
        # Status label with Material Design styling (compact)
        self.status_label = tk.Label(
            footer_inner,
            text="Ready to scan",
            font=("Segoe UI", 9),
            bg=self.MATERIAL_GRAY_50,
            fg=self.MATERIAL_GRAY_600
        )
        self.status_label.pack(side=tk.LEFT)
        
        # Made with love credit link (bottom right)
        credit_text = "Made with ❤️ by "
        author_name = "Abdelhaq El Amraoui"  # Change this to your name
        author_url = "https://github.com/abdelhaqelamraoui/laravel-projects-scanner"  # Change this to your website/URL
        
        author_link = tk.Label(
            footer_inner,
            text=author_name,
            font=("Segoe UI", 8, "underline"),
            bg=self.MATERIAL_GRAY_50,
            fg=self.MATERIAL_BLUE,
            cursor="hand2"
        )
        author_link.pack(side=tk.RIGHT)
        author_link.bind("<Button-1>", lambda e: open_url(author_url))
        
        credit_label = tk.Label(
            footer_inner,
            text=credit_text,
            font=("Segoe UI", 8),
            bg=self.MATERIAL_GRAY_50,
            fg=self.MATERIAL_GRAY_600
        )
        credit_label.pack(side=tk.RIGHT, padx=(0, 2))
        
        # Add hover effect for link
        def on_link_enter(e):
            author_link.config(fg=self.LARAVEL_RED)
        
        def on_link_leave(e):
            author_link.config(fg=self.MATERIAL_BLUE)
        
        author_link.bind("<Enter>", on_link_enter)
        author_link.bind("<Leave>", on_link_leave)
    
    def create_material_button(self, parent, text, command, bg_color, hover_color, 
                               fg_color="#212121", font_size=9, state=tk.NORMAL, height=32):
        """Create a Material Design styled button (compact, consistent height)"""
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            bg=bg_color,
            fg=fg_color,
            font=("Segoe UI", font_size, "bold"),
            relief=tk.FLAT,
            borderwidth=0,
            padx=12,
            pady=6,
            cursor="hand2",
            state=state,
            activebackground=hover_color,
            activeforeground=fg_color
        )
        
        # Add hover effects
        def on_enter(e):
            if btn['state'] == tk.NORMAL:
                btn.config(bg=hover_color)
        
        def on_leave(e):
            if btn['state'] == tk.NORMAL:
                btn.config(bg=bg_color)
        
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        
        return btn
        
        # Add hover effects
        def on_enter(e):
            if btn['state'] == tk.NORMAL:
                btn.config(bg=hover_color)
        
        def on_leave(e):
            if btn['state'] == tk.NORMAL:
                btn.config(bg=bg_color)
        
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        
        return btn

    def save_folder_path(self, folder_path):
        """Save the scanned folder path to a file"""
        filename = "scanned_folder.txt"
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(folder_path)
        except Exception as e:
            print(f"Error saving folder path: {e}")
    
    def load_saved_folder_path(self):
        """Load the saved folder path from file"""
        filename = "scanned_folder.txt"
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    folder_path = f.read().strip()
                    if folder_path and os.path.isdir(folder_path):
                        self.path_entry.delete(0, tk.END)
                        self.path_entry.insert(0, folder_path)
            except Exception as e:
                print(f"Error loading folder path: {e}")
    
    def browse_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, folder_selected)
            # Save the selected folder path
            self.save_folder_path(folder_selected)

    def start_scan(self):
        root_dir = self.path_entry.get()
        if not root_dir or not os.path.isdir(root_dir):
            messagebox.showerror("Error", "Please select a valid directory")
            return

        # Save the folder path
        self.save_folder_path(root_dir)

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
    
    def has_vendor_directory(self, project_path):
        """Check if project has a vendor directory"""
        vendor_path = os.path.join(project_path, 'vendor')
        return os.path.exists(vendor_path) and os.path.isdir(vendor_path)
    
    def add_project_row(self, project_path):
        """Add a row with a VSCode button, vendor indicator, checkbox, and project path (compact)"""
        # Create card-like row frame with Material Design styling (compact)
        row_frame = tk.Frame(
            self.results_scrollable_frame,
            bg=self.MATERIAL_WHITE,
            relief=tk.FLAT
        )
        row_frame.pack(fill=tk.X, padx=3, pady=3)
        
        # Inner frame with border effect (simulating elevation, compact)
        inner_frame = tk.Frame(
            row_frame,
            bg=self.MATERIAL_GRAY_100,
            relief=tk.FLAT
        )
        inner_frame.pack(fill=tk.X, padx=1, pady=1)
        
        content_frame = tk.Frame(inner_frame, bg=self.MATERIAL_WHITE)
        content_frame.pack(fill=tk.X, padx=10, pady=6)
        
        # Check if vendor directory exists
        has_vendor = self.has_vendor_directory(project_path)
        
        # Checkbox for selection (only enabled if vendor exists, compact)
        checkbox_var = tk.BooleanVar()
        checkbox = tk.Checkbutton(
            content_frame,
            variable=checkbox_var,
            state=tk.NORMAL if has_vendor else tk.DISABLED,
            command=lambda: self.update_remove_button_state(),
            bg=self.MATERIAL_WHITE,
            activebackground=self.MATERIAL_WHITE,
            selectcolor=self.MATERIAL_WHITE
        )
        checkbox.pack(side=tk.LEFT, padx=(0, 8))
        
        # Vendor indicator with Material Design styling (compact)
        vendor_indicator = tk.Label(
            content_frame,
            text="✓" if has_vendor else "✗",
            fg=self.MATERIAL_GREEN if has_vendor else self.MATERIAL_GRAY_600,
            bg=self.MATERIAL_WHITE,
            font=("Segoe UI", 10, "bold"),
            width=2
        )
        vendor_indicator.pack(side=tk.LEFT, padx=(0, 8))
        
        # Project path label (selectable) with Material Design typography (compact)
        path_label = tk.Label(
            content_frame,
            text=project_path,
            anchor="w",
            cursor="hand2",
            bg=self.MATERIAL_WHITE,
            fg=self.MATERIAL_GRAY_900,
            font=("Segoe UI", 9),
            padx=8
        )
        path_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        path_label.bind("<Double-1>", lambda e, p=project_path: open_folder(p))
        
        # VSCode button with Material Design styling (compact, same height)
        vscode_btn = self.create_material_button(
            content_frame,
            text="VSCode",
            command=lambda p=project_path: open_in_vscode(p),
            bg_color=self.MATERIAL_BLUE,
            hover_color="#1976D2",
            fg_color=self.MATERIAL_WHITE,
            font_size=8,
            height=32
        )
        vscode_btn.pack(side=tk.LEFT, padx=(8, 0))
        
        # Store row reference
        self.project_rows.append({
            'frame': row_frame,
            'inner_frame': inner_frame,
            'content_frame': content_frame,
            'path': project_path,
            'has_vendor': has_vendor,
            'checkbox': checkbox,
            'checkbox_var': checkbox_var,
            'vendor_indicator': vendor_indicator
        })
        
        # Update canvas scroll region
        self.results_canvas.update_idletasks()
        self.results_canvas.configure(scrollregion=self.results_canvas.bbox("all"))
        
        # Update remove button state
        self.update_remove_button_state()
    
    def update_remove_button_state(self):
        """Update the remove vendor button state based on selected projects"""
        selected_count = 0
        for row in self.project_rows:
            if row.get('has_vendor') and row.get('checkbox_var'):
                if row['checkbox_var'].get():
                    selected_count += 1
        if selected_count > 0:
            self.remove_vendor_btn.config(state=tk.NORMAL)
        else:
            self.remove_vendor_btn.config(state=tk.DISABLED)
    
    def remove_vendor_packages(self):
        """Remove vendor directories from selected projects"""
        selected_projects = []
        for row in self.project_rows:
            if row.get('has_vendor') and row.get('checkbox_var'):
                if row['checkbox_var'].get():
                    selected_projects.append(row['path'])
        
        if not selected_projects:
            messagebox.showinfo("Info", "No projects with vendor directory selected")
            return
        
        # Confirm deletion
        count = len(selected_projects)
        confirm = messagebox.askyesno(
            "Confirm Removal",
            f"Are you sure you want to remove the vendor directory from {count} project(s)?\n\n"
            f"This action cannot be undone. You will need to run 'composer install' to restore packages."
        )
        
        if not confirm:
            return
        
        # Remove vendor directories
        self.status_label.config(text=f"Removing vendor directories from {count} project(s)...")
        self.remove_vendor_btn.config(state=tk.DISABLED)
        
        def remove_vendors():
            removed_count = 0
            failed_count = 0
            failed_projects = []
            
            for project_path in selected_projects:
                vendor_path = os.path.join(project_path, 'vendor')
                try:
                    if os.path.exists(vendor_path):
                        shutil.rmtree(vendor_path)
                        removed_count += 1
                except Exception as e:
                    failed_count += 1
                    failed_projects.append((project_path, str(e)))
            
            # Update UI
            def update_ui():
                # Refresh vendor indicators
                for row in self.project_rows:
                    if row['path'] in selected_projects:
                        has_vendor = self.has_vendor_directory(row['path'])
                        row['has_vendor'] = has_vendor
                        row['vendor_indicator'].config(
                            text="✓" if has_vendor else "✗",
                            fg=self.MATERIAL_GREEN if has_vendor else self.MATERIAL_GRAY_600
                        )
                        row['checkbox'].config(state=tk.NORMAL if has_vendor else tk.DISABLED)
                        if not has_vendor:
                            row['checkbox_var'].set(False)
                
                self.update_remove_button_state()
                
                if failed_count == 0:
                    self.status_label.config(
                        text=f"Successfully removed vendor directories from {removed_count} project(s)"
                    )
                else:
                    error_msg = f"Removed from {removed_count} project(s). Failed: {failed_count}"
                    if failed_projects:
                        error_msg += "\n" + "\n".join([f"  - {p}: {e}" for p, e in failed_projects[:3]])
                    self.status_label.config(text=error_msg)
                    if len(failed_projects) > 3:
                        messagebox.showerror("Some removals failed", error_msg)
            
            self.after(0, update_ui)
        
        threading.Thread(target=remove_vendors, daemon=True).start()

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

