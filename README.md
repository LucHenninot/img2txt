# ![img2txt](lib/img2txt-small.png) img2txt Tool Documentation

#### A Windows application that extracts text from clipboard images using OCR and copies the text back to the clipboard.

## 📋 Features
- Clipboard image-to-text conversion
- System-wide keyboard shortcut support
- Configurable OCR settings
- Lightweight GUI with status feedback
- Multi-language support

## ⚙️ System Requirements
- Windows 10/11
- Python 3.9+ (for source version)
- [Tesseract OCR 5.0+](#tesseract)

# 🖥️ Usage
## Install from this site
1. Download from the the latest [Release](/releases/latest/download/):
   - [img2txt.exe](https://github.com/LucHenninot/img2txt/releases/download/v0.1.0/img2txt.exe)
   - [config.ini](https://github.com/LucHenninot/img2txt/releases/download/v0.1.0/config.ini) *(optional, the program will create it if needed)*
2. Place all files in the same directory
k
## GUI Mode
1. Launch `img2txt.exe` in administrator mode or not (see below [^1])
2. Copy an image to clipboard (Snipping Tool/Print Screen)
3. Either:
   - Click `Convert Image to Text` button
   - Press configured hotkey (default: `Ctrl+Alt+V`)
v*note*

Paste text anywhere (`Ctrl+V`)

## 📥 Installation

### Method 2: From Source
```bash
# Create virtual environment
python -m venv ocr_env
ocr_env\Scripts\activate

# Install dependencies
pip install -r requirements.txt 

# Generate the program
pyinstaller --onefile --windowed --icon=lib/img2txt.ico --name img2txt img2txt.py
```

### <a name="tesseract"></a>Install Tesseract OCR
**Method 1**: from Tesseract
Download from [https://github.com/UB-Mannheim/tesseract/wiki]()  
Add the Tesseract folder to PATH during installation, or manually  
(should be `C:\Program Files\Tesseract-OCR\tesseract.exe` by default)

Alternatively, set the `tesseract_path` in the [config.ini](#config) file

**Method 2**: using `chocolatey` 
In a powershell terminal as administrator:  
`choco install tesseract`  
No need to modify the path: choco does it.

# ⚙️ <a name="config"></a>Configuration (config.ini)

By default `img2txt.exe` creates a `config.ini` file if not present.  
Here is the default `config.ini` file:
```
[General]
; Keyboard shortcut (ctrl/alt/shift+key)
hotkey = ctrl+alt+v

; OCR languages (eng, fra, spa, etc)
; set eng+spa to optimize Tesseract for english and spanish for example.
language = eng

; Message display time (milliseconds)
timeout = 3000

; Admin mode: ask/always/never
admin_mode = ask

[Advanced]
; Path to tesseract.exe if not in PATH
tesseract_path = 

; Keep temporary images for debugging
save_temp_images = false
```

## Configuration Options
| Section | Key | Values | Description |
| ------- | --- | ------ | ----------- |
| General | hotkey | modifier+key | System-wide shortcut combination | 
| General | language | ISO 3166-1 language codes | OCR languages (e.g., eng+fra) |
| General | timeout |1000-10000 | Success message duration |
| General | admin_mode | ask/always/never | Privilege elevation behavior |
| Advanced | tesseract_path | Full path to tesseract.exe | Custom Tesseract location |
| Advanced | save_temp_images | true/false | Keep temporary PNG files |

## 🚨 Troubleshooting
### Common Issues
| Error | Solution |
| ----- | -------- |
| Tesseract not found | - Check PATH<br>- set `tesseract_path` in `config.ini` |
| Unsupported image format | Convert image to RGB format |
| Hotkey not working	| - Run as admin.<br>- Check for hotkey conflicts |
| OCR accuracy issues | - Use higher quality images<br>- add language data |

### Error Messages
| Message | Meaning |
| ------- | ------- |
| "No image in clipboard" | Copy an image first |
| "No text extracted" | Poor image quality/unsupported language |
| "Conversion in progress" | Wait for current operation to finish |


# ❓FAQ
**Q: How do I change the keyboard shortcut?**
A: Edit hotkey in config.ini and restart the app.

**Q: Can I use multiple languages simultaneously?**
A: Yes! Separate languages with + (e.g., eng+fra)

**Q: Why does the EXE trigger antivirus warnings?**
A: This is common with PyInstaller packages. Add an exception for the EXE.  
You can build your own .exe from the code if you don't trust the provided .exe

**Q: Can I run without the GUI?**
A: Yes! Use the system-wide shortcut - the GUI will minimize to tray.
