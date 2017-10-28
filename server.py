from http.server import BaseHTTPRequestHandler, HTTPServer
import multiprocessing, urllib, json, threading
import tensorflow as tf

class SessionServer(HTTPServer):

  def __init__(self, tensors, session, address="127.0.0.1", port=8084):

    super(HTTPServer, self).__init__((address, port), self.RequestHandler)

    self.tensors = tensors
    self.session = session

    manager = multiprocessing.Manager()
    self.shared = manager.dict()

    self.shared["tensor_names"] = [tensor.name for tensor in tensors]

    tensor_dtypes = []
    for  tensor in tensors:
      if tensor.dtype == tf.string or tensor.dtype.name == "string_ref":
        tensor_dtypes.append(str)
      else:
        np_dtype = tensor.dtype.as_numpy_dtype
        tensor_dtypes.append(type(np_dtype(0).item()))

    self.shared["tensor_dtypes"] = tensor_dtypes

    self.shared["last_check_iteration"] = 0

    self.events = manager.list()
    self.past_events = manager.list()

  def check_events(self, iteration):

    # remember when we last checked
    self.shared["last_check_iteration"] = iteration

    # check if any event is triggered
    events_to_delete = []

    for event in sorted(self.events, key=lambda x: x["iteration"], reverse=True):
      if event["iteration"] <= iteration:
        self.assign_value(event["tensor_name"], event["value"])
        events_to_delete.append(self.events.index(event))

    for event_idx in sorted(events_to_delete, reverse=True):
      self.past_events.append(self.events[event_idx])
      del self.events[event_idx]


  def assign_value(self, tensor_name, value):

    tensor_index = self.shared["tensor_names"].index(tensor_name)
    tensor = self.tensors[tensor_index]
    self.session.run(tensor.assign(value))

  class RequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):

      # events and past_events are a ListProxy that isn't JSON serializable => convert it to Python list
      json_obj = {
        "events": [x for x in self.server.events],
        "past_events": [x for x in self.server.past_events],
        "tensor_names": self.server.shared["tensor_names"],
        "last_check_iteration": int(self.server.shared["last_check_iteration"])
      }

      json_string = json.dumps(json_obj).encode()

      self.send_response(200)
      self.end_headers()
      self.wfile.write(json_string)

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

          tensor_name = post_data["tensor_name"][0]

          if tensor_name in self.server.shared["tensor_names"]:
            tensor_index = self.server.shared["tensor_names"].index(tensor_name)
            tensor_dtype = self.server.shared["tensor_dtypes"][tensor_index]

            value = post_data["value"][0]
            value = tensor_dtype(value)
          else:
            error = True
        except ValueError:
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

        if event_idx >= len(self.server.events):
          error = True
      else:
        error = True

      if not error:
        del self.server.events[event_idx]
        self.send_response_only(200)
      else:
        self.send_error(400, "Invalid delete event request.")

      self.end_headers()

    def add_event(self, iteration, tensor_name, value):
      self.server.events.append({
        "iteration": iteration, "tensor_name": tensor_name, "value": value
      })

    def log_message(self, format, *args):
      return

def run_server(tensors, session, address="127.0.0.1", port=8084):
  httpd = SessionServer(tensors, session, address=address, port=port)

  def worker(server):
    server.serve_forever()

  thread = threading.Thread(target=worker, args=(httpd,), daemon=True)
  thread.start()

  return httpd, thread