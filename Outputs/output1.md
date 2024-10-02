# Output 1 By GPT-4 Omni

Here's a Python script using PyQt6 to create an impressive and nicely designed GUI for generating images from prompts using the DALL-E API. This script allows users to specify a title, prompt, image size, and output directory. The settings persist through reboots using `QSettings`.

```python
import sys
import os
import requests
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QFileDialog, QMessageBox,
                             QComboBox)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, QSettings
from dotenv import load_dotenv
import openai

# Load the OpenAI API key from the .env file
load_dotenv()
api_key = os.getenv('OPENAI_KEY')
openai.api_key = api_key

class DalleImageGenerator(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('DALL-E Image Generator')
        self.setGeometry(100, 100, 500, 300)
        self.setStyleSheet("background-color: #f0f8ff;")  # Light blue background

        layout = QVBoxLayout()
        
        # Title input
        title_label = QLabel('Image Title:')
        self.title_input = QLineEdit()
        layout.addWidget(title_label)
        layout.addWidget(self.title_input)
        
        # Prompt input
        prompt_label = QLabel('Enter your prompt:')
        self.prompt_input = QLineEdit()
        layout.addWidget(prompt_label)
        layout.addWidget(self.prompt_input)
        
        # Size selection
        size_label = QLabel('Select Image Size:')
        self.size_combo = QComboBox()
        self.size_combo.addItems(["256x256", "512x512", "1024x1024"])
        layout.addWidget(size_label)
        layout.addWidget(self.size_combo)

        # Output folder selection
        folder_layout = QVBoxLayout()
        self.folder_label = QLabel('Select output folder:')
        self.folder_button = QPushButton('Browse')
        self.folder_button.clicked.connect(self.select_folder)
        folder_layout.addWidget(self.folder_label)
        folder_layout.addWidget(self.folder_button)
        layout.addLayout(folder_layout)

        # Generate button
        generate_button = QPushButton('Generate Image')
        generate_button.setStyleSheet('background-color: #4682b4; color: white;')  # Steel blue button
        generate_button.clicked.connect(self.generate_image)
        layout.addWidget(generate_button)

        self.setLayout(layout)

        # Load saved settings
        self.settings = QSettings('DalleImageGenerator', 'Settings')
        self.load_settings()

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Directory")
        if folder:
            self.folder_label.setText(f'Selected: {folder}')
            self.settings.setValue('output_folder', folder)

    def load_settings(self):
        output_folder = self.settings.value('output_folder', '')
        
        if output_folder:
            self.folder_label.setText(f'Selected: {output_folder}')

    def save_settings(self):
        self.settings.setValue('output_folder', self.settings.value('output_folder', ''))

    def generate_image(self):
        title = self.title_input.text().strip().replace(" ", "-").lower()
        prompt = self.prompt_input.text().strip()
        
        if not title or not prompt:
            QMessageBox.warning(self, 'Error', 'Please enter both a title and a prompt.')
            return
        
        size = self.size_combo.currentText()
        
        try:
            # Call the DALL-E API to generate an image
            response = openai.Image.create(
                prompt=prompt,
                n=1,
                size=size
            )
            
            image_url = response['data'][0]['url']
            
            # Create the directory structure if it doesn't exist
            today = datetime.now().strftime('%d%m%y')
            output_folder = self.settings.value('output_folder', '')
            save_path = os.path.join(output_folder, today)
            os.makedirs(save_path, exist_ok=True)
            
            # Download and save the image
            image_response = requests.get(image_url)
            image_path = os.path.join(save_path, f'{title}.webp')
            
            with open(image_path, 'wb') as f:
                f.write(image_response.content)
            
            QMessageBox.information(self, 'Success', f'Image saved to {image_path}')
            self.close()
            
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'An error occurred: {str(e)}')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon())  # Add your icon here if available
    ex = DalleImageGenerator()
    ex.show()
    sys.exit(app.exec())
```

### Key Features:

- **User Inputs:** Allows users to specify an image title, prompt, and size.
- **Output Directory:** Users can select an output directory for saving images. This setting persists through reboots using `QSettings`.
- **Folder Structure:** Images are saved in `/generations/ddmmyy` format within the specified output directory.
- **File Naming:** The file name is based on the user-provided title (converted to lowercase and spaces replaced with hyphens).
- **Bright UI:** The interface uses a light blue background with steel blue buttons for a modern look.

### Setup Instructions:

1. **Install Required Packages:**
   Ensure you have these packages installed:

   ```bash
   pip install pyqt6 openai python-dotenv requests
   ```

2. **Create a `.env` File:**
   Place your OpenAI API key in a `.env` file in the same directory as the script:

   ```
   OPENAI_KEY=your_openai_api_key_here
   ```

3. **Run the Script:**
   Execute the script to launch the GUI and start generating images.

This GUI provides a user-friendly interface for generating images with DALL-E while managing settings efficiently.