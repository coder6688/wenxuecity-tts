import sys
import os

# Get the parent directory of the current file's directory
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from PyQt5.QtWidgets import *
from PyQt5.QtGui import QTextCursor, QColor, QFont
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import requests
import time
from bs4 import BeautifulSoup
from langdetect import detect, LangDetectException
from src.text_to_speech_online import speak, detect_language, clean_text_for_detection, normalize_lang_code
import re

class SpeakingThread(QThread):
    update_output_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()
    
    def __init__(self, words, lang='en', start_index=0, get_volume=lambda: 80, auto_detect=True):
        super().__init__()
        self.words = words
        self.original_lang = lang  # Store original language
        self.current_lang = lang    # Track current speaking language
        self.start_index = start_index
        self.stopped = False
        self.current_index = start_index
        self.get_volume = get_volume  # Store volume getter function
        self.auto_detect = auto_detect  # Auto-detect flag
        
    def run(self):
        total_words = len(self.words)

        if total_words == 0:  # Add empty check
            self.update_output_signal.emit("Error: No content to speak")
            return
            
        text_chunk = []
        while self.current_index < total_words and not self.stopped:
            word = self.words[self.current_index].strip()
            text_chunk.append(word)
            
            if len(text_chunk) >= 1 or self.current_index == total_words - 1:
                full_text = ' '.join(text_chunk)
                detected_lang = detect_language(clean_text_for_detection(full_text))
                normalized_lang = normalize_lang_code(detected_lang)

                # fixed for wxc only
                if normalized_lang not in ['en', 'zh-cn']:
                    normalized_lang = 'zh-cn'
                
                if normalized_lang != self.current_lang:
                    self.current_lang = normalized_lang
                    print(f"Language changed to: {normalized_lang}")
                text_chunk = []
            
            # Update output before speaking
            current_time = time.strftime("%H:%M:%S")
            output_message = f"[{current_time}] Speaking: {word}"
            print(output_message)
            self.update_output_signal.emit(f"Speaking ({self.current_lang}): {self.current_index + 1}/{total_words} - {word}")
            
            try:
                current_volume = self.get_volume()  # Get fresh volume value
                speak(word, lang=self.current_lang, volume=current_volume)
                self.current_index += 1
            except Exception as e:
                self.update_output_signal.emit(f"Speech Error: {str(e)}")
                break
        
        self.finished_signal.emit()

    def stop(self):
        self.stopped = True

class NewsFetcherThread(QThread):
    news_fetched = pyqtSignal(list)
    
    def __init__(self):
        super().__init__()
        
    def run(self):
        from src.wxc_news_list import get_wenxuecity_news  # Import your news function
        articles = get_wenxuecity_news()
        self.news_fetched.emit(articles)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Wenxuecity Text-to-Speech News Reader")
        self.setGeometry(100, 100, 900, 1200)

        # Create main splitter
        splitter = QSplitter(Qt.Vertical)
        self.setCentralWidget(splitter)

        # Create top section for news
        top_widget = QWidget()
        top_layout = QVBoxLayout(top_widget)
        top_layout.setContentsMargins(0, 0, 0, 0)

        # Add font size buttons
        font_layout = QHBoxLayout()
        self.font_size = 20  # Default font size
        self.increase_font_btn = QPushButton("+")
        self.decrease_font_btn = QPushButton("-")
        font_layout.addWidget(QLabel("Text Size:"))
        font_layout.addWidget(self.decrease_font_btn)
        font_layout.addWidget(self.increase_font_btn)
        # top_layout.addLayout(font_layout)  # Add to existing bottom layout

        self.news_label = QLabel("Latest News:")
        self.news_display = QTextBrowser()
        self.news_display.setOpenLinks(False)  # Now works with QTextBrowser
        self.news_display.anchorClicked.connect(self.on_news_clicked)
        self.refresh_news_btn = QPushButton("↻")  # Unicode refresh symbol
        self.refresh_news_btn.setFixedWidth(50)  # Set fixed width
        self.refresh_news_btn.setToolTip("Refresh news list")
        
        # Create horizontal layout for label + button
        news_header = QHBoxLayout()
        news_header.setContentsMargins(0, 0, 0, 5)  # Add bottom margin
        news_header.addWidget(self.news_label)
        news_header.addStretch()
        
        # Add button with alignment
        self.refresh_news_btn.setFixedWidth(40)
        news_header.addWidget(self.refresh_news_btn, 0, Qt.AlignRight)
        
        top_layout.addLayout(news_header)
        top_layout.addWidget(self.news_display)

        # Create bottom section for controls
        bottom_widget = QWidget()
        bottom_layout = QVBoxLayout(bottom_widget)
        
        # URL input
        self.url_label = QLabel("Enter URL:")
        self.url_input = QLineEdit()
        bottom_layout.addWidget(self.url_label)
        bottom_layout.addWidget(self.url_input)

        # Language selection
        self.lang_label = QLabel("Select Language (optional):")
        self.lang_combo = QComboBox()
        languages = ['', 'zh-cn','en', 'fr', 'es', 'de', 'it', 'pt', 'ru']
        self.lang_combo.addItems(languages)
        bottom_layout.addWidget(self.lang_label)
        bottom_layout.addWidget(self.lang_combo)

        # Add auto-detect checkbox to language selection area
        self.auto_detect_check = QCheckBox("Auto Detect Language")
        self.auto_detect_check.setChecked(True)  # Default enabled
        bottom_layout.addWidget(self.auto_detect_check)  # Add to existing lang layout

        # Auto-continue checkbox
        self.auto_continue_check = QCheckBox("Auto Continue")
        self.auto_continue_check.setChecked(True)  # Default enabled
        bottom_layout.addWidget(self.auto_continue_check)  # Add to existing lang layout

        # Character limit
        self.chars_label = QLabel("Max Characters:")
        self.chars_input = QLineEdit()
        self.chars_input.setText('500')
        bottom_layout.addWidget(self.chars_label)
        bottom_layout.addWidget(self.chars_input)
        
        # Modified control layout
        control_layout = QHBoxLayout()
        
        # Font controls
        font_group = QHBoxLayout()
        self.text_size_label = QLabel("Text Size:")  # Create instance variable
        self.decrease_font_btn = QPushButton("-")
        self.increase_font_btn = QPushButton("+")
        font_group.addWidget(self.text_size_label)
        font_group.addWidget(self.decrease_font_btn)
        font_group.addWidget(self.increase_font_btn)
        
        # Volume controls
        self.volume = 80  # Default volume (0-100)
        self.volume_label = QLabel("Volume:")
        volume_group = QHBoxLayout()
        volume_group.addWidget(self.volume_label)
        self.decrease_volume_btn = QPushButton("-")
        self.increase_volume_btn = QPushButton("+")
        volume_group.addWidget(self.decrease_volume_btn)
        volume_group.addWidget(self.increase_volume_btn)
        
        # Add to main control layout
        control_layout.addLayout(font_group)
        control_layout.addStretch()
        control_layout.addLayout(volume_group)
        bottom_layout.addLayout(control_layout)

        # Buttons
        button_layout = QHBoxLayout()
        self.speak_button = QPushButton("Speak")
        self.stop_button = QPushButton("Pause")
        self.clear_button = QPushButton("Clear")
        self.exit_button = QPushButton("Exit")
        button_layout.addWidget(self.speak_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addWidget(self.clear_button)
        button_layout.addWidget(self.exit_button)
        bottom_layout.addLayout(button_layout)

        # Output area
        self.output_label = QLabel("Caption:")
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        bottom_layout.addWidget(self.output_label)
        bottom_layout.addWidget(self.output_text)

        # Add sections to splitter
        splitter.addWidget(top_widget)
        splitter.addWidget(bottom_widget)
        
        # Set splitter stretch factors (news area gets 1/3 of space initially)
        splitter.setSizes([300, 500])

        # Connect signals
        self.speak_button.clicked.connect(self.process_and_speak)
        self.stop_button.clicked.connect(self.stop_speaking)
        self.clear_button.clicked.connect(self.clear_input)
        self.exit_button.clicked.connect(self.close)
        self.refresh_news_btn.clicked.connect(self.load_news_list)
        self.load_news_list()

        self.original_words = []
        self.current_index = 0
        self.original_url = ""
        self.original_lang = ""
        self.original_chars_limit = 0
        self.news_articles = []  # Add this to store news list
        self.current_news_index = -1  # Add this to track current news position

        # Enable stop button only when speaking
        self.stop_button.setEnabled(False)

        # Connect font buttons
        self.increase_font_btn.clicked.connect(self.increase_font_size)
        self.decrease_font_btn.clicked.connect(self.decrease_font_size)
        
        # Set initial fonts
        self.update_font_size()

        # Connect volume buttons
        self.increase_volume_btn.clicked.connect(self.increase_volume)
        self.decrease_volume_btn.clicked.connect(self.decrease_volume)

        # Center window after initialization
        self.center_window()

    def center_window(self):
        """Center the window on the active screen"""
        frame_geo = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        center_point = QApplication.desktop().screenGeometry(screen).center()
        frame_geo.moveCenter(center_point)
        self.move(frame_geo.topLeft())

    def showEvent(self, event):
        """Handle window show events"""
        self.center_window()
        super().showEvent(event)

    def clear_input(self):
        """Clear all input fields and output text."""
        self.url_input.clear()
        self.lang_combo.setCurrentIndex(0)
        self.chars_input.clear()
        self.output_text.clear()

    def stop_speaking(self):
        if hasattr(self, 'speaking_thread') and self.speaking_thread.isRunning():
            self.speaking_thread.stop()
            # Save the exact position where we stopped
            self.current_index = self.speaking_thread.current_index
            self.speaking_thread.quit()
            self.speaking_thread.wait()
            self.stop_button.setEnabled(False)
            self.show_message(f"Paused at position: {self.current_index + 1}")
            #self.current_index = self.current_index + 1 # skip the current already spoken word

    def process_and_speak(self):
        """Process the URL and speak the content with timing."""
        url = self.url_input.text().strip()
        if not url:
            self.show_message("Please enter a valid URL.")
            return
            
        # Get language from combo box
        lang = self.lang_combo.currentText()
        if not lang:  # Handle empty selection
            lang = 'en'  # Default to English
        
        chars_limit = int(self.chars_input.text()) if self.chars_input.text() else 500
        
        # Modified resume condition check
        if (url == self.original_url and
            self.current_index < len(self.original_words)):
            
            # Force stop any existing thread
            if hasattr(self, 'speaking_thread') and self.speaking_thread.isRunning():
                self.speaking_thread.stop()
                self.speaking_thread.quit()
                self.speaking_thread.wait()
            
            self.speaking_thread = SpeakingThread(
                self.original_words,
                lang=self.lang_combo.currentText(),
                start_index=self.current_index,
                get_volume=lambda: self.volume,  # Pass real-time volume getter
                auto_detect=self.auto_detect_check.isChecked()
            )
            self.speaking_thread.update_output_signal.connect(self.update_output)
            self.speaking_thread.finished_signal.connect(self.handle_speech_finished)
            self.speaking_thread.start()
            self.stop_button.setEnabled(True)
            return
            
        try:
            response = requests.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
                element.decompose()
                
            main_text = soup.get_text(separator='\n', strip=True)

            # specific for wxc news
            idx = main_text.find("被阅读次数")
            if idx != -1:
                main_text = main_text[idx+len("被阅读次数") + 8:] # skip the "被阅读次数" and the following 8 characters(A-AA+)
            
            if not lang:
                try:
                    lang = detect(main_text[:chars_limit])
                except LangDetectException:
                    lang = 'en'
                    
            speak_text = main_text[:chars_limit]
            
            segments = re.findall(r'[^。！？，；：、]+[。！？，；：、]?', speak_text)
            self.original_words = [seg.strip() for seg in segments if seg.strip()]

            self.current_index = 0
            self.original_url = url
            self.original_lang = lang
            self.original_chars_limit = chars_limit
            
            # Add validation before thread start
            if not self.original_words:
                self.show_message("Error: No text content found to speak")
                return
            
            # Add thread cleanup
            if hasattr(self, 'speaking_thread'):
                self.speaking_thread.quit()
            
            self.speaking_thread = SpeakingThread(
                self.original_words,
                lang=lang,
                start_index=self.current_index,
                get_volume=lambda: self.volume,  # Pass real-time volume getter
                auto_detect=self.auto_detect_check.isChecked()
            )
            self.speaking_thread.update_output_signal.connect(self.update_output)
            self.speaking_thread.finished_signal.connect(self.handle_speech_finished)
            self.speaking_thread.start()
            self.stop_button.setEnabled(True)
            
        except requests.exceptions.RequestException as e:
            self.show_message(f"Error fetching URL: {e}")
            
    def update_output(self, message):
        self.output_text.setReadOnly(False)
        cursor = self.output_text.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.output_text.setTextCursor(cursor)
        # Add error message filtering
        if "Speech Error" in message:
            self.output_text.setTextColor(QColor(255, 0, 0))  # Red text for errors
        else:
            self.output_text.setTextColor(QColor(0, 0, 0))  # Black text otherwise
        self.output_text.append(message)
        self.output_text.verticalScrollBar().setValue(self.output_text.verticalScrollBar().maximum())
        self.output_text.setReadOnly(True)  # Re-enable read-only after update

    def load_news_list(self):
        """Load and display news in the text area"""
        self.news_display.clear()
        self.news_display.append("Loading news...")
        
        # Run news fetching in a thread to prevent UI freeze
        self.news_thread = NewsFetcherThread()
        self.news_thread.news_fetched.connect(self.update_news_display)
        self.news_thread.start()

    def update_news_display(self, articles):
        """Update display with formatted news list"""
        self.news_display.clear()
        self.news_articles = articles  # Store the articles list
        for idx, article in enumerate(articles, 1):
            self.news_display.append(
                f"{idx}. <a href='{article['url']}' style='text-decoration:none; color:blue;'>"
                f"{article['title']}</a>"
            )
        self.news_display.moveCursor(QTextCursor.Start)

    def on_news_clicked(self, url):
        """Handle news link clicks"""
        was_speaking = False
        # Stop any ongoing speech
        if hasattr(self, 'speaking_thread') and self.speaking_thread.isRunning():
            was_speaking = True
            self.stop_speaking()
            self.show_message("Interrupting current speech...")
            self.speaking_thread.wait(2000)  # Wait up to 2 seconds
            if self.speaking_thread.isRunning():  # Force terminate if still running
                self.speaking_thread.terminate()
                self.speaking_thread.wait()
                self.show_message("Speech stopped forcefully!")
            else:
                self.show_message("Speech interrupted successfully")
        
        # Reset state variables
        self.current_index = 0
        self.original_words = []
        self.original_url = ""
        
        # Find clicked article position
        clicked_url = url.toString()
        clicked_title = ""
        for idx, article in enumerate(self.news_articles):
            if article['url'] == clicked_url:
                self.current_news_index = idx
                clicked_title = article['title']
                break
        else:
            self.current_news_index = -1
        
        # Add index display
        self.show_message(f"*** Start reading news {self.current_news_index + 1} of {len(self.news_articles)} - {clicked_title}")
        
        # Update URL and start processing
        self.url_input.setText(clicked_url)
        self.process_and_speak()

        if was_speaking:
            self.stop_button.setEnabled(False)  # Update UI state

    def show_message(self, message):
        """Display messages in the output area"""
        self.output_text.setReadOnly(False)
        self.output_text.append(message)
        self.output_text.verticalScrollBar().setValue(
            self.output_text.verticalScrollBar().maximum()
        )
        self.output_text.setReadOnly(True)

    def increase_font_size(self):
        self.font_size = min(24, self.font_size + 2)
        self.update_font_size()

    def decrease_font_size(self):
        self.font_size = max(8, self.font_size - 2)
        self.update_font_size()

    def update_font_size(self):
        font = QFont()
        font.setPointSize(self.font_size)
        
        # Update all text elements
        widgets_to_update = [
            self.text_size_label,
            self.news_display,
            self.output_text,
            self.news_label,
            self.output_label,
            self.url_label,
            self.url_input,
            self.lang_label,
            self.lang_combo,
            self.chars_label,
            self.chars_input,
            self.auto_detect_check,
            self.auto_continue_check,
            self.volume_label,
            self.speak_button,
            self.stop_button,
            self.clear_button,
            self.exit_button,
            self.refresh_news_btn,
        ]
        
        for widget in widgets_to_update:
            widget.setFont(font)
        
        # Adjust button fonts slightly smaller
        button_font = QFont()
        button_font.setPointSize(self.font_size - 2)
        for btn in [self.increase_font_btn, self.decrease_font_btn,
                    self.increase_volume_btn, self.decrease_volume_btn]:
            btn.setFont(button_font)

    def increase_volume(self):
        self.volume = min(100, self.volume + 10)
        self.show_message(f"Volume: {self.volume}%")
        # Add actual volume control implementation here

    def decrease_volume(self):
        self.volume = max(0, self.volume - 10)
        self.show_message(f"Volume: {self.volume}%")
        # Add actual volume control implementation here

    def handle_speech_finished(self):
        # Only auto-continue if we naturally finished speaking all text
        if (self.auto_continue_check.isChecked() 
            and self.current_news_index != -1
            and self.current_news_index < len(self.news_articles) - 1
            and self.stop_button.isEnabled() == True):
            #and self.current_index >= len(self.original_words)):  # bug: has to disable here
            
            # Move to next article
            next_index = self.current_news_index + 1
            next_article = self.news_articles[next_index]
            
            # Reset state BEFORE processing next article
            self.current_news_index = next_index
            self.current_index = 0
            self.original_words = []
            self.original_url = ""
            
            # Update UI and process
            self.show_message(f"*** Continuing to: {next_article['title']}")
            
            # Speak the title first
            title = next_article['title']
            if self.auto_detect_check.isChecked():
                clean_title = clean_text_for_detection(title)
                detected_lang = detect_language(clean_title)
                lang = normalize_lang_code(detected_lang)
                if lang not in ['en', 'zh-cn']:  # Match SpeakingThread's fallback
                    lang = 'zh-cn'
            else:
                lang = self.lang_combo.currentText() or 'en'

            speak(f"Next article: {title}", lang=lang, volume=self.volume)
            
            # Add brief delay before content starts
            time.sleep(0.5)  # 500ms pause after title
            
            self.url_input.setText(next_article['url'])
            self.process_and_speak()

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
