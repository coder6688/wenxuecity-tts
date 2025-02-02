rm -rf dist
rm -rf build
rm -rf WenxuecityTTS.dmg
pyinstaller wxc-tts.spec --noconfirm 

# Create dated DMG
hdiutil create -volname "Wenxuecity TTS" -srcfolder "dist/WenxuecityTTS.app" -ov -format UDZO "dist/WenxuecityTTS_$(date +"%Y%m%d").dmg"