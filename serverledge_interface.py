import etcd3
import grequests
import json

class ServerLedgeInterface:

    @staticmethod
    def get_etcd_elements(ip : str, port : int):
        etcd = etcd3.client(host=ip, port=port)

        urls = []
        functions = []

        for value, metadata in etcd.get_all():
            if metadata.key.decode().find("function") != -1:
                functions.append(json.loads(value.decode()))
            if metadata.key.decode().find("registry") != -1:
                urls.append({"url": value.decode(), "location": str(metadata.key.decode().split("/")[1])})
        return urls, functions

    @staticmethod
    def get_async_nodes_status(urls: list):
        #This method is for side threads
        node_requests = []
        for url in urls:
            node_requests.append(grequests.get(f"{url}/status"))

        responses = grequests.map(node_requests)
        responses_decoded = []

        for response, url in zip(responses,urls):
            if not response:
                responses_decoded.append({"Error_Code": f"Not active", "Url": f"{url}"})
            elif response.status_code == 200:
                responses_decoded.append(json.loads(response.content.decode()))
            else:
                responses_decoded.append({"Error_Code": f"Not available", "Url": f"{url}"})
        return responses_decoded

    @staticmethod
    def get_async_node_status_requests(urls: list):
        #This method id for the main thread, in case it needs to send requests
        #and then do something instead of waiting
        node_requests = []
        for url in urls:
            #Create request...
            request = grequests.get(f"{url}/status")
            #...and then sends it without waiting for results
            grequests.send(request)
            #...memorize request
            node_requests.append(request)
        return node_requests

    @staticmethod
    def get_async_node_status_response(node_requests: list):
        #This method is for the main thread, takes previously created async requests
        #and 'finishes' them returning a list of responses
        node_responses = grequests.map(node_requests)
        responses_decoded = []
        for response in node_responses:
            if not response:
                responses_decoded.append({"Error_Code": f"Not active"})
            elif response.status_code == 200:
                responses_decoded.append(json.loads(response.content.decode()))
            else:
                responses_decoded.append({"Error_Code": f"Not available"})
        return responses_decoded

    @staticmethod
    def post_invoke_sync_function(url : str, function_name : str, param_string : str):

        param_dict = ServerLedgeInterface.string_to_dict(param_string)

        parameters = {
            "Params": param_dict,
            "CanDoOffloading": True,
            "Async": False,
            "ReturnOutput": True
        }


        sync_request = grequests.post(f"{url}/invoke/{function_name}",json = parameters)
        responses = grequests.map([sync_request])
        #We get one response, so...
        if responses[0] is None:
            return {"Error_Code": "Not active"}
        if responses[0].status_code == 404:
            return {"Error_Code": "Unknown function"}
        if responses[0].status_code == 429:
            return {"Error_Code": "Load to high"}
        if responses[0].status_code == 500:
            return {"Error_Code": "Invocation failed"}
        return json.loads(responses[0].content.decode())

    @staticmethod
    def post_invoke_async_function(url : str, function_name : str, param_string : str):

        param_dict = ServerLedgeInterface.string_to_dict(param_string)

        parameters = {
            "Params": param_dict,
            "CanDoOffloading": True,
            "Async": True,
            "ReturnOutput": True
        }

        sync_request = grequests.post(f"{url}/invoke/{function_name}", json=parameters)
        responses = grequests.map([sync_request])
        # We get one response, so...
        if responses[0] is None:
            return {"Error_Code": "Not active"}
        if responses[0].status_code == 404:
            return {"Error_Code": "Unknown function"}
        if responses[0].status_code == 429:
            return {"Error_Code": "Load to high"}
        if responses[0].status_code == 500:
            return {"Error_Code": "Invocation failed"}
        return json.loads(responses[0].content.decode())

    @staticmethod
    def get_poll_async_functions(url : str, req_ids : list):

        responses = grequests.map([grequests.get(f"{url}/poll/{req_id}") for req_id in req_ids])

        decoded_responses = []
        for response in responses:
            if response is None:
                decoded_responses.append({"Error_Code": "Not active"})
                continue
            if response.status_code == 404:
                decoded_responses.append({"Error_Code": "Result not found"})
            if response.status_code == 429:
                decoded_responses.append({"Error_Code": "Load too high"})
            if response.status_code == 500:
                decoded_responses.append({"Error_Code": "General fail"})
            if response.status_code == 200:
                decoded_responses.append(json.loads(response.content.decode()))
        return decoded_responses

    @staticmethod
    def string_to_dict(string : str):
        #Remove delimiters ':' and '=' end split single elements
        string_list = string.replace(":"," ").replace("="," ").split()
        #Construct list of keys and values
        keys = []
        values = []
        dictionary = {}
        for i in range(len(string_list)):
            if i%2 == 0:
                keys.append(string_list[i])
            else:
                values.append(string_list[i])
        for i in range(len(keys)):
            dictionary[keys[i]] = values[i]
        #return dict
        return dictionary
