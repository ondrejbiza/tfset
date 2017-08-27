import json, os

class TFServer:

  FILE = "session.json"
  MODIFIABLE_PARAMETERS = "modifiable_parameters"
  STATIC_PARAMETERS = "static_parameters"
  RECEIVED = "received"

  def __init__(self, path, overwrite=True):

    self.path = path
    self.modifiable_parameters = None
    self.static_parameters = None
    self.session = None

    if not os.path.exists(path):
      os.makedirs(path)
    elif not os.path.isdir(path):
      raise ValueError("{:s} is not a directory.".format(path))

    self.file = os.path.join(path, self.FILE)

    if os.path.exists(self.file):

      if overwrite:
        os.remove(self.file)
      else:
        raise ValueError("{:s} already exists. Either choose a different directory or set overwrite to True."
                         .format(self.file))

  def register_session(self, modifiable_parameters, static_parameters, session):

    if self.session is not None:
      raise ValueError("A session is already registered.")

    self.modifiable_parameters = modifiable_parameters
    self.static_parameters = static_parameters
    self.session = session

    self.__save_params()

  def check_update(self):

    params = self.__load_params()
    params = self.__map_names_to_params(params, self.modifiable_parameters)

    changed = self.__find_changes(self.modifiable_parameters, params)

    if len(changed.keys()) > 0:
      print("parameter changes:")

      for key, val in changed.items():
        print("{:s}: {}".format(key.name, val))
        self.session.run(key.assign(val))

    self.modifiable_parameters = params
    self.__save_params()

  @staticmethod
  def __map_params_to_names(params):

    names = {}

    for key, item in params.items():
      names[key.name] = item

    return names

  @staticmethod
  def __map_names_to_params(names, params):

    new_params = {}

    for key, item in names.items():

      param = None
      for key2, item2 in params.items():
        if key2.name == key:
          param = key2

      assert param is not None

      new_params[param] = item

    return new_params

  @staticmethod
  def __find_changes(old_params, new_params):

    changed = {}

    for key, new_val in new_params.items():

      old_val = old_params[key]

      if old_val != new_val:
        changed[key] = new_val

    return changed

  def __save_params(self):

    obj = {
      self.MODIFIABLE_PARAMETERS: self.__map_params_to_names(self.modifiable_parameters),
      self.STATIC_PARAMETERS: self.__map_params_to_names(self.static_parameters),
      self.RECEIVED: True
    }

    with open(self.file, "w") as file:
      json.dump(obj, file)

  def __load_params(self):

    with open(self.file, "r") as file:
      obj = json.load(file)

    return obj[self.MODIFIABLE_PARAMETERS]