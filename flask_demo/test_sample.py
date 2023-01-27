import logging

log = logging.getLogger(__name__)


def a():
    log.info("a log message")


class TestSample:
    def test_a(self):
        a()
        assert False
