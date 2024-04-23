import unittest
from app import app
from unittest.mock import patch, MagicMock
import json
from bson import ObjectId

class TestTaskManager(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

        self.collection_mock = MagicMock()
        self.patcher = patch('app.collection', self.collection_mock)
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    def test_create_task(self):
        data = {'title': 'Test Task', 'description': 'This is a test task'}
        response = self.app.post('/api/tasks', json=data)
        self.assertEqual(response.status_code, 201)
        self.assertIn(b'Task created successfully', response.data)

    def test_get_all_tasks(self):
        self.collection_mock.find.return_value = []
        response = self.app.get('/api/tasks')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data)['tasks'], [])

    def test_update_task(self):
        with patch('app.ObjectId', return_value='mocked_id'):
            response = self.app.put('/api/tasks/mock_id', json={'title': 'Updated Task', 'description': 'This is an updated task'})
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Task updated successfully', response.data)

    def test_delete_task(self):
        with patch('app.ObjectId', return_value=ObjectId()):
            response = self.app.delete('/api/tasks/mock_id')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Task deleted successfully', response.data)

if __name__ == '__main__':
    unittest.main()
