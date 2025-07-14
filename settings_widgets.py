from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget, QTextEdit, QLabel, QPushButton, QLineEdit, QSpinBox
from PyQt5.QtGui import QFont, QRegExpValidator
from PyQt5.QtCore import QRegExp

class StackWidget(QWidget):

    def __init__(self, widget_top : QWidget, widget_bottom : QWidget):
        super().__init__()

        #Widget definition
        self.widget_top = widget_top
        self.widget_bottom = widget_bottom

        #Layout: Vertical
        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        #Add widgets
        layout.addWidget(self.widget_top)
        layout.addWidget(self.widget_bottom)
        #Set layout
        self.setLayout(layout)

class SettingsFormWidget(QWidget):

    def __init__(self):
        super().__init__()

        #Widget definition
        self.etcd_ip_form = QLineEdit()
        self.etcd_port_form = QLineEdit()
        self.frequency_update_form = QSpinBox()
        self.submit_button = QPushButton()
        self.text_etcd_ip = QLabel()
        self.text_etcd_port = QLabel()
        self.freq = QLabel()

        #Button text
        self.submit_button.setText("Apply")
        #Label text
        self.text_etcd_ip.setText("""<p style="font-size: 26px; color: white; font-family: 'JetBrains Mono'">Etcd ip (Ipv4):</p>""")
        self.text_etcd_port.setText("""<p style="font-size: 26px; color: white; font-family: 'JetBrains Mono'">Etcd port:</p>""")
        self.freq.setText("""<p style="font-size: 26px; color: white; font-family: 'JetBrains Mono'">Update frequency:</p>""")

        # Stacking widgets
        stack1 = StackWidget(self.text_etcd_ip, self.etcd_ip_form)
        stack2 = StackWidget(self.text_etcd_port, self.etcd_port_form)
        stack3 = StackWidget(self.freq, self.frequency_update_form)

        #Sizes
        self.setFixedHeight(700)
        self.etcd_ip_form.setFixedHeight(50)
        self.etcd_port_form.setFixedHeight(50)
        self.frequency_update_form.setFixedHeight(50)
        self.submit_button.setFixedSize(120, 50)
        stack1.setFixedHeight(100)
        stack2.setFixedHeight(100)
        stack3.setFixedHeight(100)

        # Input font sizes
        font = QFont("Jetbrains mono", 15)
        self.etcd_ip_form.setFont(font)
        self.etcd_port_form.setFont(font)
        self.frequency_update_form.setFont(font)

        # Input centering
        self.etcd_ip_form.setAlignment(Qt.AlignCenter)
        self.etcd_port_form.setAlignment(Qt.AlignCenter)
        self.frequency_update_form.setAlignment(Qt.AlignCenter)
        # Text centering
        self.text_etcd_ip.setAlignment(Qt.AlignCenter)
        self.text_etcd_port.setAlignment(Qt.AlignCenter)
        self.freq.setAlignment(Qt.AlignCenter)

        #Validator - regular expression
        self.etcd_ip_form.setValidator(QRegExpValidator(QRegExp("^[0-9]{1,3}[.][0-9]{1,3}[.][0-9]{1,3}[.][0-9]{1,3}$")))
        self.etcd_port_form.setValidator(QRegExpValidator(QRegExp("^[0-9]{1,5}$")))

        #Layout: Vertical
        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(20, 0, 20, 0)
        #Add widgets
        layout.addWidget(stack1)
        layout.addWidget(stack2)
        layout.addWidget(stack3)
        layout.addWidget(self.submit_button)
        #Set layout
        self.setLayout(layout)

        #Apply css
        self.apply_css()

    def apply_css(self):
        # MUST: By default, for efficiency reason, css on custom widget is disabled
        # to enable it:
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet("""
                            background-color: #06538c;
                            border-top-left-radius: 15px;
                            border-bottom-left-radius: 15px;
                    """)
        self.etcd_ip_form.setStyleSheet("""
                                        background-color: white;
                                        border-radius: 15px;
                                    """)
        self.etcd_port_form.setStyleSheet("""
                                        background-color: white;
                                        border-radius: 15px;
                                    """)
        self.frequency_update_form.setStyleSheet("""
                                        QSpinBox{
                                            background-color: white;
                                            border-radius: 15px;
                                        }
                                        QSpinBox::up-button {
                                            border-bottom: 0px;
                                        }
                                        QSpinBox::down-button {
                                            border-bottom: 0px;
                                        }
                                        """)
        self.submit_button.setStyleSheet("""
                                        QPushButton{
                                            color: white;
                                            font-size: 20px;
                                            border-radius: 10px;
                                            background-color: #044b80;
                                            border: 3px solid white;
                                        }
                                        QPushButton:hover{
                                            background-color: #b30412;
                                        }
                                    """)

    def set_text_forms(self, etcd_ip : str, etcd_port : str, delay_seconds : int):

        self.etcd_ip_form.setText(etcd_ip)
        self.etcd_port_form.setText(etcd_port)
        self.frequency_update_form.setValue(delay_seconds)

class SettingsWidget(QWidget):

    def __init__(self):
        super().__init__()

        #Widget definition
        self.form = SettingsFormWidget()
        self.log = QTextEdit()

        #Sizes
        self.log.setMaximumSize(500,700)
        self.form.setMinimumWidth(450)

        #Tweak: Cant interact
        self.log.setReadOnly(True)

        #Layout: Horizontal
        layout = QHBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(50, 0, 50, 0)
        #Adding widgets and spacer for centering
        layout.addWidget(self.form)
        layout.addWidget(self.log)
        #Set layout
        self.setLayout(layout)

        #Apply css
        self.apply_css()

    def apply_css(self):
        self.log.setStyleSheet("""
                                background-color: rgb(67,110,144);
                                border: 0px;
                                border-top-right-radius: 15px;
                                border-bottom-right-radius: 15px;                
                            """)

    def write_outcome(self, conf_written : bool):

        icon = "!"
        text = "Failed to overwrite configuration file"
        if conf_written is True:
            icon = "✓"
            text = "All done!"

        self.log.setHtml(f"""
                        <br><br><br><br><br><br><br><br><br>
                        <br><br><br><br><br><br><br><br><br>
                        <center style="color: white; font-size: 26px;">{icon}<br>{text}</center>
                    """)

        #After a short while clear the log
        QTimer.singleShot(2000, self.clear_log)

    def clear_log(self):
        self.log.setHtml("")