import os
import sys
import time
import psutil
import socket
import requests
import getpass
from PyQt5.QtCore import Qt, QRect, QPropertyAnimation, QEasingCurve, QDateTime, QTimer
from PyQt5.QtGui import QPainter, QFont, QFontDatabase
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QToolBar, QDesktopWidget, QLabel

class ResizableApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.initUI()

    def initUI(self):
        screen = QDesktopWidget().screenGeometry()
        self.setGeometry(screen.width()  -220, -0, 100, 150)
        self.setWindowTitle('Rigby')

        # Create a toolbar
        self.toolbar = QToolBar(self)
        self.toolbar.setFocusPolicy(Qt.NoFocus)
        self.addToolBar(Qt.TopToolBarArea, self.toolbar)
        self.toolbar.setMovable(False)
        self.toolbar.setStyleSheet("QToolBar { border: none; outline: none; }")

        custom_font_path = 'fonts/digital_7/digital-7.ttf'
        QFontDatabase.addApplicationFont(custom_font_path)
        self.gui_font = QFont("digital-7", 20)
        self.info_label_font = QFont("digital-7", 13)

        #TOOLBAR APPS ------------------------------------------------------------------------------

        #TOOLBAR TOGGLE
        self.toggle_button = QPushButton(self)
        self.toggle_button.setText('Expand')
        self.toggle_button.setFont(self.gui_font)
        self.toggle_button.clicked.connect(self.toggleWindow)
        self.toggle_button.setStyleSheet(
            "QPushButton {"
            "   background-image: url('images/toggle_btn.png');"
            "   border: 0px;"
            "   background-repeat: no-repeat;"  
            "   background-position: left center;"  
            "   background-color: rgba(255, 255, 255, 0);"
            "   text-align: left;"
            "   color: white;"
            "   padding-left: 50px;"
            "   height: 200px;"
            "   width: 145px;"
            "}"
        )

        self.info_label = QLabel(self.get_network_info())
        self.info_label.setFixedSize(200, 200)
        self.info_label.setFont(self.info_label_font)
        self.info_label.setStyleSheet("color: #fff; background-image: url('images/info_panel.png'); padding-left: 10px; border: 0px;")

        self.drive_info = QLabel(self.get_drive_info())
        self.drive_info.setFixedSize(200, 200)
        self.drive_info.setFont(self.info_label_font)
        self.drive_info.setStyleSheet("color: #fff; background-image: url('images/drive_info.png'); padding-left: 15px; padding-top:20px; border: 0px;")

        self.button_studiocode = QPushButton(self)
        #self.button_studiocode.setText('CODE')
        self.button_studiocode.setFixedSize(100, 200)
        self.button_studiocode.setFont(self.info_label_font)
        self.button_studiocode.clicked.connect(self.open_vscode)
        self.button_studiocode.setStyleSheet(
                    "QPushButton {"                   
                    "color: #fff; background-image: url('images/code_button.png'); background-color: transparent; border: 0px;"
                    "}"
                    "QPushButton:hover {"                   
                    "color: #fff; background-image: url('images/code_button_hover.png'); background-color: transparent; border: 0px;"
                    "}"
                )

        self.button_widget = QPushButton(self)
        #self.button_widget.setText('')
        self.button_widget.setFixedSize(100, 200)
        self.button_widget.setFont(self.info_label_font)
        self.button_studiocode.clicked.connect(self.open_spotify)
        self.button_widget.setStyleSheet(
                    "QPushButton {"                   
                    "color: #fff; background-image: url('images/widget_button.png'); background-color: transparent; border: 0px;"
                    "}"
                    "QPushButton:hover {"                   
                    "color: #fff; background-image: url('images/widget_button_hover.png'); background-color: transparent; border: 0px;"
                    "}"
                )

        self.button_shortcuts = QPushButton(self)
        #self.button_shortcuts.setText('')
        self.button_shortcuts.setFixedSize(100, 200)
        self.button_shortcuts.setFont(self.info_label_font)
        self.button_shortcuts.clicked.connect(self.open_spotify)
        self.button_shortcuts.setStyleSheet(
                    "QPushButton {"                   
                    "color: #fff; background-image: url('images/dir_button.png'); background-color: transparent; border: 0px;"
                    "}"
                    "QPushButton:hover {"                   
                    "color: #fff; background-image: url('images/dir_button_hover.png'); background-color: transparent; border: 0px;"
                    "}"
                )
        
        self.button_refresh = QPushButton(self)
        #self.button_refresh.setText('')
        self.button_refresh.setFixedSize(100, 200)
        self.button_refresh.setFont(self.info_label_font)
        self.button_refresh.clicked.connect(self.refresh_system_info)
        self.button_refresh.setStyleSheet(
                    "QPushButton {"                   
                    "color: #fff; background-image: url('images/refresh_button.png'); background-color: transparent; border: 0px;"
                    "}"
                    "QPushButton:hover {"                   
                    "color: #fff; background-image: url('images/refresh_button_hover.png'); background-color: transparent; border: 0px;"
                    "}"
                )
        
        self.timer1 = QTimer(self)
        self.timer1.timeout.connect(self.update_button_text)
        self.timer1.start(1000)

        #ADDING WIDGET
        self.toolbar.addWidget(self.toggle_button)
        self.toolbar.addWidget(self.info_label)
        self.toolbar.addWidget(self.drive_info)
        self.toolbar.addWidget(self.button_studiocode)
        self.toolbar.addWidget(self.button_widget)
        self.toolbar.addWidget(self.button_shortcuts)
        self.toolbar.addWidget(self.button_refresh)
     
        self.animation = QPropertyAnimation(self, b'geometry')
        self.animation.setEasingCurve(QEasingCurve.OutQuint)
        self.animation.setDuration(200)  # Animation duration in milliseconds

        self.expanded = False
        self.draggable = False

    def toggleWindow(self):
        if not self.expanded:
            start_geometry = self.geometry()
            end_geometry = QRect(self.x() - 800, -0, 1050, 800)
            self.animation.setStartValue(start_geometry)
            self.animation.setEndValue(end_geometry)
            self.animation.start()

        else:
            start_geometry = self.geometry()
            end_geometry = QRect(self.x() + 800, -0, 100, 100)
            self.animation.setStartValue(start_geometry)
            self.animation.setEndValue(end_geometry)
            self.animation.start()
        self.expanded = not self.expanded

    def mousePressEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.draggable = True
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.draggable:
            self.move(self.mapToGlobal(event.pos() - self.offset))

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.draggable = False

    def paintEvent(self, event):
        painter = QPainter(self)
        #painter.fillRect(self.rect(), QColor(30, 144, 255, 100))  # Background color (Dodger Blue)

    def open_vscode(self):
        os.system("code")

    def open_spotify(self):
        os.system("Start-Process powershell")

    def updateClock(self):
        self.current_time = QDateTime.currentDateTime().toString('hh:mm:ss')
        self.digital_clock.setText(self.current_time)

    def update_button_text(self):
        current_time = time.strftime("%H:%M:%S")
        cpu_usage = psutil.cpu_percent()
        ram_usage = psutil.virtual_memory().percent

        t = f"{current_time}"
        c = f"CPU: {cpu_usage}%"
        r = f"RAM: {ram_usage}%"

        self.toggle_button.setText(
            f"{t}\n"
            f"{c}\n"
            f"{r}"
        )

    def get_network_info(self):
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        try:
            response = requests.get('https://api64.ipify.org?format=json')
            data = response.json()
            public_ip = data['ip']
        except requests.exceptions.RequestException:
            public_ip = "Not available"
        local_domain_name = socket.getfqdn().split('.', 1)[-1]

        username = getpass.getuser()

        info = (f". Hostname:\n   {hostname}"
                 f"\n    . User:\n      {username}\n"
                 f"\n    . L IP: {local_ip}"
                 f"\n   . P IP: {public_ip}"
                 f"\n . Local Domain:\n{local_domain_name}"
                 )
        return info
    
    def get_drive_info(self):
        test = "TESTING"

        partitions = psutil.disk_partitions()

        drive_info = ""

        for partition in partitions:
            partition_info = psutil.disk_usage(partition.mountpoint)
            drive = partition.device
            total_space_gb = partition_info.total / (1024**3)
            free_space_gb = partition_info.free / (1024**3)
            drive_info += f"{drive}: {total_space_gb:.2f} GB {free_space_gb:.2f} GB\n"

        return drive_info
    
    def refresh_system_info(self):
        self.info_label = QLabel(self.get_network_info())
        self.drive_info = QLabel(self.get_drive_info())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ResizableApp()
    window.show()
    sys.exit(app.exec_())
