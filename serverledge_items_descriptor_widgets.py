from PyQt5 import QtCore
from PyQt5.QtCore import Qt, pyqtSignal, QMutex
from PyQt5.QtGui import QPixmap, QFont, QMouseEvent, QCursor, QPixmap, QIcon
from PyQt5.QtWidgets import QLabel, QHBoxLayout, QWidget, QPushButton


#Custom widget label that can emit clicked signal
class ClickableLabel(QLabel):
    clicked = pyqtSignal(QMouseEvent)

    def __init__(self, parent=None):
        super().__init__(parent)

    def mousePressEvent(self, event):
        self.clicked.emit(event)

class NodeWidget(QWidget):

    #Class variables for sizes
    LOGO_WIDTH = 60
    LOGO_HEIGHT = 60
    ICON_WIDTH = 140
    ICON_HEIGHT = 140
    MIN_ELEMENT_WIDTH = 350
    MIN_ELEMENT_HEIGHT = 160
    MAX_ELEMENT_WIDTH = 350
    MAX_ELEMENT_HEIGHT = 150


    def __init__(self, url : str):
        super().__init__()

        #ServerLedge node infos
        self.url = url
        self.available_cpu = 0
        self.available_memory = 0
        self.online = True
        #Used for pull get requests
        #Memorize dict with structure:
        # {
        #   pull_id
        #   params
        # }
        self.pull_ids = []
        #For concurrency
        self.node_mutex = QMutex()

        #Widget elements
        self.text_box = QLabel()
        self.icon = ClickableLabel(parent=self)

        #For printing spacial characters we must:
        self.text_box.setFont(QFont("Noto Sans Cuneiform", 12))

        # For easy customization we define a name for each child widget and the widget itself
        self.setObjectName("Element")
        self.text_box.setObjectName("Text_Box")
        self.icon.setObjectName("Icon")

        #Add image to icon label
        pixmap = QPixmap("./images/server2.png")
        self.icon.setPixmap(pixmap.scaled(NodeWidget.LOGO_WIDTH, NodeWidget.LOGO_HEIGHT))

        #Set default text to the text_box
        self.text_box.setText(f"""<p style="font-size: 20px; color: white; font-family: 'JetBrains Mono'">
                    <center>{self.url.capitalize().replace("Http://","").split(":")[0]}<br><br>
                    <img src="./images/cpu1.png" width="30" height="30"></img>:   {self.available_cpu}<br>
                    <img src="./images/ram1.png" width="33" height="36">:  {self.available_memory}
                    </p></center>
                """)

        #Setting size for elements
        self.setFixedSize(NodeWidget.MIN_ELEMENT_WIDTH,NodeWidget.MIN_ELEMENT_HEIGHT)
        self.icon.setMaximumSize(NodeWidget.ICON_WIDTH,NodeWidget.ICON_HEIGHT)

        #Define layout: horizontal
        layout = QHBoxLayout()
        layout.setContentsMargins(15,0,0,0)
        layout.setSpacing(0)
        layout.addWidget(self.icon)
        layout.addWidget(self.text_box)
        self.setLayout(layout)

        #Apply default css
        self.apply_css_default()
        self.set_online()

    def apply_css_default(self):
        # MUST: By default, for efficiency reason, css on custom widget is disabled
        # to enable it:
        self.setAttribute(Qt.WA_StyledBackground, True)

        #Css
        self.setStyleSheet("""
                    QWidget#Element{
                        background-color: rgb(67,110,144);
                        margin: 0px;
                    }
                    QLabel#Text_Box{
                        font-size: 20px;
                        color: white;
                        margin: 0px 0px 0px 10px;
                        border: 0px;
                    }
                """)

    def set_online(self):
        self.online = True
        #Change cursor
        self.icon.setCursor(QCursor(Qt.PointingHandCursor))
        #Change the background color of the icon to green
        self.icon.setStyleSheet("""
                        text-align: center;
                        background-color: #32a852;
                        qproperty-alignment: AlignCenter;
                        border: 2px solid white;
                        padding: 20px 30px;
                        border-radius: 25px;
                """)

    def set_offline(self):
        self.online = False
        # Change the background color of the icon to grey
        self.icon.setStyleSheet("""
                        text-align: center;
                        background-color: #909992;
                        qproperty-alignment: AlignCenter;
                        border: 2px solid white;
                        padding: 20px 30px;
                        border-radius: 25px;
                """)


    def set_node_text(self, available_cpu : str, available_memory : str):
        # Set text to the text_box
        self.text_box.setText(f"""<p style="font-size: 24px; color: white; font-family: 'JetBrains Mono'">
                    <center>{self.url.capitalize().replace("Http://","").split(":")[0]}<br><br>
                    <img src="./images/cpu1.png" width="30" height="30"></img>:   {available_cpu}<br>
                    <img src="./images/ram1.png" width="33" height="36">:  {available_memory}
                    </p></center>
                    """)

    def update_node_status(self, available_cpu : str, available_memory : str):
        self.set_node_text(available_cpu,available_memory)

    def select(self):
        self.setStyleSheet("""
                    QWidget#Element{
                        background-color: rgb(3,63,107);
                        margin: 0px;
                    }
                    QLabel#Text_Box{
                        font-size: 20px;
                        color: white;
                        margin: 0px 0px 0px 10px;
                        border: 0px;
                    }
                """)

    def deselect(self):
        self.setStyleSheet("""
                    QWidget#Element{
                        background-color: rgb(67,110,144);
                        margin: 0px;
                    }
                    QLabel#Text_Box{
                        font-size: 20px;
                        color: white;
                        margin: 0px 0px 0px 10px;
                        border: 0px;
                    }
                """)

    def get_pull_ids(self):
        self.node_mutex.lock()
        pull_ids_copy = self.pull_ids.copy()
        self.node_mutex.unlock()
        return pull_ids_copy

    def extend_pull_ids(self, new_pull_ids : list):
        self.node_mutex.lock()
        self.pull_ids.extend(new_pull_ids)
        self.node_mutex.unlock()

    def remove_pull_ids(self, unsatisfied_pull_ids : list):
        self.node_mutex.lock()
        pull_ids_copy = self.pull_ids.copy()
        for pull_id in pull_ids_copy:
            if pull_id not in unsatisfied_pull_ids:
                self.pull_ids.remove(pull_id)
        self.node_mutex.unlock()

class EtcdWidget(QWidget):

    def __init__(self):
        super().__init__()

        #Attributes
        self.etcd_status_online = False
        self.etcd_ip = ""
        self.number_nodes = 0

        #Widget within
        self.etcd_icon = QLabel()
        self.etcd_status_text = QLabel()

        #For added customization, we define an object name for each widget
        self.setObjectName("EtcdWidget")
        self.etcd_icon.setObjectName("EtcdIcon")
        self.etcd_status_text.setObjectName("EtcdText")

        #Defining font
        font = QFont("JetBrains Mono",10)
        self.etcd_status_text.setFont(font)

        #Adding images
        self.etcd_icon.setPixmap(QPixmap("./images/etcd.png").scaled(70,70))

        #Default text
        self.etcd_status_text.setText(f"""<center><p style="font-size: 22px; color: white; font-family: 'JetBrains Mono'">
                                    {self.etcd_ip}<br>
                                    <br>NO NODES<br>AVAILABLE<br>
                                    </p></center>
                                    """)

        # Setting size for elements
        self.setFixedSize(NodeWidget.MIN_ELEMENT_WIDTH, NodeWidget.MIN_ELEMENT_HEIGHT+20)
        self.etcd_icon.setFixedSize(NodeWidget.ICON_WIDTH-1,NodeWidget.ICON_HEIGHT-1)

        #Layout: Horizontal
        layout = QHBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(15, 30, 0, 20)
        #Add elements
        #Fist row
        layout.addWidget(self.etcd_icon)
        layout.addWidget(self.etcd_status_text)
        #Setting layout
        self.setLayout(layout)

        #Apply default css
        self.apply_css()


    def apply_css(self):
        #MUST: By default, for efficiency reason, css on custom widget is disabled
        #to enable it:
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.setStyleSheet("""
                        EtcdWidget{
                            background-color: #06538c;
                        }
                        QLabel#EtcdIcon{
                            background-color: #909992;
                            qproperty-alignment: AlignCenter;
                            border: 2px solid white;
                            padding: 10px;
                            border-radius: 25px;
                        }
                    """)

    def update_etcd_ip(self, etcd_ip : str):
        self.etcd_ip = etcd_ip
        self.update_text()

    def set_online(self):
        self.etcd_icon.setStyleSheet("""
                                    background-color: #32a852;
                                    qproperty-alignment: AlignCenter;
                                    border: 2px solid white;
                                    padding: 10px;
                                    border-radius: 25px;
                                """)

    def set_offline(self):
        self.etcd_icon.setStyleSheet("""
                                    background-color: #909992;
                                    qproperty-alignment: AlignCenter;
                                    border: 2px solid white;
                                    padding: 10px;
                                    border-radius: 25px;
                                """)

    def plus_node(self):
        self.number_nodes += 1
        self.update_text()

    def update_text(self):
        # Set text to the text_box
        self.etcd_status_text.setText(f"""<center><p style="font-size: 24px; color: white; font-family: 'JetBrains Mono'">
                            {self.etcd_ip}<br><br>
                            <img src="./images/server2.png" width="50" height="50"></img>: {self.number_nodes}<br>
                            </p></center>
                            """)

class FunctionWidget(QWidget):

    FUNCTION_NUMBER = 0

    def __init__(self, function_name, memory_demand, cpu_demand):
        super().__init__()

        # Increment number of functions
        FunctionWidget.FUNCTION_NUMBER += 1

        # Attributes
        self.function_name = function_name
        self.memory_demand = memory_demand
        self.cpu_demand = cpu_demand

        # Widget definition
        self.function_icon = QLabel()
        self.invoke_button = QPushButton()
        self.function_info_text = QLabel()

        # For more customization we define an object name
        self.setObjectName("Widget")
        self.function_icon.setObjectName("Icon")
        self.invoke_button.setObjectName("InvokeButton")
        self.function_info_text.setObjectName("Text")

        # Setting function icon & invoke button
        self.function_icon.setPixmap(QPixmap("./images/function.png").scaled(100,100))
        self.invoke_button.setIcon(QIcon("./images/invoke.png"))
        self.invoke_button.setIconSize(QtCore.QSize(60,60))

        # Sizes
        self.setFixedHeight(160)
        self.function_icon.setFixedWidth(120)
        self.function_icon.setFixedHeight(120)
        self.invoke_button.setFixedSize(120, 120)

        # Layout: Horizontal
        layout = QHBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(20,0,20,0)
        # Adding widgets
        layout.addWidget(self.function_icon)
        layout.addWidget(self.function_info_text)
        layout.addWidget(self.invoke_button)
        # Setting layout
        self.setLayout(layout)

        # Apply css
        self.apply_css()

        self.update_text()

    def update_text(self):
        self.function_info_text.setText(f"""
                                        <p style="font-size: 20px; color: white; font-family: 'JetBrains Mono'">
                                        Name:&nbsp;{self.function_name}<br><br>
                                        <img src="./images/cpu1.png" width="30" height="30"></img>:&nbsp;{self.cpu_demand}<br>
                                        <img src="./images/ram1.png" width="30" height="30"></img>:&nbsp;{self.memory_demand}
                                        </p>
                                    """)

    def apply_css(self):
        # MUST: By default, for efficiency reason, css on custom widget is disabled
        # to enable it:
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.setStyleSheet("""
                            QWidget#Widget{
                                background-color: rgb(3,63,107);
                                border-radius: 15px;
                            }
                            QLabel#Icon{
                                qproperty-alignment: AlignCenter;
                                background-color: white;
                                border-radius: 15px;
                            }
                            QPushButton#InvokeButton{
                                background-color: #044b80;
                                border-radius: 15px;
                                border: 2px solid white;
                            }
                            QPushButton#InvokeButton:hover{
                                background-color: #06538c;
                            }
                        """)

        if FunctionWidget.FUNCTION_NUMBER % 2 == 0:
            self.setStyleSheet("""
                            QWidget#Widget{
                                background-color: #06538c;
                                border-radius: 15px;
                            }
                            QLabel#Icon{
                                qproperty-alignment: AlignCenter;
                                background-color: white;
                                border-radius: 15px;
                            }
                            QPushButton#InvokeButton{
                                background-color: #044b80;
                                border-radius: 15px;
                                border: 2px solid white;
                            }
                            QPushButton#InvokeButton:hover{
                                background-color: #06538c;
                            }
                            """)