import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton
from serverledge_items_descriptor_widgets import NodeWidget, FunctionWidget
from secondary_threads import DataUpdateThread, InvokedFunctionSyncThread, InvokedFunctionAsyncThread, PullThread, WriteFileThread
from main_ui_widgets import TopWidget, ContentWidget
from dynamic_menu_widgets import SubMenuWidget


class ServerLedgeGUI(QMainWindow):

    def __init__(self):
        super().__init__()

        #Screen sizes
        screen = app.primaryScreen()
        screen_width = screen.size().width()
        screen_height = screen.size().height()

        # Functional attributes
        # Direct access to node widgets
        self.node_widgets = []
        # Node widget with whom we get the url for forwarding function invocations
        self.selected_node = None
        # Function invocation modality: default sync
        self.selected_mod = "Sync"
        # Dict for sub-menu for group of node widgets based on location
        self.sub_menus_location_widgets = {}

        # Read from conf file
        conf = []
        with open("./conf.txt", "r") as file:
            for line in file:
                conf.append(str(line).replace("\n", ""))
        # Check values read
        if conf[0] is None or conf[1] is None or conf[2] is None:
            #Default
            conf = ["172.16.5.155","2379","2"]

        # Window options
        # Size & spawn location
        self.setGeometry(int((screen_width//2) - 1200//2),int((screen_height//2) - 930//2), 1200, 930)
        # Frameless & without background
        self.setWindowFlag(Qt.FramelessWindowHint)
        # Application icon
        self.setWindowIcon(QIcon("images/stemma_unipi.svg.png"))

        # Widget at the base of the gui structure
        self.central_widget = QWidget()
        self.central_widget.setContentsMargins(0,0,0,0)
        self.setCentralWidget(self.central_widget)
        self.top_widget = TopWidget()
        self.main_widget = ContentWidget()

        # For easy future access we define references to the main widgets
        # Scrolling left side node menu widget
        self.node_widgets_menu = self.main_widget.scrollable_node_menu
        # Stacked widget widgets
        self.stacked_widgets = self.main_widget.stacked_widgets_with_menu.stacked_widgets
        self.bar_widget_selector = self.main_widget.stacked_widgets_with_menu.option_bar
        # Function widget widgets
        self.functions_widget = self.stacked_widgets.function_widget
        self.functions_params_input = self.functions_widget.log.input
        self.functions_button_menu = self.functions_widget.function_menu.button_menu
        self.functions_descriptor_menu = self.functions_widget.function_menu.function_menu
        # Settings widget widgets
        self.settings_widget = self.stacked_widgets.settings_widget
        self.settings_form = self.settings_widget.form

        # Combine the widget in a vertical layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(self.top_widget)
        main_layout.addWidget(self.main_widget)
        self.central_widget.setLayout(main_layout)

        # Event signals initializer for always present widgets
        self.init_interactions()

        #Update etcd widget with conf settings values
        self.main_widget.etcd_widget.update_etcd_ip(conf[0])
        #Update settings form to display current settings
        self.settings_form.set_text_forms(conf[0],conf[1],int(conf[2]))

        #Side thread declaration and settings for sensing new nodes and updating cpu and memory resources
        #Thread for updating nodes infos
        self.update_thread = DataUpdateThread(conf[0], int(conf[1]), int(conf[2]))
        self.update_thread.node_widget_add_new.connect(self.add_new_node_widgets)
        self.update_thread.function_widget_add_new.connect(self.add_new_function_widgets)
        self.update_thread.node_widget_status_updated.connect(self.update_node_widgets)
        self.update_thread.etcd_widget_set_status.connect(self.toggle_etcd_status)
        self.update_thread.start()
        #List of threads for sync/async/pull requests to serverledge nodes
        self.function_threads = []

    def init_interactions(self):
        #View change from top buttons options
        for menu_option in self.bar_widget_selector.buttons:
            menu_option.clicked.connect(lambda state, btn=menu_option : self.change_view(btn))
        #Interactions with the buttons from the functions menu
        self.functions_button_menu.clear_button.clicked.connect(self.clear_function_log)
        self.functions_button_menu.mod_button.clicked.connect(self.toggle_modality)
        self.functions_button_menu.pull_button.clicked.connect(self.pull_responses)
        #DEBUG:
        self.functions_button_menu.add_fake_node.clicked.connect(self.add_fake_node)
        #Interactions with the submit button from the settings widget
        self.settings_form.submit_button.clicked.connect(self.update_conf_file)

    def add_new_node_widgets(self, urls_and_locations : list):

        for url_and_location in urls_and_locations:
            # Get url
            url = url_and_location.get("url")
            # Get location
            location = url_and_location.get("location")

            # See if is a new location
            # If new create new sub-menu
            if location not in self.sub_menus_location_widgets.keys():
                # New sub-menu
                self.sub_menus_location_widgets.update({location: SubMenuWidget(location)})
                # Append new sub-menu to main menu on the left side
                self.node_widgets_menu.menu_widget.addWidget(self.sub_menus_location_widgets.get(location))

            #Creating node widget for each NEW node
            new_widget = NodeWidget(url)
            #Selectable node for invoked function
            new_widget.icon.clicked.connect(lambda state, widget=new_widget: self.select_node(widget))
            #Append to local list for easy access
            self.node_widgets.append(new_widget)
            #Append to right sub-menu
            sub_menu = self.sub_menus_location_widgets.get(location)
            sub_menu.addWidget(new_widget)
            #Updating total number widgets
            self.main_widget.etcd_widget.plus_node()


    def add_new_function_widgets(self, functions : list):
        for function in functions:
            #Creating new function widget
            function_widget = FunctionWidget(function.get("Name"),function.get("MemoryMB"),function.get("CPUDemand"))
            #Adding function to invoke button
            function_widget.invoke_button.clicked.connect(lambda state, widget=function_widget: self.invoke_function(widget))
            #Inserting function widget in correspondent menu
            self.functions_descriptor_menu.menu_widget.addWidget(function_widget)

    def update_node_widgets(self, updated_node_statuses : list):
        #Method used by the side thread invoked with a signal
        #Updating
        for updated_node_status, node_widget in zip(updated_node_statuses, self.node_widgets):
            if 'Error_Code' not in updated_node_status.keys():
                node_widget.update_node_status(updated_node_status.get('Url'),updated_node_status.get('AvailableCPUs'),
                                               updated_node_status.get('AvailableMemMB'))
                node_widget.set_online()
            else:
                node_widget.update_node_status(updated_node_status.get('Url'), "--","--")
                node_widget.set_offline()

    def toggle_etcd_status(self, status : bool):
        if status is True:
            self.main_widget.etcd_widget.set_online()
        else:
            self.main_widget.etcd_widget.set_offline()

    def update_conf_file(self):
        # Getting infos
        new_etcd_ip = self.settings_form.etcd_ip_form.text()
        new_etcd_port = self.settings_form.etcd_port_form.text()
        new_frequency = self.settings_form.frequency_update_form.text()

        write_thread = WriteFileThread([new_etcd_ip,new_etcd_port,new_frequency],"./conf.txt")

        # Connect signal to write on log the outcome
        write_thread.write_outcome.connect(self.write_on_settings_log)

        # Once finished it gets removed
        write_thread.finished.connect(lambda: self.remove_finished_threads(write_thread))
        self.function_threads.append(write_thread)
        #Starting thread
        write_thread.start()

        #Then we will update the etcd_ip, etcd_port and seconds delay of the update thread
        self.update_thread.etcd_ip = new_etcd_ip
        self.update_thread.etcd_port = new_etcd_port
        self.update_thread.delay_seconds = int(new_frequency)
        #Update etcd widget
        self.main_widget.etcd_widget.update_etcd_ip(new_etcd_ip)

    def change_view(self, button : QPushButton):
        dictionary = {"FunctionButton": 0, "CreditButton": 1, "InfoButton": 2, "SettingButton": 3}
        self.stacked_widgets.view_widget(dictionary.get(button.object_name))

    def select_node(self, clicked_widget : NodeWidget):
        #Double click: deselect!
        if self.selected_node is clicked_widget:
            self.selected_node.deselect()
            self.selected_node = None
            return
        #Select another node
        if self.selected_node is not clicked_widget:
            # See if node is offline
            if clicked_widget.online is False:
                return
            #Deselect old selection
            if self.selected_node is not None:
                self.selected_node.deselect()
            #Set new selection
            self.selected_node = clicked_widget
            self.selected_node.select()

    def toggle_modality(self):
        if self.selected_mod == "Sync":
            self.selected_mod = "Async"
            self.functions_button_menu.change_mod_text("Mode: Async")
        else:
            self.selected_mod = "Sync"
            self.functions_button_menu.change_mod_text("Mode: Sync")

    def write_on_log(self,subject:str ,text:str ,good:bool):
        self.functions_widget.add_row_text(subject, text, good)

    def clear_function_log(self):
        self.functions_widget.clear_text()

    def write_on_settings_log(self, good: bool):
        self.settings_widget.write_outcome(good)

    def remove_finished_threads(self,thread):
        if thread in self.function_threads:
            self.function_threads.remove(thread)

    def invoke_function(self, function_widget : FunctionWidget):
        # Check selected node
        if self.selected_node is None:
            self.write_on_log("System","No nodes selected, select an active node by clicking on the icon on the menu on the left!",False)
            return
        # Check if node is online
        if self.selected_node.online is False:
            self.write_on_log("System","Selected node has passed from online to offline!",False)
            return
        param_string = self.functions_params_input.text()
        if self.selected_mod == "Sync":
            function_thread = InvokedFunctionSyncThread(self.selected_node.url, function_widget.function_name, param_string)
            #For write outcome and result
            function_thread.write_result.connect(self.write_on_log)
        else:
            function_thread = InvokedFunctionAsyncThread(self.selected_node, function_widget.function_name, param_string)
            # For write outcome and result of async request
            function_thread.write_result.connect(self.write_on_log)


        # Once finished it gets removed
        function_thread.finished.connect(lambda: self.remove_finished_threads(function_thread))
        self.function_threads.append(function_thread)
        #Starting thread
        function_thread.start()

    def pull_responses(self):
        #If there is not a node selected
        if self.selected_node is None:
            self.write_on_log("System", "No nodes selected, select an active node by clicking on the icon on the menu on the left!",False)
            return
        #If list is empty
        if not self.selected_node.pull_ids:
            ip = self.selected_node.url.replace("Http://", "").split(":")[0]
            self.write_on_log("System",f"Node {ip} does not have pending function outcomes!",False)
            return
        function_thread = PullThread(self.selected_node)
        # For write outcome and result
        function_thread.write_result.connect(self.write_on_log)
        # Once finished it gets removed
        function_thread.finished.connect(lambda: self.remove_finished_threads(function_thread))
        self.function_threads.append(function_thread)
        # Starting thread
        function_thread.start()

    #DEBUG:
    def add_fake_node(self):
        location = self.functions_params_input.text()
        self.add_new_node_widgets([{"url": "Fake node", "location": location}])

app = QApplication([])
# Create window
window = ServerLedgeGUI()
# Show window & dont make it disappear
window.show()
sys.exit(app.exec_())

