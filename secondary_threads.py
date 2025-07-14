from os import close
from time import sleep
from PyQt5.QtCore import QThread, pyqtSignal
from serverledge_interface import ServerLedgeInterface

class DataUpdateThread(QThread):
    # Signals ("StopLights")
    node_widget_add_new = pyqtSignal(list)
    function_widget_add_new = pyqtSignal(list)
    node_widget_status_updated = pyqtSignal(list)
    etcd_widget_set_status = pyqtSignal(bool)

    def __init__(self, etcd_ip, etcd_port, delay_seconds):
        super().__init__()
        self.etcd_ip = etcd_ip
        self.etcd_port = etcd_port
        self.delay_seconds = delay_seconds
        self.etcd_status_online = False

    def run(self):

        #nodes urls
        urls = []
        functions = []

        while True:
            #Search for new nodes & functions
            #Lists for new nodes anf function discovered
            new_urls_and_locations = []
            new_functions = []

            #Lists for etcd responses
            etcd_urls_and_locations = []
            etcd_functions = []

            #Catch for exception in case:
            #wrong etcd_ip
            #various connection errors
            exception_flag = False
            try:
                etcd_urls_and_locations, etcd_functions = ServerLedgeInterface.get_etcd_elements(self.etcd_ip,self.etcd_port)
            except Exception:
                #Communicates disconnect
                exception_flag = True
                self.etcd_widget_set_status.emit(False)
            #Communicates connection
            if exception_flag is False:
                self.etcd_widget_set_status.emit(True)


            #See if is a new node:
            for url_and_location in etcd_urls_and_locations:
                if url_and_location.get("url") not in urls:
                    urls.append(url_and_location.get("url"))
                    new_urls_and_locations.append(url_and_location)
            for function in etcd_functions:
                if function not in functions:
                    functions.append(function)
                    new_functions.append(function)


            #emit new urls so that the main thread can create node widgets and add them
            #to the side menu
            self.node_widget_add_new.emit(new_urls_and_locations.copy())
            #Here the thread will emit new functions!
            self.function_widget_add_new.emit(new_functions.copy())

            for i in range(3):
                # Gets updated node statuses
                updated_node_status_list = ServerLedgeInterface.get_async_nodes_status(urls)
                # Send signal with updated node statuses
                self.node_widget_status_updated.emit(updated_node_status_list.copy())
                # Sleep
                sleep(self.delay_seconds)

class InvokedFunctionSyncThread(QThread):

    #For communicating outcome and result
    write_result = pyqtSignal(str,str, bool)

    def __init__(self,url,function_name,param_string):
        super().__init__()

        self.url = url
        self.function_name = function_name
        self.param_string = param_string

    def run(self):
        # Post sync request
        response = ServerLedgeInterface.post_invoke_sync_function(self.url,self.function_name,self.param_string)
        #Write outcome & result string, and sending it to main thread
        subject = self.url.capitalize().replace("Http://","").split(":")[0]
        if 'Error_Code' not in response.keys():
            #Outcome string
            outcome = "Failure!"
            if response.get("Success") is True:
                outcome = "Success!"
            #Output string
            result = response.get("Result")
            #Analitics
            time = response.get("ResponseTime")
            self.write_result.emit(subject,f"Outcome: {outcome} - ResponseTime: {time} - Output: {result}",True)
        else:
            self.write_result.emit(subject, response.get("Error_Code"),False)

class InvokedFunctionAsyncThread(QThread):

    write_result = pyqtSignal(str, str, bool)

    def __init__(self, node_widget, function_name, param_string):
        super().__init__()

        self.node_widget = node_widget
        self.url = node_widget.url
        self.function_name = function_name
        self.param_string = param_string

    def run(self):
        # Post sync request
        response = ServerLedgeInterface.post_invoke_async_function(self.url, self.function_name, self.param_string)
        #Write outcome to log
        subject = self.url.capitalize().replace("Http://", "").split(":")[0]
        if 'Error_Code' not in response.keys():
            self.write_result.emit(subject, f"Async request sent with success!",True)
            # Saving req_id and params in dict to node_widget personal list
            pull_dict = {'pull_id': response.get("ReqId"), 'params': self.param_string}
            self.node_widget.extend_pull_ids([pull_dict])
        else:
            self.write_result.emit(subject, response.get("Error_Code"),False)

class PullThread(QThread):

    write_result = pyqtSignal(str, str, bool)

    def __init__(self, selected_node):
        super().__init__()

        self.url = selected_node.url
        #Gets a copy of current pull_ids stored
        self.pull_ids = selected_node.get_pull_ids()
        self.selected_node = selected_node

    def run(self):

        #Construct list with only pull_ids
        only_pull_ids_list = [pull_dict.get('pull_id') for pull_dict in self.pull_ids]
        responses = ServerLedgeInterface.get_poll_async_functions(self.url,only_pull_ids_list)
        #Copy of list pull_ids
        copy_pull_ids = self.pull_ids.copy()
        for response, i in zip(responses,range(len(responses))):
            # Write outcome & result string, and sending it to main thread
            subject = self.url.capitalize().replace("Http://", "").split(":")[0]
            if 'Error_Code' not in response.keys():
                #Safe removal of pull_id
                pull_id = copy_pull_ids[i]
                self.pull_ids.remove(pull_id)
                # Outcome string
                outcome = "Failure!"
                if response.get("Success") is True:
                    outcome = "Success!"
                # Output string
                result = response.get("Result")
                # Time
                time = response.get("ResponseTime")
                self.write_result.emit(subject, f"Pulled: Outcome: {outcome} - ResponseTime: {time} - Output: {result} "
                                                f"with params: {pull_id.get('params')}",True)
            else:
                self.write_result.emit(subject, response.get("Error_Code"),False)
        #Remove satisfied pull_ids from node pull_ids
        self.selected_node.remove_pull_ids(self.pull_ids)

class WriteFileThread(QThread):

    write_outcome = pyqtSignal(bool)

    def __init__(self,rows,path):
        super().__init__()

        self.rows = rows
        self.path = path

    def run(self):
        # Overwrite
        try:
            file = open(self.path,"w")
            for row in self.rows:
                file.write(f"{row}\n")
            file.close()
        except Exception:
            self.write_outcome.emit(False)
            return
        self.write_outcome.emit(True)