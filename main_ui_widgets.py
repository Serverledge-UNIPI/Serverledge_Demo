from titlebar_widgets import TitleBarWindows
from stacked_widgets_widgets import ViewWindowWithTopMenuWidget
from dynamic_menu_widgets import ScrollableMenuWidget
from serverledge_items_descriptor_widgets import EtcdWidget
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget


class TopWidget(QWidget):

    def __init__(self):
        super().__init__()

        #Widgets definition
        self.title_bar = TitleBarWindows()

        #Layout: Vertical
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        #Add elements
        layout.addWidget(self.title_bar)
        #Set layout
        self.setLayout(layout)

class ContentWidget(QWidget):

    def __init__(self):
        super().__init__()

        #Widgets definition
        self.scrollable_node_menu = ScrollableMenuWidget()
        self.etcd_widget = EtcdWidget()
        self.stacked_widgets_with_menu = ViewWindowWithTopMenuWidget()

        #Adding etcd widget to the scrollable_node_menu
        self.scrollable_node_menu.menu_widget.addWidget(self.etcd_widget)

        #Layout: Horizontal
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        #Add elements
        layout.addWidget(self.scrollable_node_menu)
        layout.addWidget(self.stacked_widgets_with_menu)
        #Set layout
        self.setLayout(layout)