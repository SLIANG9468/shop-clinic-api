from app import create_app
from app.models import Mechanics, db
from werkzeug.security import check_password_hash, generate_password_hash
from app.util.auth import encode_token
import unittest

#Run Script: python3 -m unittest discover tests

class TestMechanics(unittest.TestCase):

    #Runs before each test_method
    def setUp(self): 
        self.app = create_app('TestingConfig') #Create a testing version of my app for these testcases
        
        self.mechanic = Mechanics(first_name="Steve", last_name="Zhang", email="tester@email.com", password=generate_password_hash('123'), salary = 9999, address='123 Apple Ln') #Creating a starter mechanic, to test things like get, login, update, and delete

        with self.app.app_context(): 
            db.drop_all() #removing any lingering table
            db.create_all() #creating fresh for another round of testing
            db.session.add(self.mechanic)
            db.session.commit()

        self.token = encode_token(1, 'mechanic')
        self.client = self.app.test_client() #creates a test client that will send requests to our API

    
    #test creating a mechanic (IMPORTANT all test functions need to start with test)
    def test_create_mechanic(self):
        mechanic_payload = {
            "first_name": "first_name_test",
            "last_name": "last_name_test",
            "email": "mechanic_01@email.com",
            "password": "123",
            "salary": 1000,
            "address": "123 Fun St."
        }


        response = self.client.post('/mechanics/', json=mechanic_payload) #sending a test POST request using our test_client, and including the JSON body
        self.assertEqual(response.status_code, 201) #checking if I got a 201 status
        data = response.get_json() #Get the JSON response data
        self.assertEqual(data['last_name'], "last_name_test") #Checking to make sure the data that I sent in, is apart of the response. make sure the data that I sent in, is apart of the response.
        self.assertTrue(check_password_hash(data['password'], "123"))

    #Negative check: See what happens when we intentially try and break an endpoint
    def test_invalid_create(self):
        mechanic_payload = { #Missing email which should be required
            "first_name": "first_name_test",
            "last_name": "last_name_test",
            "password": "123",
            "salary": 1000,
            "address": "123 Fun St."
        }

  
        response = self.client.post('/mechanics/', json=mechanic_payload)
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn('email', data) #Membership check that email is in the response json

    def test_nonunique_email(self):
        mechanic_payload = { 
            "first_name": "first_name_test",
            "last_name": "last_name_test",
            "email": "tester@email.com",
            "password": "123",
            "salary": 1000,
            "address": "123 Fun St."
        }
        response = self.client.post('/mechanics/', json=mechanic_payload)
        self.assertEqual(response.status_code, 400)

    def test_get_mechanics(self):
    
        response = self.client.get('/mechanics/')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data[0]['first_name'], 'Steve')

    def test_login(self):
        login_creds = {
            "email": "tester@email.com",
            "password": "123"
        }

        response = self.client.post('/mechanics/login', json=login_creds)
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.json)

    def test_delete(self):
        headers = {"Authorization": "Bearer " + self.token}

        response = self.client.delete("/mechanics", headers=headers) #Sending delete request to /mechanics with my Authorization headers
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['message'], 'Successfully deleted mechanic 1')


    def test_unauthorized_delete(self):

        response = self.client.delete("/mechanics") #Sending delete request to /mechanics without token
        self.assertEqual(response.status_code, 401) #Should get an error response

    
    def test_update(self):
        headers = {"Authorization": "Bearer " + self.token}

        update_payload = {
            "first_name": "first_name_test",
            "last_name": "last_name_test",
            "email": "newtester@email.com",
            "password": "123",
            "salary": 1000,
            "address": "123 Fun St."
        }

        response = self.client.put('/mechanics', headers=headers, json=update_payload)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['email'], 'newtester@email.com')
