from soyboard import models

class TestPost:
    def test_make_tripcode(self):
        assert ('bleh', 'wMKmOyDpdxJxUrAurVgZ') == models.Post.make_tripcode('bleh#lol')
