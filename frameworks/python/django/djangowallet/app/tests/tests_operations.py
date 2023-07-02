from app.tests.helpers import UnitTestCase

# from app import operations

# TODO: implement tests


class CreateUserTest(UnitTestCase):
    def test_positive(self):
        pass

    def test_bad_currency(self):
        pass

    def test_bad_params(self):
        pass

    def test_not_enough_params(self):
        pass

    def test_create_existing(self):
        pass


class GetWalletTest(UnitTestCase):
    def test_positive(self):
        pass

    def test_get_not_existing(self):
        pass

    def test_get_bad_param(self):
        pass


class CreateTransferOperationTest(UnitTestCase):
    def test_positive(self):
        pass

    def test_bad_wallet(self):
        pass

    def test_zero_amount(self):
        pass

    def test_negative_amount(self):
        pass

    def test_bad_currency(self):
        pass

    def test_transfer_to_self(self):
        pass


class CreatePutOperationTest(UnitTestCase):
    def test_positive(self):
        pass

    def test_bad_wallet(self):
        pass

    def test_zero_amount(self):
        pass

    def test_negative_amount(self):
        pass

    def test_bad_currency(self):
        pass

    def test_with_user_from(self):
        pass
