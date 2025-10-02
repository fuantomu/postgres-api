import unittest
from fastapi.testclient import TestClient
from src.server import Server


def get_test_suite(client):
    suite = unittest.TestSuite()
    return suite


def init_server():
    server = Server(port=1441, database="cookbook_test")
    server.initialize_endpoints()
    server.initialize_logging()
    server.clean_database()
    server.initialize_database()
    return server


if __name__ == "__main__":
    server = init_server()
    client = TestClient(server.app)

    suite = get_test_suite(client)
    runner = unittest.TextTestRunner()
    runner.run(suite)
