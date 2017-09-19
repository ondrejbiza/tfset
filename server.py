from http.server import BaseHTTPRequestHandler, HTTPServer
import multiprocessing, urllib

class SessionServer(HTTPServer):

  def __init__(self, tensors, session, address="127.0.0.1", port=8000):

    super(HTTPServer, self).__init__((address, port), self.RequestHandler)

    manager = multiprocessing.Manager()
    self.shared = manager.dict()

    self.shared["tensors"] = tensors
    self.shared["session"] = session
    self.shared["tensor_names"] = [tensor.name for tensor in tensors]

    self.shared["events"] = manager.list()
    self.shared["past_events"] = manager.list()

    print("init")

  class RequestHandler(BaseHTTPRequestHandler):

    def do_POST(self):
      length = int(self.headers['Content-Length'])
      post_data = urllib.parse.parse_qs(self.rfile.read(length).decode('utf-8'))

      error = False
      iteration = None
      tensor_name = None
      value = None

      if "iteration" in post_data and "tensor_name" in post_data and "value" in post_data:

        try:
          iteration = int(post_data["iteration"][0])
        except ValueError:
          error = True

        tensor_name = post_data["tensor_name"][0]
        value = post_data["value"][0]

        if "value_type" in post_data:
          value_type = post_data["value_type"][0]

          if value_type == "int":
            value = int(value)
          elif value_type == "float":
            value = float(value)
          elif value_type == "string":
            pass
          else:
            error = True
      else:
        error = True


      if not error:
        self.add_event(iteration, tensor_name, value)
        self.send_response_only(200)
      else:
        self.send_error(400, "Invalid add event request.")

      self.end_headers()

    def do_DELETE(self):
      length = int(self.headers['Content-Length'])
      post_data = urllib.parse.parse_qs(self.rfile.read(length).decode('utf-8'))

      error = False
      event_idx = None

      if "event_idx" in post_data:
        event_idx = int(post_data["event_idx"][0])

        if event_idx >= len(self.server.shared["events"]):
          error = True
      else:
        error = True

      if not error:
        del self.server.shared["events"][event_idx]
        self.send_response_only(200)
      else:
        self.send_error(400, "Invalid delete event request.")

      self.end_headers()

    def add_event(self, iteration, tensor_name, value):
      self.server.shared["events"].append(Event(iteration, tensor_name, value))

  def check_events(self, iteration):

    for idx, event in enumerate(reversed(self.shared["events"])):

      if event.iteration <= iteration:
        self.assign_value(event.tensor_name, event.value)
        del self.shared["events"][idx]

  def assign_value(self, tensor_name, value):

    tensor_index = self.shared["tensor_names"].index(tensor_name)
    tensor = self.shared["tensors"][tensor_index]
    self.shared["session"].run(tensor.assign(value))

class Event:

  def __init__(self, iteration, tensor_name, value):

    self.iteration = iteration
    self.tensor_name = tensor_name
    self.value = value


httpd = SessionServer([], None)
print("Running server.")
httpd.serve_forever()