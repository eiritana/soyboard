from soyboard import models

class TestPost:
    def test_make_tripcode(self):
        assert ('bleh', 'ZoGgoBAnxOWv8QiHwA9A') == models.Post.make_tripcode('bleh#lol')

    def test_format_message(self):
        pass
