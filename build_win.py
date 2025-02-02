import PyInstaller.__main__
import datetime

# remove build and dist folders
import os
os.system('rm -rf build dist')  

# Get current date in YYYYMMDD format
current_date = datetime.datetime.now().strftime('%Y%m%d')

PyInstaller.__main__.run([
    'src/wxc_gui.py',  # Replace with your main Python file
    '--onefile',            # Package into a single executable
    '--windowed',           # For GUI apps (remove if console app)
    '--icon=assets/icon.ico',       # Optional: add an icon
    f'--name=WenxuecityTTS_{current_date}',  # Add date to executable name
    '--add-data=models/lid.176.bin;models'  # Add the model file to the bundle
])
