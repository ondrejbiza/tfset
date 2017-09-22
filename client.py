import argparse, json, requests, sys

def decode_json(content):
  return json.loads(content.decode())

def print_events(events):

  if len(events) > 0:
    for event in events:
      print("iteration: {:d}, tensor: {:s}, value: {}".format(event["iteration"], event["tensor_name"], event["value"]))
  else:
    print("None")

def main(args):

  while True:
    address = "{:s}:{:d}".format(args.address, args.port)

    r = requests.get(address)
    content = decode_json(r.content)

    print()
    print("Scheduled events:")
    print_events(content["events"])
    print("Past events:")
    print_events(content["past_events"])

    print()
    print("Actions: 1. schedule event, 2. remove event.")

    while True:
      try:
        action_id = int(input())
        break
      except ValueError:
        print("1 or 2")

    if action_id == 1:

      while True:
        try:
          iteration = int(input("iteration: "))
          break
        except ValueError:
          print("Integer, please.")

      tensor_name = input("tensor name: ")
      value = input("value: ")

      while True:
        value_type = input("value type: ")

        if value_type not in ["int", "float", "string"]:
          print("Integer, float or string, please.")
        else:
          break

      event = {
        "iteration": iteration,
        "tensor_name": tensor_name,
        "value": value,
        "value_type": value_type
      }
      requests.post(address, data=event)

parser = argparse.ArgumentParser()
parser.add_argument("-a", "--address", default="http://127.0.0.1")
parser.add_argument("-p", "--port", type=int, default=8084)
parsed = parser.parse_args()

try:
  main(parsed)
except requests.exceptions.ConnectionError:
  print("Connection error.")