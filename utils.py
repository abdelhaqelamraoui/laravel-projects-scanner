import os
import platform
import subprocess
import shutil
import webbrowser


def open_folder(path):
    if platform.system() == "Windows":
        os.startfile(path)
    elif platform.system() == "Darwin":  # macOS
        subprocess.Popen(["open", path])
    else:  # Linux and others
        subprocess.Popen(["xdg-open", path])


def open_in_vscode(path):
    """Open a folder in VSCode"""
    code_command = None
    
    # Try to find the 'code' command
    if platform.system() == "Windows":
        # Common VSCode installation paths on Windows
        possible_paths = [
            os.path.expanduser(r"~\AppData\Local\Programs\Microsoft VS Code\Code.exe"),
            r"C:\Program Files\Microsoft VS Code\Code.exe",
            r"C:\Program Files (x86)\Microsoft VS Code\Code.exe",
        ]
        for code_path in possible_paths:
            if os.path.exists(code_path):
                code_command = [code_path]
                break
        
        # Also try 'code' command if available in PATH
        if not code_command and shutil.which("code"):
            code_command = ["code"]
    else:
        # On macOS and Linux, try 'code' command
        code_command = shutil.which("code")
        if code_command:
            code_command = [code_command]
    
    if code_command:
        try:
            subprocess.Popen(code_command + [path])
        except Exception as e:
            print(f"Error opening VSCode: {e}")
    else:
        # Fallback: try to open with 'code' command anyway
        try:
            subprocess.Popen(["code", path])
        except Exception:
            print("VSCode not found. Please install VSCode and ensure 'code' command is in PATH.")


def open_url(url):
    """Open a URL in the default web browser"""
    try:
        webbrowser.open(url)
    except Exception as e:
        print(f"Error opening URL: {e}")
