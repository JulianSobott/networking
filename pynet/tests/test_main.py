
from unittest import TestCase


class TestMain(TestCase):

    def test_imports(self):
        import pynet

    def test_final_procedure(self):
        """"
        # Client:
        def test():
            name = "John"
            password = "12345"
            successful = server.login(name, password)


         # Server
         def login(name, password)
            if name and password:
                return True
            else:
                return False
        """