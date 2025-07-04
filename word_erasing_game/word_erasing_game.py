import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QMessageBox
from PyQt5.QtGui import QColor, QPalette, QFont
from PyQt5.QtCore import Qt, QTimer, QPoint
import random

# FallingWord 클래스 정의
class FallingWord(QLabel):
    def __init__(self, word, parent=None):
        super().__init__(word, parent)
        self.word = word
        self.speed = 0 # 난이도에 따라 설정될 속도
        self.y_pos = 0 # 초기 y 위치
        self.x_pos = 0 # 초기 x 위치 (랜덤하게 설정)
        self.setFont(QFont("Arial", 28, QFont.Bold))
        self.setStyleSheet("color: black;")
        self.setAlignment(Qt.AlignCenter)
        self.adjustSize()

    def move_down(self):
        self.y_pos += self.speed
        self.move(int(self.x_pos), int(self.y_pos))

class WordErasingGame(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("글자 없애기 게임")
        self.setFixedSize(800, 600) # 기본 윈도우 크기 800x600으로 고정

        self.resolutions = [(640, 480), (800, 600), (1280, 720), (1920, 1080)]
        self.current_resolution_index = 1 # 800x600이 기본

        self.current_difficulty = None
        self.current_language = None
        self.score = 0
        self.words = [] # 현재 게임에서 사용할 단어 목록
        self.falling_words = [] # 현재 화면에 떨어지고 있는 FallingWord 객체들
        self.game_running = False

        self.game_timer = QTimer(self) # 단어 낙하 및 게임 로직 업데이트 타이머
        self.game_timer.timeout.connect(self.update_game)

        self.word_spawn_timer = QTimer(self) # 새 단어 생성 타이머
        self.word_spawn_timer.timeout.connect(self.spawn_new_word)

        self.init_ui()

    def init_ui(self):
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.show_main_menu()

    def load_words(self, language):
        file_path = ""
        if language == "korean":
            file_path = "C:\\Users\\SBA\\github\\gemini-cli-tutorial\\korean_words.txt"
        elif language == "english":
            file_path = "C:\\Users\\SBA\\github\\gemini-cli-tutorial\\english_words.txt"

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                self.words = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            QMessageBox.critical(self, "오류", f"{file_path} 파일을 찾을 수 없습니다.")
            self.words = []

    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clear_layout(item.layout())

    def show_language_selection(self):
        self.clear_layout(self.main_layout)

        language_label = QLabel("언어 선택")
        language_label.setFont(QFont("Arial", 36, QFont.Bold))
        language_label.setAlignment(Qt.AlignCenter)
        language_label.setStyleSheet("color: black;")

        korean_button = QPushButton("한글")
        korean_button.setFont(QFont("Arial", 20))
        korean_button.clicked.connect(lambda: self.set_language_and_show_difficulty("korean"))
        korean_button.setFixedSize(250, 60)

        english_button = QPushButton("영어")
        english_button.setFont(QFont("Arial", 20))
        english_button.clicked.connect(lambda: self.set_language_and_show_difficulty("english"))
        english_button.setFixedSize(250, 60)

        back_button = QPushButton("뒤로가기")
        back_button.setFont(QFont("Arial", 18))
        back_button.clicked.connect(self.show_main_menu) # Back to main menu
        back_button.setFixedSize(150, 50)

        language_layout = QVBoxLayout()
        language_layout.addStretch(1)
        language_layout.addWidget(language_label, alignment=Qt.AlignCenter)
        language_layout.addWidget(korean_button, alignment=Qt.AlignCenter)
        language_layout.addWidget(english_button, alignment=Qt.AlignCenter)
        language_layout.addSpacing(30)
        language_layout.addWidget(back_button, alignment=Qt.AlignCenter)
        language_layout.addStretch(1)

        self.main_layout.addLayout(language_layout)
        self.set_background_color(QColor("#87CEEB")) # 하늘색 (SkyBlue)

    def set_language_and_show_difficulty(self, language):
        self.current_language = language
        self.load_words(language)
        if not self.words:
            QMessageBox.critical(self, "오류", "단어 로드에 실패했습니다. 언어 선택 화면으로 돌아갑니다.")
            self.show_language_selection() # 단어 로드 실패 시 언어 선택 화면으로 돌아감
            return
        self.show_difficulty_selection()

    def show_difficulty_selection(self):
        self.clear_layout(self.main_layout)

        difficulty_label = QLabel("난이도 선택")
        difficulty_label.setFont(QFont("Arial", 36, QFont.Bold))
        difficulty_label.setAlignment(Qt.AlignCenter)
        difficulty_label.setStyleSheet("color: black;")

        easy_button = QPushButton("Easy")
        easy_button.setFont(QFont("Arial", 20))
        easy_button.clicked.connect(lambda: self.start_game("easy"))
        easy_button.setFixedSize(250, 60)

        normal_button = QPushButton("Normal")
        normal_button.setFont(QFont("Arial", 20))
        normal_button.clicked.connect(lambda: self.start_game("normal"))
        normal_button.setFixedSize(250, 60)

        hard_button = QPushButton("Hard")
        hard_button.setFont(QFont("Arial", 20))
        hard_button.clicked.connect(lambda: self.start_game("hard"))
        hard_button.setFixedSize(250, 60)

        back_button = QPushButton("뒤로가기")
        back_button.setFont(QFont("Arial", 18))
        back_button.clicked.connect(self.show_language_selection) # Back to language selection
        back_button.setFixedSize(150, 50)

        difficulty_layout = QVBoxLayout()
        difficulty_layout.addStretch(1)
        difficulty_layout.addWidget(difficulty_label, alignment=Qt.AlignCenter)
        difficulty_layout.addWidget(easy_button, alignment=Qt.AlignCenter)
        difficulty_layout.addWidget(normal_button, alignment=Qt.AlignCenter)
        difficulty_layout.addWidget(hard_button, alignment=Qt.AlignCenter)
        difficulty_layout.addSpacing(30)
        difficulty_layout.addWidget(back_button, alignment=Qt.AlignCenter)
        difficulty_layout.addStretch(1)

        self.main_layout.addLayout(difficulty_layout)
        self.set_background_color(QColor("#87CEEB")) # 하늘색 (SkyBlue)

    def show_main_menu(self):
        self.clear_layout(self.main_layout)
        self.game_timer.stop()
        self.word_spawn_timer.stop()
        for word_obj in self.falling_words:
            word_obj.deleteLater()
        self.falling_words.clear()

        if hasattr(self, 'pause_overlay') and self.pause_overlay.isVisible():
            self.pause_overlay.hide() # 메인 메뉴로 돌아올 때 일시정지 오버레이 숨기기

        # Title
        title_label = QLabel("글자 없애기 게임")
        title_font = QFont("Arial", 48, QFont.Bold) # 폰트 추천: Arial Bold
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #A0522D;") # 연갈색 (Sienna)

        # Buttons
        start_button = QPushButton("게임시작")
        start_button.setFont(QFont("Arial", 24))
        start_button.clicked.connect(self.show_language_selection) # 언어 선택 화면으로 연결
        start_button.setFixedSize(200, 70)

        settings_button = QPushButton("설정")
        settings_button.setFont(QFont("Arial", 24))
        settings_button.clicked.connect(self.show_settings_menu_from_main)
        settings_button.setFixedSize(200, 70)

        exit_button = QPushButton("나가기")
        exit_button.setFont(QFont("Arial", 24))
        exit_button.clicked.connect(self.close)
        exit_button.setFixedSize(200, 70)

        button_layout = QVBoxLayout()
        button_layout.addStretch(1)
        button_layout.addWidget(start_button, alignment=Qt.AlignCenter)
        button_layout.addWidget(settings_button, alignment=Qt.AlignCenter)
        button_layout.addWidget(exit_button, alignment=Qt.AlignCenter)
        button_layout.addStretch(1)

        self.main_layout.addWidget(title_label)
        self.main_layout.addLayout(button_layout)

        self.set_background_color(QColor("#87CEEB")) # 하늘색 (SkyBlue)

    def _create_settings_ui(self, return_callback):
        self.confirm_button = QPushButton("확인")
        self.confirm_button.setFont(QFont("Arial", 24))
        self.confirm_button.clicked.connect(return_callback)
        self.confirm_button.setFixedSize(200, 70)

        self.back_button = QPushButton("뒤로가기")
        self.back_button.setFont(QFont("Arial", 18))
        self.back_button.clicked.connect(return_callback)
        self.back_button.setFixedSize(150, 50)

        settings_layout = QVBoxLayout()
        settings_layout.addStretch(1)
        settings_layout.addWidget(settings_label, alignment=Qt.AlignCenter)
        settings_layout.addLayout(resolution_change_layout)
        settings_layout.addSpacing(30)
        settings_layout.addWidget(confirm_button, alignment=Qt.AlignCenter)
        settings_layout.addWidget(back_button, alignment=Qt.AlignCenter)
        settings_layout.addStretch(1)

        self.main_layout.addLayout(settings_layout)
        self.set_background_color(QColor("#87CEEB")) # 하늘색 (SkyBlue)

    def show_settings_menu_from_main(self):
        self.clear_layout(self.main_layout)
        self._create_settings_ui(self.apply_resolution_and_return_to_main)

    def show_settings_menu_from_pause(self):
        self.clear_layout(self.main_layout)
        if hasattr(self, 'pause_overlay'):
            self.pause_overlay.hide() # 일시정지 오버레이 숨기기
        self._create_settings_ui(self.apply_resolution_and_return_to_pause_menu)

    def prev_resolution(self):
        self.current_resolution_index = (self.current_resolution_index - 1) % len(self.resolutions)
        self.update_resolution_display()

    def next_resolution(self):
        self.current_resolution_index = (self.current_resolution_index + 1) % len(self.resolutions)
        self.update_resolution_display()

    def update_resolution_display(self):
        width, height = self.resolutions[self.current_resolution_index]
        self.resolution_display_label.setText(f"{width} x {height}")

    def apply_resolution_and_return_to_main(self):
        width, height = self.resolutions[self.current_resolution_index]
        self.setFixedSize(width, height)
        self.show_main_menu()

    def apply_resolution_and_return_to_pause_menu(self):
        width, height = self.resolutions[self.current_resolution_index]
        self.setFixedSize(width, height)
        self.resume_game()

    def start_game(self, difficulty):
        self.current_difficulty = difficulty
        self.score = 0
        self.clear_layout(self.main_layout)
        self.game_running = True
        self.falling_words.clear() # 기존 단어들 초기화

        # Top Bar (Score and Pause Button)
        top_bar_layout = QHBoxLayout()
        self.score_label = QLabel(f"점수: {self.score}")
        self.score_label.setFont(QFont("Arial", 24, QFont.Bold))
        self.score_label.setStyleSheet("color: black;")
        top_bar_layout.addWidget(self.score_label, alignment=Qt.AlignLeft | Qt.AlignTop)
        top_bar_layout.addStretch(1) # Push score to left

        pause_button = QPushButton("일시정지")
        pause_button.setFont(QFont("Arial", 18))
        pause_button.clicked.connect(self.show_pause_menu)
        pause_button.setFixedSize(100, 40)
        top_bar_layout.addWidget(pause_button, alignment=Qt.AlignRight | Qt.AlignTop)

        # Input Field
        self.input_field = QLineEdit()
        self.input_field.setFont(QFont("Arial", 24))
        self.input_field.setStyleSheet("background-color: white; color: black;")
        self.input_field.setPlaceholderText("여기에 단어를 입력하세요...")
        self.input_field.returnPressed.connect(self.check_word) # Enter 키 입력 시 단어 확인

        # 구름 표현 (QLabel 사용) - 메인 윈도우의 자식으로 생성
        self.cloud_label = QLabel(self) # 메인 윈도우의 자식으로 생성
        self.cloud_label.setFixedHeight(100) # 구름 높이 고정
        self.cloud_label.setStyleSheet("background-color: #A9A9A9; border-bottom-left-radius: 50px; border-bottom-right-radius: 50px;") # 회색 구름
        self.cloud_label.show()

        # Game Screen Layout
        self.game_area = QWidget(self) # 단어들이 떨어질 영역
        self.game_area.setStyleSheet("background-color: transparent;") # 배경 투명하게

        # Main layout for game screen
        self.main_layout.addLayout(top_bar_layout) # 점수/일시정지 버튼을 가장 먼저 추가
        self.main_layout.addWidget(self.cloud_label) # 그 다음 구름 추가
        self.main_layout.addWidget(self.game_area, 1) # 단어 떨어지는 영역이 남은 공간을 차지하도록 stretch factor 1 부여
        self.main_layout.addWidget(self.input_field)

        self.set_background_color(QColor("#ADD8E6")) # 밝은 하늘색 (LightBlue)

        # Set speed based on difficulty and resolution
        base_speed = 0 # 픽셀/프레임 (나중에 해상도에 비례하여 조정)
        if difficulty == "easy":
            base_speed = 2
            self.spawn_interval = 2000 # 2초마다 단어 생성
        elif difficulty == "normal":
            base_speed = 4
            self.spawn_interval = 1500 # 1.5초마다 단어 생성
        elif difficulty == "hard":
            base_speed = 6
            self.spawn_interval = 1000 # 1초마다 단어 생성

        # 단어 속도를 화면 높이에 비례하여 조정
        # 기준 해상도 높이를 480으로 가정 (가장 작은 해상도)
        reference_height = 480
        self.word_speed = base_speed * (self.height() / reference_height)

        self.game_timer.start(30) # 약 30ms마다 업데이트 (초당 약 33프레임)
        self.word_spawn_timer.start(self.spawn_interval)

    def spawn_new_word(self):
        if not self.words:
            QMessageBox.warning(self, "경고", "선택된 언어의 단어 목록이 비어있습니다. 게임을 종료합니다.")
            self.game_over()
            return

        word_text = random.choice(self.words)
        new_word_obj = FallingWord(word_text, self.game_area) # game_area를 부모로 설정
        new_word_obj.speed = self.word_speed

        # 단어의 x 위치를 랜덤하게 설정 (화면 너비 내에서)
        max_x = self.game_area.width() - new_word_obj.width()
        new_word_obj.x_pos = random.randint(0, max_x) if max_x > 0 else 0
        new_word_obj.y_pos = 0 # game_area의 맨 위에서 시작
        new_word_obj.move(new_word_obj.x_pos, new_word_obj.y_pos)
        new_word_obj.show()
        self.falling_words.append(new_word_obj)

    def update_game(self):
        words_to_remove = []
        game_over_triggered = False

        for word_obj in self.falling_words:
            word_obj.move_down()
            # 단어가 화면 하단에 닿았는지 확인
            if word_obj.y_pos > self.game_area.height():
                words_to_remove.append(word_obj)
                game_over_triggered = True # 단어가 바닥에 닿으면 게임 오버

        for word_obj in words_to_remove:
            self.falling_words.remove(word_obj)
            word_obj.deleteLater() # 위젯 삭제

        if game_over_triggered:
            self.game_over()

    def check_word(self):
        typed_word = self.input_field.text().strip()
        self.input_field.clear()

        matched_word_obj = None
        for word_obj in self.falling_words:
            if word_obj.word == typed_word:
                matched_word_obj = word_obj
                break

        if matched_word_obj:
            self.score += 1
            self.score_label.setText(f"점수: {self.score}")
            self.falling_words.remove(matched_word_obj)
            matched_word_obj.deleteLater() # 위젯 삭제
        else:
            # 틀렸을 경우 처리 (예: 경고 메시지)
            pass # 현재는 아무것도 하지 않음

    def show_pause_menu(self):
        self.game_timer.stop()
        self.word_spawn_timer.stop()
        self.game_running = False

        # 반투명 배경 위젯
        if not hasattr(self, 'pause_overlay'): # pause_overlay가 없으면 새로 생성
            self.pause_overlay = QWidget(self)
            self.pause_overlay.setGeometry(0, 0, self.width(), self.height())
            self.pause_overlay.setStyleSheet("background-color: rgba(0, 0, 0, 128);") # 반투명 검은색

            # 일시정지 메뉴 레이아웃
            pause_layout = QVBoxLayout(self.pause_overlay)
            pause_layout.setAlignment(Qt.AlignCenter)

            resume_button = QPushButton("계속하기")
            resume_button.setFont(QFont("Arial", 24))
            resume_button.setFixedSize(200, 70)
            resume_button.clicked.connect(self.resume_game)

            settings_button = QPushButton("설정")
            settings_button.setFont(QFont("Arial", 24))
            settings_button.setFixedSize(200, 70)
            settings_button.clicked.connect(self.show_settings_menu_from_pause) # 설정 메뉴 함수 (일시정지 메뉴에서 호출)

            exit_button = QPushButton("나가기")
            exit_button.setFont(QFont("Arial", 24))
            exit_button.setFixedSize(200, 70)
            exit_button.clicked.connect(self.game_over)

            pause_layout.addWidget(resume_button, alignment=Qt.AlignCenter)
            pause_layout.addWidget(settings_button, alignment=Qt.AlignCenter)
            pause_layout.addWidget(exit_button, alignment=Qt.AlignCenter)
        
        self.pause_overlay.show() # 항상 보이도록

    def resume_game(self):
        self.clear_layout(self.main_layout) # 설정 화면 레이아웃 정리
        self.pause_overlay.hide()
        self.game_timer.start(30)
        self.word_spawn_timer.start(self.spawn_interval)
        self.game_running = True

    def game_over(self):
        self.game_running = False
        self.game_timer.stop()
        self.word_spawn_timer.stop()

        # 모든 떨어지는 단어 제거
        for word_obj in self.falling_words:
            word_obj.deleteLater()
        self.falling_words.clear()

        if hasattr(self, 'pause_overlay'):
            self.pause_overlay.hide() # 일시정지 메뉴 숨기기

        QMessageBox.information(self, "게임 오버!", f"총 점수: {self.score}점")
        self.show_main_menu()

    def set_background_color(self, color):
        palette = self.palette()
        palette.setColor(QPalette.Window, color)
        self.setPalette(palette)
        self.setAutoFillBackground(True)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            if self.game_running:
                self.show_pause_menu()
            elif hasattr(self, 'pause_overlay') and self.pause_overlay.isVisible():
                self.resume_game()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    game = WordErasingGame()
    game.show()
    sys.exit(app.exec_())