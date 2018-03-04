from unittest import TestCase
import mutalk
import threading
import time


class TestIntegration(TestCase):

    def reader_thread(self, reader, result):
        try:
            packet = reader.read()
            self.assertEqual(packet.channel, 123456)
            self.assertEqual(packet.payload, b"hell in world")
        except Exception as e:
            result[0] = e

    def test_all(self):
        with mutalk.Reader(timeout=5) as reader, mutalk.Writer() as writer:
            reader.subscribe(1, 2, 123456)

            thread_result = [None]

            t = threading.Thread(target=self.reader_thread, args=(reader, thread_result))
            t.start()

            time.sleep(1)

            writer.write(123456 + 16777215, "double hell in world")
            writer.write(123456, "hell in world")

            t.join()
            if thread_result[0] is not None:
                self.fail(thread_result[0])

            reader.unsubscribe(1, 2, 123456)
