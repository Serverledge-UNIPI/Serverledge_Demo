from PyQt5.QtWidgets import QWidget, QSizePolicy, QHBoxLayout, QSpacerItem, QFrame, QLabel, QStackedLayout, QPushButton, QVBoxLayout
from PyQt5.QtGui import QFont
from functions_widget import FunctionsConsoleWidget
from settings_widgets import SettingsWidget
from about_and_help_widgets import AboutWidget, ScrollableHelpWidget

class OptionsMenuWidget(QFrame):

    def __init__(self):
        super().__init__()

        #Define elements
        self.function_button = QPushButton()
        self.credit_button = QPushButton()
        self.info_button = QPushButton()
        self.setting_button = QPushButton()
        self.side_spacer = QSpacerItem(0, 100, QSizePolicy.Expanding, QSizePolicy.Fixed)

        # List for easy access
        self.buttons = [self.function_button,self.credit_button,self.info_button,self.setting_button]

        # For easy customization we define a name for the widget itself and widgets within
        self.setObjectName("OptionsMenu")
        self.function_button.object_name ="FunctionButton"
        self.credit_button.object_name = "CreditButton"
        self.info_button.object_name = "InfoButton"
        self.setting_button.object_name = "SettingButton"

        #Fixed sizes
        self.function_button.setFixedSize(150,32)
        self.credit_button.setFixedSize(150, 32)
        self.info_button.setFixedSize(150, 32)
        self.setting_button.setFixedSize(150, 32)
        self.setFixedHeight(33)

        #Set content font
        font = QFont("JetBrains Mono", 10)
        self.function_button.setFont(font)
        self.credit_button.setFont(font)
        self.info_button.setFont(font)
        self.setting_button.setFont(font)
        #Set content text
        self.function_button.setText("Functions")
        self.credit_button.setText("About")
        self.info_button.setText("Help")
        self.setting_button.setText("Settings")

        #Layout: Horizontal
        layout = QHBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        #Add elements
        layout.addWidget(self.function_button)
        layout.addWidget(self.setting_button)
        layout.addWidget(self.credit_button)
        layout.addWidget(self.info_button)
        # Spacer
        layout.addSpacerItem(self.side_spacer)
        #Set layout
        self.setLayout(layout)

        #Apply css
        self.apply_css()

    def apply_css(self):

        self.setStyleSheet("""
                        OptionsMenuWidget{
                            background-color: #06538c;
                        }
                        QPushButton{
                            color: white;
                            background-color: #06538c;
                            border: none;
                        }
                        QPushButton:last-child{
                            border-right: none;
                        }
                        QPushButton:hover{
                            background-color: #044b80;
                        }
                    """)

class ViewMenuWidget(QFrame):

    def __init__(self):
        super().__init__()

        #Important attribute
        self.number_of_view = 4

        #Define elements
        #We need 4 view widgets
        self.function_widget = FunctionsConsoleWidget()
        self.about_widget = AboutWidget()
        self.help_widget = ScrollableHelpWidget()
        self.settings_widget = SettingsWidget()

        #List of all the widget within for easy access
        self.views = []
        self.views.extend([self.function_widget, self.about_widget, self.help_widget, self.settings_widget])

        # For easy customization we define a name for the widget itself and widgets within
        self.setObjectName("ViewMenu")


        #Layout: Neither vertical nor horizontal
        #so that the widgets can overlay one another
        self.layout = QStackedLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.function_widget)
        self.layout.addWidget(self.about_widget)
        self.layout.addWidget(self.help_widget)
        self.layout.addWidget(self.settings_widget)
        #Set layout
        self.setLayout(self.layout)

        #DEBUG:
        self.view_widget(0)

    def view_widget(self, number : int):
        #Check
        if number >= self.number_of_view:
            return
        self.layout.setCurrentWidget(self.views[number])

class ViewWindowWithTopMenuWidget(QWidget):

    def __init__(self):
        super().__init__()

        #Widget definition
        self.option_bar = OptionsMenuWidget()
        self.stacked_widgets = ViewMenuWidget()

        #Layout: Vertical
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        #Add elements:
        layout.addWidget(self.option_bar)
        layout.addWidget(self.stacked_widgets)
        # Set layout
        self.setLayout(layout)