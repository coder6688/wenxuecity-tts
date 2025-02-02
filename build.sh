rm -rf dist
rm -rf build
rm -rf WenxuecityTTS.dmg
pyinstaller wxc-tts.spec --noconfirm 
hdiutil create -volname "Wenxuecity TTS" -srcfolder "dist/WenxuecityTTS.app" -ov -format UDZO "dist/WenxuecityTTS.dmg"