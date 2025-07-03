import sys
import subprocess
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QTextEdit, QLabel
from PyQt5.QtCore import QThread, pyqtSignal

class DownloadThread(QThread):
    download_output = pyqtSignal(str)
    download_finished = pyqtSignal(int)

    def __init__(self, url):
        super().__init__()
        self.url = url

    def run(self):
        try:
            # yt-dlp 명령 실행
            process = subprocess.Popen(
                [sys.executable, '-m', 'yt_dlp', '-f', 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best', self.url],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                encoding='utf-8',
                errors='replace'
            )

            for line in process.stdout:
                self.download_output.emit(line.strip())
            
            process.wait()
            self.download_finished.emit(process.returncode)

        except Exception as e:
            self.download_output.emit(f"Error: {e}")
            self.download_finished.emit(1) # Indicate error

class YouTubeDownloader(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('YouTube Downloader')
        self.setGeometry(100, 100, 600, 400)

        main_layout = QVBoxLayout()

        # URL 입력 섹션
        url_layout = QHBoxLayout()
        self.url_label = QLabel('YouTube URL:')
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText('Enter YouTube video URL here')
        self.download_button = QPushButton('Download')
        self.download_button.clicked.connect(self.start_download)

        url_layout.addWidget(self.url_label)
        url_layout.addWidget(self.url_input)
        url_layout.addWidget(self.download_button)

        main_layout.addLayout(url_layout)

        # 출력 로그 섹션
        self.output_log = QTextEdit()
        self.output_log.setReadOnly(True)
        main_layout.addWidget(self.output_log)

        self.setLayout(main_layout)

        self.download_thread = None

    def start_download(self):
        url = self.url_input.text()
        if not url:
            self.output_log.append("Please enter a YouTube URL.")
            return

        self.output_log.clear()
        self.output_log.append(f"Starting download for: {url}")
        self.download_button.setEnabled(False)

        self.download_thread = DownloadThread(url)
        self.download_thread.download_output.connect(self.update_log)
        self.download_thread.download_finished.connect(self.download_complete)
        self.download_thread.start()

    def update_log(self, text):
        self.output_log.append(text)

    def download_complete(self, returncode):
        if returncode == 0:
            self.output_log.append("\nDownload finished successfully!")
        else:
            self.output_log.append(f"\nDownload failed with error code: {returncode}")
        self.download_button.setEnabled(True)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = YouTubeDownloader()
    ex.show()
    sys.exit(app.exec_())