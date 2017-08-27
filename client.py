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

parser = argparse.ArgumentParser()
parser.add_argument("dir", help="session directory")
parsed = parser.parse_args()
main(parsed)