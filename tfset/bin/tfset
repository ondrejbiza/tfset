#!/usr/bin/env python

import argparse, json, requests

def decode_json(content):
  """
  Decode a JSON string.
  :param content:     JSON string.
  :return:            JSON object.
  """
  return json.loads(content.decode())

def print_events(events):
  """
  Print interactive-tensorflow events.
  :param events:    List of events.
  :return:          None.
  """

  if len(events) > 0:
    for event in events:
      print("iteration: {:d}, tensor: {:s}, value: {}".format(event["iteration"], event["tensor_name"], event["value"]))
  else:
    print("None")

def main(args):

  address = "{}:{}".format(args.address, args.port)

  if args.status:
    # get status of the server

    r = requests.get(address)
    content = decode_json(r.content)

    if r.status_code != 200:
      print("Status request error.")
      exit(1)

    if "events" not in content and "past_events" not in content and "tensor_names" not in content and \
       "last_check_iteration" not in content:
      print("Response format error.")
      exit(1)

    print("Status:")
    print()

    print("Events:")
    print_events(content["events"])
    print()

    print("Past events:")
    print_events(content["past_events"])
    print()

    print("Tensor names:")
    if len(content["tensor_names"]) > 0:
      for tensor_name in content["tensor_names"]:
        print(tensor_name)
    else:
      print("None")
    print()

    print("Last iteration checked: {:d}".format(content["last_check_iteration"]))

  elif args.add:
    # add an event

    if None in [args.name, args.iter, args.value]:

      print("Please specify tensor name (--name), iteration (--iter) and value (--value).")
      exit(1)

    data = {
      "tensor_name": args.name,
      "iteration": args.iter,
      "value": args.value,
    }

    post_r = requests.post(address, data=data)

    if post_r.status_code == 200:
      print("Event successfully added.")
    else:
      print("Error while adding the event.")
      exit(1)

  elif args.remove:
    # remove an event

    if None in [args.eidx]:

      print("Please specify event index (--eidx).")
      exit(1)

    data = {
      "event_idx": args.eidx
    }

    post_r = requests.post(address, data=data)

    if post_r.status_code == 200:
      print("Event successfully removed.")
    else:
      print("Error while removing the event.")
      exit(1)

  else:

    print("No action specified.")
    exit(1)

parser = argparse.ArgumentParser("Client for interactive-tensorflow server.")

# action parameters
parser.add_argument("-s", "--status", default=False, action="store_true", help="print status (tensor names, registered events, ...)")
parser.add_argument("-a", "--add", default=False, action="store_true", help="add event")
parser.add_argument("-r", "--remove", default=False, action="store_true", help="remove event")

# add parameters
parser.add_argument("-n", "--name", help="new event - tensor name")
parser.add_argument("-i", "--iter", type=int, help="new event - iteration")
parser.add_argument("-v", "--value", help="new event - value")

# remove parameters
parser.add_argument("-e", "--eidx", type=int, help="index of an event that should be removed")

# connection parameters
parser.add_argument("--address", default="http://127.0.0.1", help="address of the server")
parser.add_argument("--port", type=int, default=8084, help="port of the server")

parsed = parser.parse_args()

# catch all request connection errors
if __name__ == "__main__":
  try:
    main(parsed)
  except requests.exceptions.ConnectionError:
    print("Connection error.")
    exit(1)
