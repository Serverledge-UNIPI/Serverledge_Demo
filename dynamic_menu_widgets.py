from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QSizePolicy, QWidget, QVBoxLayout, QSpacerItem, QScrollArea, QLabel


#Menu widget without scrolling
class MenuWidget(QWidget):

    MIN_ELEMENT_WIDTH = 350

    def __init__(self):
        super().__init__()

        #Menu infos
        self.number_of_child_widgets = 0

        #Widget elements, the widget allows to dynamically
        #add new widgets but at initialization we define a 'QSpacerItem'
        #so that all the widget within are 'pushed' to the top
        self.bottom_spacer = QSpacerItem(MenuWidget.MIN_ELEMENT_WIDTH,0,QSizePolicy.Fixed,QSizePolicy.Expanding)

        #for easy customization we define a name for the widget itself
        #and all the widget within
        self.setObjectName("Menu")

        # Setting resize policy for elements
        self.setMinimumWidth(MenuWidget.MIN_ELEMENT_WIDTH)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        #DefineLayout: Vertical
        self.layout = QVBoxLayout()
        #We want zeros spaces between elements
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.layout.addSpacerItem(self.bottom_spacer)
        self.setLayout(self.layout)

        #Apply css
        self.apply_css()

    def addWidget(self, widget : QWidget):
        #Add Widgets to the layout to the end
        #but before the spacer!
        self.layout.insertWidget(self.number_of_child_widgets,widget)
        #Increment number of child widgets
        self.number_of_child_widgets += 1

    def apply_css(self):
        # MUST: By default, for efficiency reason, css on custom widget is disabled
        # to enable it:
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.setStyleSheet("""
                    QWidget#Menu{
                        background-color: rgb(67,110,144);
                    }
                """)

class SubMenuHeaderWidget(QLabel):

    def __init__(self, location : str, color: str):
        super().__init__()

        # Text
        self.setText(f"""<p style="color: white; font-family: 'JetBrains Mono'; font-size: 26px">
                        {location}
                    </p>
                    """)

        # Alignment
        self.setAlignment(Qt.AlignLeft)

        # Size
        self.setFixedHeight(40)

        # Slight left margin
        self.setContentsMargins(10,3,0,0)
        # Apply css
        self.apply_css(color)

    def apply_css(self, color: str):

        self.setStyleSheet(f"""
                            border-top: 1px solid white;
                            background-color: {color};
                            """)

class SubMenuWidget(MenuWidget):

    SUB_MENU_NUMBER = 0

    def __init__(self, location: str):
        super().__init__()
        # The only difference in the style
        # is a left border
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setObjectName("SubMenu")
        color = ["rgb(3,63,107)","#06538c"]
        self.setStyleSheet(f"""
                                border-left: 7px solid {color[SubMenuWidget.SUB_MENU_NUMBER % 2]};
                        """)

        # We add the header to indicate the nodes location
        self.addWidget(SubMenuHeaderWidget(location,color[SubMenuWidget.SUB_MENU_NUMBER % 2]))
        SubMenuWidget.SUB_MENU_NUMBER += 1

#Menu widget with scrolling
class ScrollableMenuWidget(QScrollArea):

    def __init__(self):
        super().__init__()

        #Define widget with which we provide a scrollable view
        self.menu_widget = MenuWidget()
        #Set the widget as scrollable
        self.setWidget(self.menu_widget)
        self.setWidgetResizable(True)

        # for easy customization we define a name for the widget itself
        self.setObjectName("ScrollableMenu")

        #Setting the width size
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMaximumWidth(MenuWidget.MIN_ELEMENT_WIDTH)

        #Apply css
        self.apply_css()

    def apply_css(self):
        # MUST: By default, for efficiency reason, css on custom widget is disabled
        # to enable it:
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.setStyleSheet("""
                            QWidget#ScrollableMenu{
                                background-color: rgb(67,110,144);
                                margin: 0px;
                                border: 0px;
                            }
                            QScrollBar:vertical, QScrollBar:horizontal {
                                width: 0px;
                                height: 0px;
                            }
                        """)

