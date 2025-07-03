import sys
import os
import random
import json
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QLineEdit, QVBoxLayout, QHBoxLayout
from PyQt5.QtGui import QFont, QColor, QPainter
from PyQt5.QtCore import Qt, QTimer

class Word:
    def __init__(self, text, x, y, speed):
        self.text = text
        self.x = x
        self.y = y
        self.speed = speed

class WordErasingGame(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('글자 없애기 게임')
        self.resolution = (800, 600)
        self.setFixedSize(self.resolution[0], self.resolution[1])
        self.center_window()

        self.words = []
        self.score = 0
        self.game_over_flag = False
        self.paused = False
        self.language = 'korean'
        self.difficulty = 'normal'
        self.game_in_progress = False

        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.word_list_kor = self.load_words(os.path.join(script_dir, 'korean_words.txt'))
        self.word_list_eng = self.load_words(os.path.join(script_dir, 'english_words.txt'))

        self.high_scores_file = os.path.join(script_dir, 'high_scores.json')
        self.high_scores = self.load_high_scores()

        # Timers are created once and reused
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_game)
        self.word_creation_timer = QTimer(self)
        self.word_creation_timer.timeout.connect(self.create_word)

        # Central layout that will be cleared and populated for each screen
        self.main_layout = QVBoxLayout(self)
        self.setLayout(self.main_layout)

        self.main_menu()

    def center_window(self):
        screen = QApplication.desktop().screenGeometry()
        self.move((screen.width() - self.width()) // 2, (screen.height() - self.height()) // 2)

    def clear_layout(self):
        while self.main_layout.count():
            item = self.main_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()

    def load_high_scores(self):
        if not os.path.exists(self.high_scores_file):
            return {'korean': {'easy': 0, 'normal': 0, 'hard': 0},
                    'english': {'easy': 0, 'normal': 0, 'hard': 0}}
        with open(self.high_scores_file, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {'korean': {'easy': 0, 'normal': 0, 'hard': 0},
                        'english': {'easy': 0, 'normal': 0, 'hard': 0}}

    def save_high_scores(self):
        with open(self.high_scores_file, 'w', encoding='utf-8') as f:
            json.dump(self.high_scores, f, indent=4, ensure_ascii=False)

    def main_menu(self):
        self.game_in_progress = False
        self.clear_layout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        title = QLabel('글자 없애기 게임')
        title.setFont(QFont('Arial', 50, QFont.Bold))
        title.setStyleSheet("color: #8B4513;")
        title.setAlignment(Qt.AlignCenter)

        start_button = self.create_button('게임 시작', self.language_selection)
        settings_button = self.create_button('설정', self.settings_menu)
        exit_button = self.create_button('나가기', self.close)

        self.main_layout.addStretch(1)
        self.main_layout.addWidget(title)
        self.main_layout.addSpacing(30)
        self.main_layout.addWidget(start_button, alignment=Qt.AlignCenter)
        self.main_layout.addWidget(settings_button, alignment=Qt.AlignCenter)
        self.main_layout.addWidget(exit_button, alignment=Qt.AlignCenter)
        self.main_layout.addStretch(1)

        self.show()

    def language_selection(self):
        self.clear_layout()

        kor_button = self.create_button('한국어', lambda: self.set_language('korean'))
        eng_button = self.create_button('English', lambda: self.set_language('english'))

        self.main_layout.addStretch(1)
        self.main_layout.addWidget(kor_button, alignment=Qt.AlignCenter)
        self.main_layout.addWidget(eng_button, alignment=Qt.AlignCenter)
        self.main_layout.addStretch(1)

    def set_language(self, lang):
        self.language = lang
        self.difficulty_selection()

    def difficulty_selection(self):
        self.clear_layout()

        easy_button = self.create_button('Easy', lambda: self.start_game('easy'))
        normal_button = self.create_button('Normal', lambda: self.start_game('normal'))
        hard_button = self.create_button('Hard', lambda: self.start_game('hard'))

        self.main_layout.addStretch(1)
        self.main_layout.addWidget(easy_button, alignment=Qt.AlignCenter)
        self.main_layout.addWidget(normal_button, alignment=Qt.AlignCenter)
        self.main_layout.addWidget(hard_button, alignment=Qt.AlignCenter)
        self.main_layout.addStretch(1)

    def start_game(self, difficulty):
        self.difficulty = difficulty
        self.game_in_progress = True
        self.clear_layout()
        self.game_over_flag = False
        self.score = 0
        self.words = []

        current_high_score = self.high_scores[self.language][self.difficulty]
        self.score_label = QLabel(f'Score: {self.score} (High: {current_high_score})', self)
        self.score_label.setFont(QFont('Arial', 15))
        self.score_label.move(10, 10)
        self.score_label.show()

        self.input_box = QLineEdit(self)
        self.input_box.setGeometry(self.width() // 2 - 100, self.height() - 50, 200, 30)
        self.input_box.show()
        self.input_box.returnPressed.connect(self.check_word)

        self.pause_button = QPushButton('일시정지', self)
        self.pause_button.setFont(QFont('Arial', 12))
        self.pause_button.setGeometry(self.width() - 110, 10, 100, 40)
        self.pause_button.show()
        self.pause_button.clicked.connect(self.toggle_pause)

        self.timer.start(16)
        self.word_creation_timer.start(self.get_word_creation_interval())

        self.input_box.setFocus()
        self.update()

    def update_game(self):
        if not self.paused and not self.game_over_flag:
            for word in self.words[:]:
                word.y += word.speed
                if word.y > self.height():
                    self.game_over()
                    break
            self.update()

    def create_word(self):
        if not self.paused and not self.game_over_flag:
            word_list = self.word_list_kor if self.language == 'korean' else self.word_list_eng
            text = random.choice(word_list)
            x = random.randint(50, self.width() - 150)
            speed = self.get_word_speed()
            self.words.append(Word(text, x, 100, speed))

    def check_word(self):
        if not self.paused and not self.game_over_flag:
            input_text = self.input_box.text()
            for word in self.words[:]:
                if word.text == input_text:
                    self.words.remove(word)
                    self.score += 1
                    current_high_score = self.high_scores[self.language][self.difficulty]
                    self.score_label.setText(f'Score: {self.score} (High: {current_high_score})')
                    break
            self.input_box.clear()

    def game_over(self):
        self.game_in_progress = False
        self.game_over_flag = True
        self.timer.stop()
        self.word_creation_timer.stop()

        # Update high score
        if self.score > self.high_scores[self.language][self.difficulty]:
            self.high_scores[self.language][self.difficulty] = self.score
            self.save_high_scores()

        # Manually hide game-specific widgets
        self.score_label.hide()
        self.input_box.hide()
        self.pause_button.hide()

        self.clear_layout()

        game_over_label = QLabel('Game Over')
        game_over_label.setFont(QFont('Arial', 50, QFont.Bold))
        score_label = QLabel(f'Total Score: {self.score}')
        score_label.setFont(QFont('Arial', 30))
        high_score_label = QLabel(f'High Score: {self.high_scores[self.language][self.difficulty]}')
        high_score_label.setFont(QFont('Arial', 20))

        restart_button = self.create_button('다시 시작', self.main_menu)
        exit_button = self.create_button('나가기', self.close)

        self.main_layout.addStretch(1)
        self.main_layout.addWidget(game_over_label, alignment=Qt.AlignCenter)
        self.main_layout.addWidget(score_label, alignment=Qt.AlignCenter)
        self.main_layout.addWidget(high_score_label, alignment=Qt.AlignCenter)
        self.main_layout.addSpacing(30)
        self.main_layout.addWidget(restart_button, alignment=Qt.AlignCenter)
        self.main_layout.addWidget(exit_button, alignment=Qt.AlignCenter)
        self.main_layout.addStretch(1)

    def toggle_pause(self):
        if not self.game_in_progress: return
        self.paused = not self.paused
        if self.paused:
            self.pause_button.setText('계속')
            self.timer.stop()
            self.word_creation_timer.stop()
            self.show_pause_menu()
        else:
            self.pause_button.setText('일시정지')
            self.timer.start()
            self.word_creation_timer.start()
            self.hide_pause_menu()
            self.input_box.setFocus()

    def show_pause_menu(self):
        self.pause_menu = QWidget(self)
        self.pause_menu.setGeometry(0, 0, self.width(), self.height())
        self.pause_menu.setStyleSheet("background-color: rgba(0, 0, 0, 150);")
        layout = QVBoxLayout(self.pause_menu)
        exit_button = self.create_button('나가기', self.exit_to_main_menu_from_pause)
        layout.addWidget(exit_button, alignment=Qt.AlignCenter)
        self.pause_menu.show()

    def exit_to_main_menu_from_pause(self):
        self.timer.stop()
        self.word_creation_timer.stop()

        # Manually hide game-specific widgets
        if hasattr(self, 'score_label'):
            self.score_label.hide()
        if hasattr(self, 'input_box'):
            self.input_box.hide()
        if hasattr(self, 'pause_button'):
            self.pause_button.hide()

        self.paused = False
        self.hide_pause_menu()
        self.main_menu()

    def hide_pause_menu(self):
        if hasattr(self, 'pause_menu') and self.pause_menu:
            self.pause_menu.hide()
            self.pause_menu.deleteLater()
            self.pause_menu = None

    def settings_menu(self):
        self.clear_layout()

        settings_label = QLabel("설정")
        settings_label.setFont(QFont("Arial", 30, QFont.Bold))

        res_layout = QHBoxLayout()
        prev_button = self.create_button('<', self.prev_resolution, fixed_size=False)
        self.resolution_label = QLabel(f'해상도: {self.resolution[0]} x {self.resolution[1]}')
        self.resolution_label.setFont(QFont('Arial', 20))
        next_button = self.create_button('>', self.next_resolution, fixed_size=False)
        res_layout.addWidget(prev_button)
        res_layout.addWidget(self.resolution_label, alignment=Qt.AlignCenter)
        res_layout.addWidget(next_button)

        confirm_button = self.create_button("확인", self.apply_settings)
        back_button = self.create_button("뒤로가기", self.main_menu)

        self.main_layout.addStretch(1)
        self.main_layout.addWidget(settings_label, alignment=Qt.AlignCenter)
        self.main_layout.addLayout(res_layout)
        self.main_layout.addWidget(confirm_button, alignment=Qt.AlignCenter)
        self.main_layout.addWidget(back_button, alignment=Qt.AlignCenter)
        self.main_layout.addStretch(1)

    def prev_resolution(self):
        resolutions = [(640, 480), (800, 600), (1280, 720), (1920, 1080)]
        try:
            index = resolutions.index(self.resolution)
            if index > 0:
                self.resolution = resolutions[index - 1]
                self.resolution_label.setText(f'해상도: {self.resolution[0]} x {self.resolution[1]}')
        except ValueError:
            pass

    def next_resolution(self):
        resolutions = [(640, 480), (800, 600), (1280, 720), (1920, 1080)]
        try:
            index = resolutions.index(self.resolution)
            if index < len(resolutions) - 1:
                self.resolution = resolutions[index + 1]
                self.resolution_label.setText(f'해상도: {self.resolution[0]} x {self.resolution[1]}')
        except ValueError:
            pass

    def apply_settings(self):
        self.setFixedSize(self.resolution[0], self.resolution[1])
        self.center_window()
        self.main_menu()

    def get_word_speed(self):
        base_speed = 1.0
        if self.difficulty == 'normal':
            base_speed = 1.5
        elif self.difficulty == 'hard':
            base_speed = 2.0
        return base_speed * (self.height() / 600)

    def get_word_creation_interval(self):
        interval = 1000
        if self.difficulty == 'easy':
            interval = 2000
        elif self.difficulty == 'normal':
            interval = 1320
        elif self.difficulty == 'hard':
            interval = 660
        return interval

    def load_words(self, filename):
        with open(filename, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f]

    def create_button(self, text, callback, fixed_size=True):
        button = QPushButton(text)
        button.setFont(QFont('Arial', 18))
        if fixed_size:
            button.setFixedSize(120, 80)
        button.clicked.connect(callback)
        return button

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.fillRect(self.rect(), QColor('#87CEEB'))

        painter.setBrush(QColor('#A9A9A9'))
        painter.drawRect(0, 0, self.width(), 100)

        if self.game_in_progress:
            painter.setPen(QColor('black'))
            painter.setFont(QFont('Arial', 18))
            for word in self.words:
                painter.drawText(word.x, int(word.y), word.text)

    def keyPressEvent(self, event):
        if self.game_in_progress and event.key() == Qt.Key_Escape:
            self.toggle_pause()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    game = WordErasingGame()
    sys.exit(app.exec_())