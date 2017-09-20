import unittest, server, requests, json

class TestServer(unittest.TestCase):

  address = "http://127.0.0.1:8000"

  def setUp(self):
    self.httpd, self.thread = server.run_server([], None)

  def tearDown(self):
    self.httpd.shutdown()
    self.thread.join(timeout=10)

  def test_start_and_stop_server(self):
    pass

  def test_get_events(self):

    r = requests.get(self.address)
    content = self.__decode_json(r.content)

    self.assertEqual(r.status_code, 200)
    self.assertTrue(len(content["events"]) == 0)
    self.assertTrue(len(content["past_events"]) == 0)

  def test_add_event(self):

    event = {
      "iteration": 10,
      "tensor_name": "learning_rate",
      "value": 0.001
    }

    data = event.copy()
    data["value_type"] = "float"

    post_r = requests.post(self.address, data=data)
    self.assertEqual(post_r.status_code, 200)

    get_r = requests.get(self.address)
    content = self.__decode_json(get_r.content)

    self.assertEqual(get_r.status_code, 200)
    self.assertTrue(len(content["events"]) == 1)
    self.assertDictEqual(content["events"][0], event)
    self.assertTrue(len(content["past_events"]) == 0)

  def test_add_events(self):

    event_1 = {
      "iteration": 10,
      "tensor_name": "learning_rate",
      "value": 0.001
    }
    event_2 = {
      "iteration": 100,
      "tensor_name": "save_freq",
      "value": 10
    }

    data_1 = event_1.copy()
    data_1["value_type"] = "float"
    data_2 = event_2.copy()
    data_2["value_type"] = "int"

    post_r = requests.post(self.address, data=data_1)
    self.assertEqual(post_r.status_code, 200)
    post_r = requests.post(self.address, data=data_2)
    self.assertEqual(post_r.status_code, 200)

    get_r = requests.get(self.address)
    content = self.__decode_json(get_r.content)

    self.assertEqual(get_r.status_code, 200)
    self.assertTrue(len(content["events"]) == 2)
    self.assertDictEqual(content["events"][0], event_1)
    self.assertDictEqual(content["events"][1], event_2)
    self.assertTrue(len(content["past_events"]) == 0)

  def test_remove_event(self):
    
    event = {
      "iteration": 10,
      "tensor_name": "learning_rate",
      "value": 0.001
    }

    data = event.copy()
    data["value_type"] = "float"

    post_r = requests.post(self.address, data=data)
    self.assertEqual(post_r.status_code, 200)

    delete_r = requests.delete(self.address, data={
      "event_idx": 0
    })
    self.assertEqual(delete_r.status_code, 200)

    get_r = requests.get(self.address)
    content = self.__decode_json(get_r.content)

    self.assertEqual(get_r.status_code, 200)
    self.assertTrue(len(content["events"]) == 0)
    self.assertTrue(len(content["past_events"]) == 0)

  @staticmethod
  def __decode_json(content):
    return json.loads(content.decode())