from abc import abstractmethod
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QSizePolicy, QHBoxLayout, QSpacerItem, QFrame, QLabel
from PyQt5.QtGui import QPixmap, QFont


class TitleBar(QFrame):

    @abstractmethod
    def __init__(self):
        super().__init__()

        #Generic attributes
        self.app_icon = None
        self.app_title = None
        self.close_icon = None
        self.maximize_icon = None
        self.minimize_icon = None
        #Functional attributes
        self._drag_pos = None
        self._drag_enabled = True

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos()
            event.accept()

    def mouseMoveEvent(self, event):
        if not self._drag_enabled:
            return
        if event.buttons() == Qt.LeftButton:
            parent = self.window()
            if parent and not parent.isMaximized():
                parent.move(parent.pos() + event.globalPos() - self._drag_pos)
                self._drag_pos = event.globalPos()
                event.accept()

    def close_window(self, event):
        event.accept()
        #Slight delay
        QTimer.singleShot(100, self.window().close)

    def minimize_window(self, event):
        event.accept()
        self.window().showMinimized()

    def maximize_restore_window(self, event):
        self._drag_enabled = False
        event.accept()
        win = self.window()
        if win.isMaximized():
            win.showNormal()
        else:
            win.showMaximized()
        QTimer.singleShot(300,self.reenable_drag)

    def reenable_drag(self):
        self._drag_enabled = True

class TitleBarWindows(TitleBar):

    ICON_WIDTH = 20
    ICON_HEIGHT = 20

    def __init__(self):
        super().__init__()

        #Define elements
        self.close_icon = QLabel()
        self.maximize_icon = QLabel()
        self.minimize_icon = QLabel()
        self.app_title = QLabel()
        self.app_icon = QLabel()
        self.center_spacer = QSpacerItem(0, 100, QSizePolicy.Expanding, QSizePolicy.Fixed)

        # Classic window event
        self.close_icon.mousePressEvent = self.close_window
        self.minimize_icon.mousePressEvent = self.minimize_window
        self.maximize_icon.mousePressEvent = self.maximize_restore_window

        #For easy customization we define a name for the widget itself and widgets within
        self.setObjectName("TitleBar")
        self.app_title.setObjectName("Title")
        self.app_icon.setObjectName("AppIcon")
        self.close_icon.setObjectName("CloseIcon")
        self.maximize_icon.setObjectName("MaxIcon")
        self.minimize_icon.setObjectName("MinIcon")

        #Set image for every icon
        self.close_icon.setPixmap(QPixmap("./images/close.png").scaled(TitleBarWindows.ICON_WIDTH,TitleBarWindows.ICON_HEIGHT))
        self.maximize_icon.setPixmap(QPixmap("./images/maximize.png").scaled(TitleBarWindows.ICON_WIDTH,TitleBarWindows.ICON_HEIGHT))
        self.minimize_icon.setPixmap(QPixmap("./images/minimize.png").scaled(TitleBarWindows.ICON_WIDTH,TitleBarWindows.ICON_HEIGHT))
        self.app_icon.setPixmap(QPixmap("./images/lambda.png").scaled(TitleBarWindows.ICON_WIDTH+15,TitleBarWindows.ICON_HEIGHT+15))

        # Fixed sizes
        self.close_icon.setFixedSize(50, 40)
        self.maximize_icon.setFixedSize(50, 40)
        self.minimize_icon.setFixedSize(50, 40)
        self.app_icon.setFixedSize(32, 32)
        self.app_title.setFixedSize(300, 32)

        self.setFixedHeight(40)

        #Set app name
        font = QFont("JetBrains Mono")
        self.app_title.setFont(font)
        self.app_title.setText("""Λ   ServerLedge Dashboard""")

        #Layout: Horizontal
        layout = QHBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0,0,0,0)
        #sx elements
        #layout.addWidget(self.app_icon)
        layout.addWidget(self.app_title)
        #Spacer
        layout.addSpacerItem(self.center_spacer)
        #rx elements
        layout.addWidget(self.minimize_icon)
        layout.addWidget(self.maximize_icon)
        layout.addWidget(self.close_icon)
        #Set layout
        self.setLayout(layout)

        #Apply css
        self.apply_css()

    def apply_css(self):
        self.setStyleSheet("""
                        TitleBar{
                            background-color: rgb(3,63,107);
                        }
                        QLabel{
                            qproperty-alignment: AlignCenter;
                        }
                        QLabel#CloseIcon:hover{
                           background-color: red; 
                        }
                        QLabel#MinIcon:hover{
                            background-color: #044b80;
                        }
                        QLabel#MaxIcon:hover{
                            background-color: #044b80;
                        }
                        QLabel#Title{
                            font-size: 20px;
                            color: white;
                            font-weight: bold;
                        }
                        QLabel#AppIcon{
                            margin-left: 5px;
                        }
                    """)



