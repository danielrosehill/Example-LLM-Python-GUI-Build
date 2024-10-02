import sys
import os
import requests
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel,
                             QLineEdit, QPushButton, QFileDialog, QMessageBox,
                             QComboBox, QTextEdit, QProgressBar, QHBoxLayout)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QSettings, QThread, pyqtSignal
from openai import OpenAI

class ImageGeneratorThread(QThread):
    progress = pyqtSignal(int)
    image_ready = pyqtSignal(str)

    def __init__(self, prompt, size, client):
        super().__init__()
        self.prompt = prompt
        self.size = size
        self.client = client

    def run(self):
        try:
            for i in range(1, 101):
                self.progress.emit(i)
                self.msleep(30)
            response = self.client.images.generate(prompt=self.prompt,
                                                   n=1,
                                                   size=self.size)
            image_url = response.data[0].url
            self.image_ready.emit(image_url)
        except Exception as e:
            self.image_ready.emit(f"Error: {str(e)}")

class DalleImageGenerator(QWidget):
    def __init__(self):
        super().__init__()
        self.settings = QSettings('DalleImageGenerator', 'Settings')
        self.client = OpenAI(api_key=self.settings.value('api_key', ''))
        self.initUI()

    def initUI(self):
        self.setWindowTitle('DALL-E Image Generator')
        self.setGeometry(100, 100, 600, 700)
        self.setStyleSheet("background-color: #E7F6EF; color: #10A37F;")

        layout = QVBoxLayout()

        api_key_label = QLabel('OpenAI API Key:')
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText('Enter your OpenAI API key here')
        self.api_key_input.setStyleSheet("background-color: white; padding: 5px;")
        layout.addWidget(api_key_label)
        layout.addWidget(self.api_key_input)

        title_label = QLabel('Image Title:')
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText('Enter a descriptive title for your image')
        self.title_input.setStyleSheet("background-color: white; padding: 5px;")
        layout.addWidget(title_label)
        layout.addWidget(self.title_input)

        prompt_label = QLabel('Enter your prompt:')
        self.prompt_input = QTextEdit()
        self.prompt_input.setPlaceholderText('Describe the image you want to generate in detail...')
        self.prompt_input.setStyleSheet("background-color: white; padding: 5px;")
        layout.addWidget(prompt_label)
        layout.addWidget(self.prompt_input)

        size_label = QLabel('Select Image Size:')
        self.size_combo = QComboBox()
        self.size_combo.addItems(["1024x1024", "1792x1024", "1024x1792"])
        self.size_combo.setStyleSheet("background-color: white; padding: 5px;")
        layout.addWidget(size_label)
        layout.addWidget(self.size_combo)

        folder_layout = QHBoxLayout()
        self.folder_label = QLabel('Select output folder:')
        self.folder_button = QPushButton('Browse')
        self.folder_button.clicked.connect(self.select_folder)
        self.folder_button.setStyleSheet("background-color: #10A37F; color: white; padding: 5px;")
        folder_layout.addWidget(self.folder_label)
        folder_layout.addWidget(self.folder_button)
        layout.addLayout(folder_layout)

        save_config_button = QPushButton('Save Config')
        save_config_button.setStyleSheet('background-color: #10A37F; color: white; padding: 5px;')
        save_config_button.clicked.connect(self.save_settings)
        layout.addWidget(save_config_button)

        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("QProgressBar::chunk { background-color: #10A37F; }")
        layout.addWidget(self.progress_bar)

        self.generate_button = QPushButton('Generate Image')
        self.generate_button.setStyleSheet('background-color: #10A37F; color: white; padding: 10px;')
        self.generate_button.clicked.connect(self.generate_image)
        layout.addWidget(self.generate_button)

        self.image_label = QLabel()
        self.image_label.setFixedSize(300, 300)
        self.image_label.setStyleSheet("background-color: white; border: 1px solid #10A37F;")
        layout.addWidget(self.image_label)

        button_layout = QHBoxLayout()
        open_editor_button = QPushButton("Open In Photo Editor")
        open_editor_button.clicked.connect(self.open_in_photo_editor)
        open_editor_button.setStyleSheet("background-color: #10A37F; color: white; padding: 5px;")
        button_layout.addWidget(open_editor_button)

        view_full_size_button = QPushButton("View Full Size")
        view_full_size_button.clicked.connect(self.view_full_size_image)
        view_full_size_button.setStyleSheet("background-color: #10A37F; color: white; padding: 5px;")
        button_layout.addWidget(view_full_size_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)
        self.load_settings()

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Directory")
        if folder:
            self.folder_label.setText(f'Selected: {folder}')
            self.settings.setValue('output_folder', folder)

    def load_settings(self):
        api_key = self.settings.value('api_key', '')
        if api_key:
            self.api_key_input.setText(api_key)

    def save_settings(self):
        api_key = self.api_key_input.text().strip()
        if not api_key:
            QMessageBox.warning(self, 'Error', 'Please enter your OpenAI API key.')
            return
        self.settings.setValue('api_key', api_key)
        self.client = OpenAI(api_key=api_key)
        QMessageBox.information(self, 'Config Updated', 'Configuration updated successfully!')

    def generate_image(self):
        title = self.title_input.text().strip().replace(" ", "-").lower()
        prompt = self.prompt_input.toPlainText().strip()
        if not title or not prompt:
            QMessageBox.warning(self, 'Error', 'Please enter both a title and a prompt.')
            return
        size = self.size_combo.currentText()

        if not self.client.api_key:
            QMessageBox.warning(self, 'Error', 'OpenAI API key is missing. Please update your configuration.')
            return

        self.generate_button.setEnabled(False)
        self.thread = ImageGeneratorThread(prompt=prompt, size=size, client=self.client)
        self.thread.progress.connect(self.progress_bar.setValue)
        self.thread.image_ready.connect(lambda url: self.display_image(url, title))
        self.thread.finished.connect(lambda: self.generate_button.setEnabled(True))
        self.thread.start()

    def display_image(self, url_or_error_message, title):
        if "Error:" in url_or_error_message:
            QMessageBox.critical(self, 'Error', url_or_error_message)
        else:
            image_url = url_or_error_message
            try:
                image_response = requests.get(image_url)
                image_response.raise_for_status()
                pixmap = QPixmap()
                pixmap.loadFromData(image_response.content)
                self.image_label.setPixmap(pixmap.scaled(300, 300, Qt.AspectRatioMode.KeepAspectRatio))

                today = datetime.now().strftime('%d%m%y')
                output_folder = self.settings.value('output_folder', '')
                save_path = os.path.join(output_folder, today)
                os.makedirs(save_path, exist_ok=True)
                image_path = os.path.join(save_path, f'{title}.webp')

                with open(image_path, 'wb') as f:
                    f.write(image_response.content)

                QMessageBox.information(self, 'Success', f'Image saved to {image_path}')
                self.title_input.clear()
                self.prompt_input.clear()
            except requests.RequestException as e:
                QMessageBox.critical(self, 'Error', f'Failed to download image: {str(e)}')
            except IOError as e:
                QMessageBox.critical(self, 'Error', f'Failed to save image: {str(e)}')

    def open_in_photo_editor(self):
        QMessageBox.information(self, "Feature Not Implemented", "Opening in photo editor is not yet implemented.")

    def view_full_size_image(self):
        QMessageBox.information(self, "Feature Not Implemented", "Viewing full-size image is not yet implemented.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = DalleImageGenerator()
    ex.show()
    sys.exit(app.exec())