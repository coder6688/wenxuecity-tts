import PyInstaller.__main__

# remove build and dist folders
import os
os.system('rm -rf build dist')  

PyInstaller.__main__.run([
    'src/wxc_gui.py',  # Replace with your main Python file
    '--onefile',            # Package into a single executable
    '--windowed',           # For GUI apps (remove if console app)
    '--icon=assets/icon.ico',       # Optional: add an icon
    '--name=WenxueCityTTS',
    '--add-data=models/lid.176.bin;models'  # Add the model file to the bundle
])
