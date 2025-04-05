import tkinter as tk
from tkinter import messagebox
import pyperclip
import pytesseract
from PIL import ImageGrab
import tempfile
import os
import keyboard
import threading
import ctypes
import sys
import configparser
from configparser import ConfigParser

# Configuration handling
def get_config_path():
    """Get config file path next to executable"""
    if getattr(sys, 'frozen', False):  # Running as compiled executable
        app_dir = os.path.dirname(sys.executable)
    else:  # Running as script
        app_dir = os.path.dirname(os.path.abspath(__file__))
    
    return os.path.join(app_dir, 'config.ini')

def load_config():
    """Load or create configuration with defaults"""
    config = ConfigParser()
    
    # Default configuration
    config.read_dict({
        'General': {
            'hotkey': 'ctrl+alt+v',
            'admin_mode': 'ask',
            'language': 'eng',
            'timeout': '3000'
        },
        'Advanced': {
            'save_temp_images': 'false',
            'tesseract_path': ''
        }
    })
    
    # Load existing config if available
    config_file = get_config_path()
    config.read(config_file)
    
    # Save default config if none exists
    if not os.path.exists(config_file):
        try:
            with open(config_file, 'w') as f:
                config.write(f)
        except Exception as e:
            messagebox.showerror("Config Error", f"Could not create config.ini:\n{str(e)}")

    return config

def save_config(config):
    """Save configuration to file"""
    with open(get_config_path(), 'w') as configfile:
        config.write(configfile)

# Admin check
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

class ClipboardOCRApp:
    def __init__(self, master, config):
        self.master = master
        self.config = config
        self.conversion_lock = threading.Lock()
        
        # Initialize Tesseract
        if config['Advanced']['tesseract_path']:
            pytesseract.pytesseract.tesseract_cmd = config['Advanced']['tesseract_path']
        
        # Setup UI
        master.title("Clipboard OCR Tool")
        master.geometry("400x140")
        self.setup_ui()
        
        # Setup hotkey
        self.setup_hotkey()
        
        # Handle closing
        master.protocol("WM_DELETE_WINDOW", self.on_close)

    def setup_ui(self):
        """Initialize user interface components"""
        self.btn_style = {'font': ('Arial', 10), 'bg': '#4CAF50', 'fg': 'white'}
        self.status_style = {'font': ('Arial', 10), 'fg': '#666666'}

        hotkey = self.config['General']['hotkey'].upper()
        btn_text = f"Convert Image to Text ({hotkey})"
        self.btn_convert = tk.Button(self.master, text=btn_text, 
                                   command=self.convert_clipboard, **self.btn_style)
        self.btn_convert.pack(pady=15, padx=20, fill=tk.X)

        self.status_label = tk.Label(self.master, text="Ready", **self.status_style)
        self.status_label.pack(pady=5)

    def setup_hotkey(self):
        """Register system-wide or window-only hotkey"""
        try:
            if is_admin():
                keyboard.add_hotkey(self.config['General']['hotkey'], self.convert_clipboard)
            else:
                self.master.bind(f'<{self.config["General"]["hotkey"].replace("+", "-")}>', 
                               lambda e: self.convert_clipboard())
        except Exception as e:
            messagebox.showwarning("Hotkey Error", 
                                 f"Invalid hotkey '{self.config['General']['hotkey']}'\nUsing default Ctrl+Alt+V")
            keyboard.add_hotkey('ctrl+alt+v', self.convert_clipboard)

    def convert_clipboard(self, event=None):
        """Main OCR conversion handler"""
        if not self.conversion_lock.acquire(blocking=False):
            return

        try:
            self.update_ui_state(disabled=True, status="Processing...")
            
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_file = os.path.join(temp_dir, "clipboard_image.png")
                
                # Process image
                image = ImageGrab.grabclipboard()
                if not image:
                    raise ValueError("No image in clipboard")
                
                if image.mode in ('RGBA', 'LA', 'P'):
                    image = image.convert('RGB')
                image.save(temp_file, "PNG")
                
                # OCR processing
                text = pytesseract.image_to_string(
                    temp_file,
                    lang=self.config['General']['language']
                ).strip()
                
                if not text:
                    raise ValueError("No text extracted")
                
                pyperclip.copy(text)
                self.show_success()

        except Exception as e:
            self.show_error(str(e))
        finally:
            self.update_ui_state(disabled=False)
            self.conversion_lock.release()

    def update_ui_state(self, disabled=True, status=None):
        """Update UI elements state"""
        self.master.after(0, lambda: self.btn_convert.config(state=tk.DISABLED if disabled else tk.NORMAL))
        if status:
            self.master.after(0, lambda: self.status_label.config(text=status))

    def show_success(self):
        """Handle successful conversion"""
        timeout = int(self.config['General']['timeout'])
        self.master.after(0, lambda: self.status_label.config(text="Text copied to clipboard!"))
        self.master.after(timeout, lambda: self.status_label.config(text="Ready"))

    def show_error(self, message):
        """Display error message"""
        self.master.after(0, lambda: messagebox.showerror("Error", message))

    def on_close(self):
        """Cleanup on window close"""
        if is_admin():
            keyboard.unhook_all()
        self.master.destroy()

if __name__ == "__main__":
    # Platform check
    if sys.platform != 'win32':
        messagebox.showerror("Unsupported Platform", "This application only supports Windows")
        sys.exit(1)

    # Load config
    config = load_config()
    
    # Admin elevation handling
    admin = is_admin()
    if not admin and config['General']['admin_mode'] == 'ask':
        root = tk.Tk()
        root.withdraw()
        answer = messagebox.askyesno(
            "Admin Rights", 
            "Run with admin privileges for system-wide shortcuts?\n"
            "(Cancel will use window-only shortcuts)"
        )
        root.destroy()
        
        if answer:
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, " ".join(sys.argv), None, 1
            )
            sys.exit()

    # Main application
    try:
        root = tk.Tk()
        pytesseract.get_tesseract_version()
        app = ClipboardOCRApp(root, config)
        root.mainloop()
    except pytesseract.TesseractNotFoundError:
        messagebox.showerror(
            "OCR Engine Missing", 
            "Tesseract OCR not found.\n"
            "1. Install from https://github.com/UB-Mannheim/tesseract/wiki\n"
            "2. Set path in config.ini if needed"
        )

