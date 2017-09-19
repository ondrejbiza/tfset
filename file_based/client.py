import argparse, json, os

from server import TFServer

def main(args):

  file_path = os.path.join(args.dir, TFServer.FILE)

  if not os.path.exists(file_path):
    print("{:s} not found.".format(file_path))

  while True:

    with open(file_path, "r") as file:
      params = json.load(file)

    print("static parameters:")
    for key, val in params[TFServer.STATIC_PARAMETERS]:
      print("{:s}: {}".format(key, val))

    print("modifiable parameters:")
    for key, val in params[TFServer.MODIFIABLE_PARAMETERS]:
      print("{:s}: {}".format(key, val))

    print("modify:")
    for key, val in params[TFServer.MODIFIABLE_PARAMETERS]:
      print(key)
      modify = input("modify: (y/n)")

      if modify == "y":
        new_val = float(input("value: "))
        params[key] = new_val

    with open(file_path, "w") as file:
      json.dump(params, file)

parser = argparse.ArgumentParser()
parser.add_argument("dir", help="session directory")
parsed = parser.parse_args()
main(parsed)