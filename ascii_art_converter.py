import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QLabel, QFileDialog, QLineEdit, QComboBox
from PyQt5.QtGui import QPixmap, QImage, QFont, QFontDatabase
from PyQt5.QtCore import Qt
from PIL import Image

class AsciiArtConverter(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.image_path = None

    def initUI(self):
        self.setWindowTitle('ASCII Art Converter')
        self.setGeometry(100, 100, 800, 600)

        main_layout = QVBoxLayout()
        
        # Top section: Load Image, Convert, Save, Clear
        top_layout = QHBoxLayout()
        
        self.load_button = QPushButton('Load Image')
        self.load_button.clicked.connect(self.loadImage)
        top_layout.addWidget(self.load_button)

        self.convert_button = QPushButton('Convert to ASCII')
        self.convert_button.clicked.connect(self.convertToAscii)
        self.convert_button.setEnabled(False) # Disable until image is loaded
        top_layout.addWidget(self.convert_button)

        self.save_button = QPushButton('Save ASCII Art')
        self.save_button.clicked.connect(self.saveAsciiArt)
        self.save_button.setEnabled(False) # Disable until conversion
        top_layout.addWidget(self.save_button)

        self.clear_button = QPushButton('Clear')
        self.clear_button.clicked.connect(self.clearAll)
        top_layout.addWidget(self.clear_button)

        main_layout.addLayout(top_layout)

        # Settings section: Output Width and Character Set
        settings_layout = QHBoxLayout()

        settings_layout.addWidget(QLabel('Output Width:'))
        self.width_input = QLineEdit('100') # Default width
        self.width_input.setFixedWidth(50)
        settings_layout.addWidget(self.width_input)

        settings_layout.addWidget(QLabel('Character Set:'))
        self.char_set_combo = QComboBox()
        self.char_set_combo.addItem('''@%#*+=-:. ''') # Dark to Light (Simple)
        self.char_set_combo.addItem(''' .:-=+*#%@''') # Light to Dark (Simple)
        self.char_set_combo.addItem(''' .'`^",:;Il!i><~+_-?][}{1)(|\/tfjrxnumbROZCXJUVYPGQ$8&B@WM#''') # More detailed
        self.char_set_combo.addItem(''' .'`^",:;Il!i><~+_-?][}{1)(|\/tfjrxnumbROZCXJUVYPGQ$8&B@WM#'''.replace(" ", "")) # More detailed (no spaces)
        self.char_set_combo.addItem(''' .:-=+*#%@''') # Simple reversed
        self.char_set_combo.addItem(''' .:-=+*#%@'''.replace(" ", "")) # Simple reversed (no spaces)
        self.char_set_combo.addItem('''█▓▒░ ''') # Blocks
        self.char_set_combo.addItem('''░▒▓█''') # Blocks reversed
        self.char_set_combo.addItem('''MNHQ$OC?7>!:-;. ''') # Another common set
        self.char_set_combo.addItem('''$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,"^`'. ''') # Very detailed
        settings_layout.addWidget(self.char_set_combo)

        settings_layout.addStretch(1) # Push elements to the left
        main_layout.addLayout(settings_layout)

        # Image preview and ASCII art display section
        content_layout = QHBoxLayout()

        self.image_preview = QLabel('No Image Loaded')
        self.image_preview.setAlignment(Qt.AlignCenter)
        self.image_preview.setFixedSize(350, 400) # Fixed size for preview
        self.image_preview.setStyleSheet("border: 1px solid gray;")
        content_layout.addWidget(self.image_preview)

        self.ascii_output = QTextEdit()
        self.ascii_output.setReadOnly(True)
        # Set a fixed-width font for ASCII art display
        fixed_font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        fixed_font.setPointSize(5) # Adjust font size as needed
        self.ascii_output.setFont(fixed_font)
        self.ascii_output.setLineWrapMode(QTextEdit.NoWrap) # No word wrap
        content_layout.addWidget(self.ascii_output)

        main_layout.addLayout(content_layout)

        self.setLayout(main_layout)

    def clearAll(self):
        self.image_path = None
        self.image_preview.clear()
        self.image_preview.setText('No Image Loaded')
        self.ascii_output.clear()
        self.ascii_output.setText('')
        self.convert_button.setEnabled(False)
        self.save_button.setEnabled(False)

    def loadImage(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Load Image", "", 
                                                   "Image Files (*.png *.jpg *.jpeg *.bmp *.gif);;All Files (*)", 
                                                   options=options)
        if file_path:
            self.image_path = file_path
            
            # Display image preview
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                # Scale pixmap to fit the label while maintaining aspect ratio
                scaled_pixmap = pixmap.scaled(self.image_preview.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.image_preview.setPixmap(scaled_pixmap)
                self.image_preview.setText("") # Clear 'No Image Loaded' text
            else:
                self.image_preview.setText("Failed to load image")

            self.ascii_output.setText(f"Image loaded: {self.image_path}\nClick 'Convert to ASCII' to process.")
            self.convert_button.setEnabled(True)
            self.save_button.setEnabled(False) # Reset save button state

    def convertToAscii(self):
        if not self.image_path:
            self.ascii_output.setText("Please load an image first.")
            return

        try:
            img = Image.open(self.image_path).convert('L') # Convert to grayscale
            
            # Get settings from UI
            try:
                new_width = int(self.width_input.text())
                if new_width <= 0:
                    raise ValueError("Width must be a positive integer.")
            except ValueError as e:
                self.ascii_output.setText(f"Invalid Output Width: {e}")
                return

            chars = self.char_set_combo.currentText()

            # Resize image for ASCII art
            width, height = img.size
            aspect_ratio = height/width
            new_height = int(new_width * aspect_ratio * 0.55) # Adjust 0.55 for character aspect ratio
            img = img.resize((new_width, new_height))

            pixels = img.getdata()
            
            ascii_art = ""
            for pixel_value in pixels:
                # Map pixel brightness to ASCII character
                index = int((pixel_value / 255) * (len(chars) - 1))
                ascii_art += chars[index]
            
            # Add newlines to form the image
            final_ascii_art = ""
            for i in range(0, len(ascii_art), new_width):
                final_ascii_art += ascii_art[i:i+new_width] + "\n"

            self.ascii_output.setText(final_ascii_art)
            self.save_button.setEnabled(True)

        except Exception as e:
            self.ascii_output.setText(f"Error during conversion: {e}")
            self.save_button.setEnabled(False)

    def saveAsciiArt(self):
        if not self.ascii_output.toPlainText():
            self.ascii_output.setText("Nothing to save. Convert an image first.")
            return

        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Save ASCII Art", "ascii_art.txt", 
                                                   "Text Files (*.txt);;All Files (*)", 
                                                   options=options)
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.ascii_output.toPlainText())
                self.ascii_output.append(f"\nASCII art saved to: {file_path}")
            except Exception as e:
                self.ascii_output.append(f"\nError saving file: {e}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = AsciiArtConverter()
    ex.show()
    sys.exit(app.exec_())