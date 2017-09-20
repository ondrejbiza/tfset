import unittest, server, requests, json

class TestServer(unittest.TestCase):

  def setUp(self):
    self.httpd, self.thread = server.run_server([], None)

  def tearDown(self):
    self.httpd.shutdown()
    self.thread.join()

  def test_start_and_stop_server(self):
    pass

  def test_get_events(self):
    r = requests.get("http://127.0.0.1:8000")
    content = json.loads(r.content.decode())

    self.assertEqual(r.status_code, 200)
    self.assertTrue(len(content["events"]) == 0)
    self.assertTrue(len(content["past_events"]) == 0)

  def test_add_event(self):
    pass

  def test_add_events(self):
    pass

  def test_remove_event(self):
    pass

  def test_remove_events(self):
    pass