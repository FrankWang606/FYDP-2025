import sys
import os
import subprocess
import threading
import time
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QHBoxLayout, QComboBox
from PyQt5.QtGui import QColor, QPalette
import pyautogui

class GestureApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.process = None
        self.running = True
        self.key_bindings = [""] * 6  # 存储每个手势对应的按键绑定

    def initUI(self):
        self.setWindowTitle('Gesture Detection App')

        layout = QVBoxLayout()

        self.start_button = QPushButton('Start', self)
        self.start_button.clicked.connect(self.start_detection)
        layout.addWidget(self.start_button)

        gestures = ["thumb up", "thumb down", "wave", "pinch in", "palm flip", "record"]
        keys = ["", "up", "down", "left", "right", "enter", "double click", "right click"]

        self.blocks = []
        self.combos = []
        for gesture in gestures:
            block_layout = QHBoxLayout()
            
            block_label = QLabel(gesture, self)
            block_label.setFixedSize(100, 100)
            
            block = QLabel(self)
            block.setAutoFillBackground(True)
            block.setFixedSize(200, 100)
            palette = block.palette()
            palette.setColor(QPalette.Window, QColor('white'))
            block.setPalette(palette)
            
            combo = QComboBox(self)
            combo.addItems(keys)
            combo.currentIndexChanged.connect(self.update_key_bindings)
            
            block_layout.addWidget(block_label)
            block_layout.addWidget(block)
            block_layout.addWidget(combo)
            layout.addLayout(block_layout)
            
            self.blocks.append(block)
            self.combos.append(combo)

        self.exit_button = QPushButton('Exit', self)
        self.exit_button.clicked.connect(self.exit_application)
        layout.addWidget(self.exit_button)

        self.setLayout(layout)

    def update_key_bindings(self):
        for i, combo in enumerate(self.combos):
            self.key_bindings[i] = combo.currentText()

    def start_detection(self):
        self.running = True
        self.process = subprocess.Popen(["python", "main_gesture.py"])
        threading.Thread(target=self.update_color_blocks, daemon=True).start()

    def update_color_blocks(self):
        colors = ["white", "white", "white", "white", "white", "white"]
        while self.running:
            if os.path.exists("gesture.txt"):
                with open("gesture.txt", "r") as file:
                    lines = file.readlines()
                    if lines:
                        try:
                            state = int(lines[-1].strip())
                            if state == 0:
                                colors = ["red", "white", "white", "white", "white", "white"]
                            elif state == 1:
                                colors = ["white", "green", "white", "white", "white", "white"]
                            elif state == 2:
                                colors = ["white", "white", "blue", "white", "white", "white"]
                            elif state == 3:
                                colors = ["white", "white", "white", "yellow", "white", "white"]
                            elif state == 4:
                                colors = ["white", "white", "white", "white", "purple", "white"]
                            elif state == 5:
                                colors = ["white", "white", "white", "white", "white", "white"]
                            else:
                                colors = ["white", "white", "white", "white", "white", "white"]

                            # 执行按键绑定
                            if state in range(6) and self.key_bindings[state]:
                                action = self.key_bindings[state]
                                if action == "double click":
                                    pyautogui.doubleClick()
                                elif action == "right click":
                                    pyautogui.rightClick()
                                else:
                                    pyautogui.press(action)
                        except ValueError:
                            colors = ["white", "white", "white", "white", "white", "white"]

                        for i, color in enumerate(colors):
                            palette = self.blocks[i].palette()
                            palette.setColor(QPalette.Window, QColor(color))
                            self.blocks[i].setPalette(palette)
                        time.sleep(2)

    def exit_application(self):
        self.running = False
        if self.process:
            self.process.terminate()
            self.process.wait()
        QApplication.instance().quit()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = GestureApp()
    ex.show()
    sys.exit(app.exec_())