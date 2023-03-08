"""
TestYourResourceModel API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import os
import logging
from unittest import TestCase
from unittest.mock import MagicMock, patch
from service import app
from service.models import db, Recommendation, init_db
from service.common import status  # HTTP Status Codes
from .utils import make_recommendation


DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)

BASE_URL = "/recommendation"


######################################################################
#  T E S T   C A S E S
######################################################################
class TestYourResourceServer(TestCase):
    """ REST API Server Tests """

    @classmethod
    def setUpClass(cls):
        """ This runs once before the entire test suite """
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        init_db(app)

    @classmethod
    def tearDownClass(cls):
        """ This runs once after the entire test suite """

    def setUp(self):
        """ This runs before each test """
        db.session.query(Recommendation).delete()  # clean up the last tests
        db.session.commit()

        self.client = app.test_client()

    def tearDown(self):
        """ This runs after each test """
        db.session.remove()

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """ It should call the home page """
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_create(self):
        """It should Create a new Recommendation"""
        rec = make_recommendation(100, 200)
        resp = self.client.post(
            BASE_URL, json=rec.serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = resp.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_rec = resp.get_json()
        self.assertEqual(new_rec["pid"], rec.pid, "pid does not match")
        self.assertEqual(new_rec["recommended_pid"], rec.recommended_pid, "recommended_pid does not match")
        self.assertEqual(new_rec["type"], rec.type, "type does not match")

        # Check that the location header was correct by getting it
        resp = self.client.get(location, content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_rec = resp.get_json()
        self.assertEqual(new_rec["pid"], rec.pid, "pid does not match")
        self.assertEqual(new_rec["recommended_pid"], rec.recommended_pid, "recommended_pid does not match")
        self.assertEqual(new_rec["type"], rec.type, "type does not match")

    def test_get(self):
        """It should Get a Recommendation that is found"""
        # Create a test case Recommendation
        rec = make_recommendation(100, 200)
        resp = self.client.post(
            BASE_URL, json=rec.serialize(), content_type="application/json"
        )

        # Check GET status is 200_OK
        location = resp.headers.get("Location", None)
        resp = self.client.get(location, content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        # Check GET data is correct
        data = resp.get_json()
        self.assertEqual(data["pid"], rec.pid)

    def test_get_not_found(self):
        """It should not Read a Recommendation that is not found"""
        # Get a Recommendation that does not exist
        resp = self.client.get(f"{BASE_URL}/0")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_update(self):
        """It should update the given recommendation"""
        pid = 100
        rec = make_recommendation(pid,200,0)
        resp = self.client.post(
            BASE_URL, json=rec.serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        body = {"pid":pid ,"recommended_pid":300, "type": 0}
        resp = self.client.put(
            BASE_URL+"/"+str(pid), json=body.serialize(),
             content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_rec = resp.get_json()
        self.assertEqual(updated_rec["pid"], body["pid"], "pid does not match")
        self.assertEqual(updated_rec["recommended_pid"], body["recommended_pid"], 
        "recommended_pid does not match")
        self.assertEqual(updated_rec["type"], body["type"], "type does not match")

        # """It should update the given recommendation: Update type"""
        pid = 400
        rec = make_recommendation(pid,200,0)
        resp = self.client.post(
            BASE_URL, json=rec.serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        body = {"pid":pid ,"recommended_pid":500, "type": 1}
        resp = self.client.put(
            BASE_URL+"/"+str(pid), json=body.serialize(),
             content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_rec = resp.get_json()
        self.assertEqual(updated_rec["pid"], body["pid"], "pid does not match")
        self.assertEqual(updated_rec["recommended_pid"], body["recommended_pid"], "recommended_pid does not match")
        self.assertEqual(updated_rec["type"], body["type"], "type does not match")

        # Make sure location header is set
        location = resp.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Test invalid recommended_pid
        pid = 500
        rec = make_recommendation(pid,200,0)
        resp = self.client.post(
            BASE_URL, json=rec.serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        body = {"pid":pid ,"recommended_pid":"600", "type": 1}
        resp = self.client.put(
            BASE_URL+"/"+str(pid), json=body.serialize(),
             content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

        # Test invalid type
        pid = 500
        rec = make_recommendation(pid,300,1)
        resp = self.client.post(
            BASE_URL, json=rec.serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        body = {"pid":pid ,"recommended_pid":600, "type": "2"}
        resp = self.client.put(
            BASE_URL+"/"+str(pid), json=body.serialize(),
             content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

        # Test no input
        pid = 500
        rec = make_recommendation(pid,300,1)
        resp = self.client.post(
            BASE_URL, json=rec.serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        body = {"pid":pid}
        resp = self.client.put(
            BASE_URL+"/"+str(pid), json=body.serialize(),
             content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
