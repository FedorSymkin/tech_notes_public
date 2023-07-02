from app.tests.helpers import IntegrationTestCase

# There are only some test cases here to test just fundamentals of whole server
# More detailed tests located in other files (unit tests)

# TODO: implement tests


class TestUsers(IntegrationTestCase):
    def test_create_user(self):
        pass

    def test_get_user_by_id(self):
        pass

    def test_get_user_by_name(self):
        pass

    def test_get_user_operations_by_name(self):
        pass


class TestWallets(IntegrationTestCase):
    def test_get_wallet(self):
        pass

    def test_put_money(self):
        pass

    def test_transfer_operation(self):
        pass

    def test_get_wallet_operations(self):
        pass

    def test_get_all_wallets(self):
        pass


class TestOperations(IntegrationTestCase):
    def test_get_operation(self):
        pass

    def test_set_operation_status(self):
        pass
