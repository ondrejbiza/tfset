import unittest, server, requests, json
import tensorflow as tf

class TestServer(unittest.TestCase):

  address = "http://127.0.0.1:8084"

  def setUp(self):
    self.tensor = tf.get_variable("tensor", initializer=tf.constant(0.1, dtype=tf.float32))
    self.session = tf.Session()
    self.session.run(tf.global_variables_initializer())

    self.httpd, self.thread = server.run_server([self.tensor], self.session)

  def tearDown(self):
    self.httpd.shutdown()
    self.thread.join(timeout=10)
    self.session.close()
    tf.reset_default_graph()

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
      "tensor_name": "tensor:0",
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
      "tensor_name": "tensor:0",
      "value": 0.001
    }
    event_2 = {
      "iteration": 100,
      "tensor_name": "tensor:0",
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
      "tensor_name": "tensor:0",
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

  def test_trigger_event(self):
    event = {
      "iteration": 10,
      "tensor_name": "tensor:0",
      "value": 0.001
    }

    data = event.copy()
    data["value_type"] = "float"

    post_r = requests.post(self.address, data=data)
    self.assertEqual(post_r.status_code, 200)

    self.httpd.check_events(5)
    self.assertTrue(len(self.httpd.shared["events"]) == 1)
    self.assertTrue(len(self.httpd.shared["past_events"]) == 0)

    self.httpd.check_events(15)
    self.assertTrue(len(self.httpd.shared["events"]) == 0)
    self.assertTrue(len(self.httpd.shared["past_events"]) == 1)
    self.assertAlmostEqual(self.session.run(self.tensor), event["value"], places=3)

  @staticmethod
  def __decode_json(content):
    return json.loads(content.decode())