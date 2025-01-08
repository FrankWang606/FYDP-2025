import sys
import os
import subprocess
import threading
import time
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QHBoxLayout, QComboBox
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QTimer,Qt
import pyautogui

class GestureApp(QWidget):
    
    def show_auto_closing_message_box(self, message, duration=1500):
        """显示一个自动消失的 QMessageBox"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Notification")
        msg_box.setText(message)
        # msg_box.setStandardButtons(QMessageBox.NoButton)  # 去掉按钮
        msg_box.setStyleSheet("background-color: lightblue;")  # 可选：设置样式
        msg_box.show()

        # 使用 QTimer 在指定时间后关闭消息框
        QTimer.singleShot(duration, msg_box.close)
    
    def __init__(self):
        super().__init__()
        self.initUI()
        self.process = None
        self.running = True
        self.key_bindings = [""] * 6  # 存储每个手势对应的按键绑定

    def initUI(self):
        self.setWindowTitle('Gesture Detection App')

        self.setStyleSheet("""

            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3e8e41;
            }
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #333;
            }
            QComboBox {
                border: 1px solid #ccc;
                padding: 5px;
                font-size: 14px;
                font-weight: bold;
            }
        """)

        layout = QVBoxLayout()

        # 将 Start 和 Record 按钮放在同一行
        buttons_layout = QHBoxLayout()
        self.start_button = QPushButton('Start', self)
        self.start_button.clicked.connect(self.start_detection)
        buttons_layout.addWidget(self.start_button)

        self.record_button = QPushButton('Record', self)
        self.record_button.clicked.connect(self.record_gesture)
        buttons_layout.addWidget(self.record_button)
        layout.addLayout(buttons_layout)  # 添加按钮行到主布局

        gestures = ["thumb up", "thumb down", "wave", "pinch in", "palm flip", "record"]
        keys = ["", "up", "down", "left", "right", "enter", "double click", "right click"]

        self.blocks = []
        self.combos = []
        for gesture in gestures:
            block_layout = QHBoxLayout()
            
            block_label = QLabel(gesture, self)
            block_label.setFixedSize(100, 100)
            block_label.setAlignment(Qt.AlignVCenter | Qt.AlignRight)  # 垂直居中，靠右对齐
            block_label.setStyleSheet("font-size: 18px; font-weight: bold;")
            
            block = QLabel(self)
            block.setAutoFillBackground(True)
            block.setFixedSize(100, 100)
            # block.setStyleSheet(" border-radius: 40px;")  # 设置圆形样式
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
                                colors = ["white", "white", "white", "white", "white", "black"]
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
                                time.sleep(2)
                        except ValueError:
                            colors = ["white", "white", "white", "white", "white", "white"]

                        for i, color in enumerate(colors):
                            palette = self.blocks[i].palette()
                            palette.setColor(QPalette.Window, QColor(color))
                            self.blocks[i].setPalette(palette)
                        time.sleep(0.1)

    def record_gesture(self):
        """Trigger the recording process."""
        try:
            with open("ges_record.txt", "w") as file:
                file.write("1")  # 写入状态 1 表示进入录制模式
            self.show_auto_closing_message_box("Gesture recording started. Perform your gesture.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to start recording: {str(e)}")


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