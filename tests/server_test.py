import unittest, requests, json
import tensorflow as tf

import tfset

class TestServer(unittest.TestCase):

  address = "http://127.0.0.1:8084"

  def setUp(self):
    self.tensors = [
      tf.get_variable("tensor1", initializer=tf.constant(0.1, dtype=tf.float32)),
      tf.get_variable("tensor2", initializer=tf.constant(15, dtype=tf.int32)),
      tf.get_variable("tensor3", initializer=tf.constant("potato", dtype=tf.string))
    ]
    self.tensor_names = [tensor.name for tensor in self.tensors]
    self.invalid_tensor_name = "t1"
    self.session = tf.Session()
    self.session.run(tf.global_variables_initializer())
    self.httpd, self.thread = tfset.server.run_server(self.tensors, self.session)

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
    self.assertEqual(set(content["tensor_names"]), set(self.tensor_names))
    self.assertEqual(content["last_check_iteration"], 0)

  def test_add_events(self):

    events = [

    ]

    event_1 = {
      "iteration": 10,
      "tensor_name": self.tensor_names[0],
      "value": 0.001
    }
    event_2 = {
      "iteration": 100,
      "tensor_name": self.tensor_names[0],
      "value": 10
    }

    post_r = requests.post(self.address, data=event_1)
    self.assertEqual(post_r.status_code, 200)
    post_r = requests.post(self.address, data=event_2)
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
      "tensor_name": self.tensor_names[0],
      "value": 0.001
    }

    post_r = requests.post(self.address, data=event)
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
      "tensor_name": self.tensor_names[0],
      "value": 0.001
    }

    post_r = requests.post(self.address, data=event)
    self.assertEqual(post_r.status_code, 200)

    self.httpd.check_events(5)
    self.assertEqual(len(self.httpd.events), 1)
    self.assertEqual(len(self.httpd.past_events), 0)
    self.assertEqual(self.httpd.shared["last_check_iteration"], 5)

    self.httpd.check_events(15)
    self.assertEqual(len(self.httpd.events), 0)
    self.assertEqual(len(self.httpd.past_events), 1)
    self.assertAlmostEqual(self.session.run(self.tensors[0]), event["value"], places=3)
    self.assertEqual(self.httpd.shared["last_check_iteration"], 15)

  def test_trigger_events(self):

    event_1 = {
      "iteration": 10,
      "tensor_name": self.tensor_names[0],
      "value": 0.001
    }

    event_2 = {
      "iteration": 20,
      "tensor_name": self.tensor_names[0],
      "value": 0.0001
    }

    post_r = requests.post(self.address, data=event_1)
    self.assertEqual(post_r.status_code, 200)
    post_r = requests.post(self.address, data=event_2)
    self.assertEqual(post_r.status_code, 200)

    self.httpd.check_events(5)
    self.assertEqual(len(self.httpd.events), 2)
    self.assertEqual(len(self.httpd.past_events), 0)
    self.assertEqual(self.httpd.shared["last_check_iteration"], 5)

    self.httpd.check_events(15)
    self.assertEqual(len(self.httpd.events), 1)
    self.assertEqual(len(self.httpd.past_events), 1)
    self.assertAlmostEqual(self.session.run(self.tensors[0]), event_1["value"], places=3)
    self.assertEqual(self.httpd.shared["last_check_iteration"], 15)

    self.httpd.check_events(20)
    self.assertEqual(len(self.httpd.events), 0)
    self.assertEqual(len(self.httpd.past_events), 2)
    self.assertAlmostEqual(self.session.run(self.tensors[0]), event_2["value"], places=3)
    self.assertEqual(self.httpd.shared["last_check_iteration"], 20)

  def test_trigger_events_same_iter(self):

    event_1 = {
      "iteration": 10,
      "tensor_name": self.tensor_names[0],
      "value": 0.001
    }

    event_2 = {
      "iteration": 10,
      "tensor_name": self.tensor_names[0],
      "value": 0.0001
    }

    post_r = requests.post(self.address, data=event_1)
    self.assertEqual(post_r.status_code, 200)
    post_r = requests.post(self.address, data=event_2)
    self.assertEqual(post_r.status_code, 200)

    self.httpd.check_events(5)
    self.assertEqual(len(self.httpd.events), 2)
    self.assertEqual(len(self.httpd.past_events), 0)
    self.assertEqual(self.httpd.shared["last_check_iteration"], 5)

    self.httpd.check_events(10)
    self.assertEqual(len(self.httpd.events), 0)
    self.assertEqual(len(self.httpd.past_events), 2)

    val = self.session.run(self.tensors[0])
    self.assertTrue(abs(val - event_1["value"]) < 0.00001 or abs(val - event_2["value"]) < 0.00001)
    self.assertEqual(self.httpd.shared["last_check_iteration"], 10)

  def test_empty_post(self):

    post_r = requests.post(self.address)
    self.assertEqual(post_r.status_code, 400)

  def test_post_invalid_tensor_name(self):

    event = {
      "iteration": 10,
      "tensor_name": self.invalid_tensor_name,
      "value": 0.001
    }

    post_r = requests.post(self.address, data=event)
    self.assertEqual(post_r.status_code, 400)

  @staticmethod
  def __decode_json(content):
    return json.loads(content.decode())
