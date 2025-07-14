from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QLabel, QSpacerItem, QVBoxLayout, QHBoxLayout, QTextEdit, QSizePolicy, QFrame, \
    QScrollArea


#Generic widgets

class SelfCenteringImageWidget(QWidget):

    def __init__(self):
        super().__init__()

        # Widget definition
        self.image = QLabel()

        # Layout : Horizontal
        layout = QHBoxLayout()
        layout.addSpacerItem(QSpacerItem(10,0,QSizePolicy.Expanding,QSizePolicy.Fixed))
        layout.addWidget(self.image)
        layout.addSpacerItem(QSpacerItem(10,0,QSizePolicy.Expanding,QSizePolicy.Fixed))
        # Set layout
        self.setLayout(layout)

    def apply_image(self, path : str, width : int, height: int):
        # Set image
        self.image.setPixmap(QPixmap(path).scaled(width,height))
        # Set label size
        self.image.setFixedSize(width,height)

class AutoReturnLabel(QTextEdit):

    def __init__(self):
        super().__init__()

        # Basic styling
        self.setStyleSheet("""
                            border: none;
                            background-color: transparent;
                        """)

        # Read only so we can use it as a label
        self.setReadOnly(True)

    def apply_centered_text(self, text : str, font_size : int, color : str):

        self.setHtml(f"""
                        <center style="font-size: {font_size}px; font-family: 'JetBrains Mono'; color:{color}">
                        {text}
                        </center>
                    """)

    def apply_text(self, text : str, font_size : int, color : str):

        self.setHtml(f"""
                    <p style="font-size: {font_size}px; font-family: 'JetBrains Mono'; color:{color}">
                        {text}
                    </p>
                    """)

class AboutWidget(QWidget):

    def __init__(self):

        super().__init__()

        # Widget definition
        self.unipi_logo = SelfCenteringImageWidget()
        self.title = AutoReturnLabel()
        self.main_text = AutoReturnLabel()

        #Sizes
        self.title.setFixedHeight(70)

        # Image and size
        self.unipi_logo.apply_image("./images/stemma_unipi.svg.png",320,320)

        # Text
        self.title.apply_centered_text("Progetto di Tesi di laurea - Ingegneria informatica", 30 ,"#033f6b")
        main_text_text = """Questo applicativo è stato sviluppato da Isaia Porcu nell'ambito della tesi di laurea in Ingegneria Informatica, con il supporto e la supervisione dei seguenti docenti relatori:
                        <br>– Prof. Carlo Vallati
                        – Prof.ssa Francesca Righetti
                        – Prof. Nicola Tonellotto
                        <br><br>Tutte le icone utilizzate sono state prelevate dal sito FlatIcon.com.<br><br>
                        Questo applicativo non è che un front-end per ServerLedge visitare la
                        repository per dettagli: https://github.com/serverledge-faas/serverledge"""
        self.main_text.apply_text(main_text_text, 25, "black")

        # Layout: Vertical
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(50,10,50,10)
        layout.addWidget(self.unipi_logo)
        layout.addWidget(self.title)
        layout.addWidget(self.main_text)
        # Set layout
        self.setLayout(layout)

class HelpWidget(QFrame):

    def __init__(self):
        super().__init__()

        # Widget definition
        self.logo = SelfCenteringImageWidget()
        self.title = AutoReturnLabel()
        self.text = AutoReturnLabel()

        # Sizes
        self.title.setFixedHeight(70)

        # Image and size
        self.logo.apply_image("./images/dashboard_logo.png",320,320)

        # Text
        self.title.apply_centered_text("Basic Configuration and Instructions",35,"#033f6b")
        text = ("""This application monitors the state of discovered ServerLedge nodes, discovered nodes are displayed on"""
                """ the left side menu under the ETCD widget, if you dont see any it must be that there are no online nodes"""
                """ (green background on ETCD icon), the ETCD server is offline or the ip of the ETCD server is wrong, if you think"""
                """ that's the case then go to the settings panel and change it!<br><span style="color:#ff9955">Settings</span><br>"""
                """There are 3 input boxes, any changes finalized by clicking on the Submit button will take affect immediately"""
                """ and saved to a config file so you dont have to recompile the input boxes!<br><span style="color:#ff9955">Functions</span><br>"""
                """The functions are displayed in a scrollable menu on the bottom, if you want to invoke one you have to first"""
                """ select an active node by clicking on his icon, choose a mode (sync/async) by toggling the selection with """
                """the button on the right and finally click the invoke button on the right of the chosen function. Functions may require """
                """parameters, you may input the parameters in the apposite input box by following the syntax: (name1)[:/=](value1)(space)(name2)[:/=](value2) ecc...<br>"""
                """If chosen the sync modality the output will be displayed as soon as available, if not you have to click the poll button"""
                """ the result will be then displayed if ready!""")
        self.text.apply_text(text,25,"black")

        # Bottomless text
        self.text.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)

        # Layout: Vertical
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(50,10,50,10)
        layout.addWidget(self.logo)
        layout.addWidget(self.title)
        layout.addWidget(self.text)
        # Set layout
        self.setLayout(layout)

class ScrollableHelpWidget(QScrollArea):

    def __init__(self):
        super().__init__()

        # Scrollable widget
        self.help_widget = HelpWidget()
        self.setWidget(self.help_widget)
        # Set scrollable
        self.setWidgetResizable(True)

        # Setting the width size
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Apply css
        self.apply_css()

    def apply_css(self):

        self.setStyleSheet("""
                            QScrollBar:vertical, QScrollBar:horizontal {
                                width: 0px;
                                height: 0px;
                            }
                        """)