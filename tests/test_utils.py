from gonka_wallet.utils import gonka_to_ngonka, ngonka_to_gonka


class TestGonkaToNgonka:
    def test_one(self):
        assert gonka_to_ngonka(1) == 1_000_000_000

    def test_half(self):
        assert gonka_to_ngonka(0.5) == 500_000_000

    def test_zero(self):
        assert gonka_to_ngonka(0) == 0


class TestNgonkaToGonka:
    def test_one_billion(self):
        assert ngonka_to_gonka(1_000_000_000) == 1.0

    def test_zero(self):
        assert ngonka_to_gonka(0) == 0.0
