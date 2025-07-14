from PyQt5.QtCore import Qt
from dynamic_menu_widgets import ScrollableMenuWidget
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget, QTextEdit, QPushButton, QLineEdit
from PyQt5.QtGui import QFont
from datetime import datetime


class ButtonMenuWidget(QWidget):

    def __init__(self):
        super().__init__()

        #Widget definition
        self.clear_button = QPushButton()
        self.mod_button = QPushButton()
        self.pull_button = QPushButton()
        #DEBUG:
        self.add_fake_node = QPushButton()

        #Widget text
        self.clear_button.setText("Clear")
        self.mod_button.setText("Mode: Sync") #Defaul: sync modality
        self.pull_button.setText("Pull")
        #DEBUG:
        self.add_fake_node.setText("Add fake node")

        #Widget text button
        font = QFont("JetBrains Mono", 10)
        self.clear_button.setFont(font)
        self.mod_button.setFont(font)
        self.pull_button.setFont(font)
        self.add_fake_node.setFont(font)

        #Sizes
        self.clear_button.setFixedSize(120,50)
        self.mod_button.setFixedSize(120, 90)
        #DEBUG:
        self.add_fake_node.setFixedSize(120,120)
        self.pull_button.setFixedSize(120, 50)
        self.setFixedHeight(400)
        self.setFixedWidth(200)

        #For added customization we define a name for each widget
        self.setObjectName("ButtonMenu")
        self.pull_button.setObjectName("PullButton")
        self.mod_button.setObjectName("ModButton")
        self.clear_button.setObjectName("ClearButton")

        #Layout: Vertical
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(40,0,0,0)
        #Add widgets
        layout.addWidget(self.clear_button)
        layout.addWidget(self.mod_button)
        layout.addWidget(self.pull_button)
        #DEBUG:
        #layout.addWidget(self.add_fake_node)

        #Set layout
        self.setLayout(layout)

        #Apply default css
        self.apply_css()

    def apply_css(self):
        # MUST: By default, for efficiency reason, css on custom widget is disabled
        # to enable it:
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.setStyleSheet("""
                            QWidget#ButtonMenu {
                                background-color: rgb(67,110,144);
                                border-top-right-radius: 15px;
                                border-bottom-right-radius: 15px;
                            }
                            QPushButton {
                                color: white;
                                border-radius: 10px;
                                background-color: #044b80;
                                border: 3px solid white;
                            }
                            QPushButton:hover {
                                background-color: #06538c;
                            }
                            """)

    def change_mod_text(self, modality : str):
        self.mod_button.setText(modality)

class FunctionsMenuWidget(QWidget):

    def __init__(self):
        super().__init__()

        #Widget definition
        self.function_menu = ScrollableMenuWidget()
        self.button_menu = ButtonMenuWidget()

        #For added customization we define a name for each widget
        self.setObjectName("Widget")

        #Size: no width limit (16777215 is a PyQt constant)
        self.function_menu.setMaximumWidth(16777215)
        self.function_menu.setMaximumHeight(400)

        #Layout: Horizontal
        layout = QHBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        #Adding widgets
        layout.addWidget(self.function_menu)
        layout.addWidget(self.button_menu)
        #Set layout
        self.setLayout(layout)

        #Apply default css
        self.apply_css()

    def apply_css(self):
        self.function_menu.menu_widget.setStyleSheet("""
                                        QWidget#Menu{
                                            background-color: rgb(67,110,144);
                                            border-top-left-radius: 15px;
                                            border-bottom-left-radius: 15px;
                                            margin: 0px;
                                        }
                                    """)
        self.function_menu.setStyleSheet("""
                                        QWidget#ScrollableMenu{
                                            background-color: rgb(67,110,144);
                                            border-top-left-radius: 15px;
                                            border-bottom-left-radius: 15px;
                                            margin: 0px;
                                            border: 0px;
                                        }
                                        QScrollBar:vertical, QScrollBar:horizontal {
                                            width: 0px;
                                            height: 0px;
                                            }
                                    """)

class ScreenAndInputWidget(QWidget):

    def __init__(self):
        super().__init__()

        #Widget definition
        self.log = QTextEdit()
        self.input = QLineEdit()

        # Tweak: Disable editing from the user
        self.log.setReadOnly(True)

        #Sizes
        self.log.setMaximumHeight(300)
        self.log.setMinimumHeight(230)
        self.input.setFixedHeight(70)

        #Input default text
        self.input.setPlaceholderText(" Params input block: Try n:5 or string=Ciao !")

        #Input font sizes
        font = QFont("Jetbrains mono",15)
        self.input.setFont(font)

        #Layout: vertical
        layout = QVBoxLayout()
        #No spaces
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        #Add widgets:
        layout.addWidget(self.log)
        layout.addWidget(self.input)
        #Set layout
        self.setLayout(layout)

class FunctionsConsoleWidget(QWidget):

    def __init__(self):
        super().__init__()

        #Widget definition
        self.log = ScreenAndInputWidget()
        self.function_menu = FunctionsMenuWidget()

        #Sizes
        self.log.setMaximumHeight(370)
        self.log.setMinimumHeight(300)

        #Layout: vertical
        layout = QVBoxLayout()
        #Left and right margins
        layout.setContentsMargins(50, 50, 50, 0)
        layout.setSpacing(0)
        #Add elements:
        layout.addWidget(self.log)
        layout.addWidget(self.function_menu)
        #Set layout
        self.setLayout(layout)

        #Apply css
        self.apply_css()

        #Welcome text
        self.add_row_text("System","Welcome!",True)

    def apply_css(self):
        self.log.setStyleSheet("""
                                border: 3px solid #044b80;
                            """)

    def add_row_text(self,subject : str, text : str, good: bool):
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        color = "#b30412"
        notification = "&nbsp;!"
        if good:
            color = "#32a852"
            notification = "&nbsp;✓"
        self.log.log.append(f"""
                        <span style="font-size: 26px">
                        <span style="background-color: rgb(3,63,107); color: white; padding: 20px;">&nbsp;&nbsp;{current_time}&nbsp;
                        <span style="background-color: #06538c; color: white;">&nbsp;&nbsp;{subject}&nbsp;&nbsp;
                        <span style="background-color: {color}; color: white;">{notification}
                        </span></span></span>&nbsp;{text}
                        </span>
                    """)

    def clear_text(self):
        self.log.log.setHtml("")


