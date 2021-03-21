import json

from Authentication.cipher import AESInstance, SHA512
from django.test import Client, TestCase
from .models import User


class EventTestCase(TestCase):
    def __init__(self, methodName: str = ...):
        super().__init__(methodName)
        self.c = None

    def setUp(self):
        User.objects.create(username='1', email=AESInstance.encrypt('1@1.1'), password=SHA512('111111'), uuid='32f1506a-e3d7-4d0b-bc03-952e78f35855')
        self.c = Client()

    def test_register(self):
        user = {
            'username': '2',
            'email': '2@2.2',
            'password': '222222'
        }

        response = self.c.post('/api/auth/register', json.dumps(user), content_type='json')
        self.assertEqual(response.status_code, 201)

    def test_getByExistingName(self):
        response = self.c.get('/api/auth/user/1')
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['exists'])

    def test_getByExistingEmail(self):
        response = self.c.get('/api/auth/user/1@1.1')
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['exists'])

    def test_getByWrongName(self):
        response = self.c.get('/api/auth/user/3')
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(data['exists'])

    def test_getByWrongEmail(self):
        response = self.c.get('/api/auth/user/3@3.3')
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(data['exists'])

    def test_loginExistingUser(self):
        user = {
            'username': '1',
            'email': '',
            'password': '111111'
        }
        response = self.c.post('/api/auth/login', json.dumps(user), content_type='json')
        data = json.loads(response.content.decode('utf-8'))
        self.assertTrue(data['success'])

    def test_loginExistingEmail(self):
        user = {
            'username': '',
            'email': '1@1.1',
            'password': '111111'
        }
        response = self.c.post('/api/auth/login', json.dumps(user), content_type='json')
        data = json.loads(response.content.decode('utf-8'))
        self.assertTrue(data['success'])

    def test_loginWrongUser(self):
        user = {
            'username': '3',
            'email': '',
            'password': '333333'
        }
        response = self.c.post('/api/auth/login', json.dumps(user), content_type='json')
        data = json.loads(response.content.decode('utf-8'))
        self.assertFalse(data['success'])

    def test_loginWrongEmail(self):
        user = {
            'username': '',
            'email': '3@3.3',
            'password': '333333'
        }
        response = self.c.post('/api/auth/login', json.dumps(user), content_type='json')
        data = json.loads(response.content.decode('utf-8'))
        self.assertFalse(data['success'])

    def test_getByExistingUUID(self):
        response = self.c.get('/api/auth/user/32f1506a-e3d7-4d0b-bc03-952e78f35855')
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['exists'])
