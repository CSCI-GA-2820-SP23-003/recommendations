"""
TestRecommendationRoutes API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import os
import logging
from unittest import TestCase
# from unittest.mock import MagicMock, patch
from service import app
from service.models import db, Recommendation, RecommendationType, init_db
from service.common import status  # HTTP Status Codes
from tests.utils import make_recommendation


DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)

BASE_URL = "/recommendations"


######################################################################
#  T E S T    C A S E S
######################################################################
# pylint: disable=R0904
class TestRecommendationRoutes(TestCase):
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
        db.session.close_all()

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """ It should call the home page """
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_health_check(self):
        """ It should get the status ok """
        resp = self.client.get("/health")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        resp_body = resp.get_json()
        self.assertEqual(resp_body["status"], "OK")

    def test_get_recommendation_list(self):
        """It should get a list of Recommendations"""
        for i in range(5):
            for j in range(3):
                rec = make_recommendation(i, j)
                resp = self.client.post(
                    BASE_URL, json=rec.serialize(), content_type="application/json"
                )

        resp = self.client.get(BASE_URL)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 15)

    def test_get_specific_type_recommendation_list(self):
        """It should get a list of Recommendations of specific type"""
        for i in range(5):
            for j in range(3):
                if i == 4:
                    rec = make_recommendation(i, j, rec_type="cross-sell")
                else:
                    rec = make_recommendation(i, j)
                resp = self.client.post(
                    BASE_URL, json=rec.serialize(), content_type="application/json"
                )

        resp = self.client.get(BASE_URL+"?type=cross-sell")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 3)

    def test_get_specific_type_recommendation_list_wrong_param(self):
        """It should get a list of Recommendations of specific type"""
        for i in range(5):
            for j in range(3):
                if i == 4:
                    rec = make_recommendation(i, j, rec_type="cross-sell")
                else:
                    rec = make_recommendation(i, j)
                resp = self.client.post(
                    BASE_URL, json=rec.serialize(), content_type="application/json"
                )

        resp = self.client.get(BASE_URL+"?type=mixed_recommendations")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_liked_recommendation_list(self):
        """It should get a list of Recommendations based on the liked type"""
        for i in range(5):
            for j in range(3):
                if i == 4:
                    rec = make_recommendation(i, j, liked=True)
                else:
                    rec = make_recommendation(i, j)
                resp = self.client.post(
                    BASE_URL, json=rec.serialize(), content_type="application/json"
                )

        resp = self.client.get(BASE_URL+"?liked=true")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 3)

    def test_get_liked_recommendation_list_wrong_param(self):
        """It should get a list of Recommendations based on the liked type"""
        for i in range(5):
            for j in range(3):
                if i == 4:
                    rec = make_recommendation(i, j, liked=True)
                else:
                    rec = make_recommendation(i, j)
                resp = self.client.post(
                    BASE_URL, json=rec.serialize(), content_type="application/json"
                )

        resp = self.client.get(BASE_URL+"?liked=trueee")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

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

    def test_create_invalid(self):
        """It should be failed to Create a Recommendation"""
        rec = make_recommendation(100, 200)
        request_body = rec.serialize()
        del request_body["recommended_pid"]
        resp = self.client.post(
            BASE_URL, json=request_body, content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

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

    def test_update_rec_pid(self):
        """It should update the recommended product"""
        pid = 100
        rec = make_recommendation(pid, 200)
        resp = self.client.post(
            BASE_URL, json=rec.serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        created_rec = resp.get_json()

        body = {"pid": pid, "recommended_pid": 300, "type": RecommendationType.CROSS_SELL}
        resp = self.client.put(
            BASE_URL+"/"+str(created_rec["id"]), json=body,
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_rec = resp.get_json()
        self.assertEqual(updated_rec["pid"], body["pid"], "pid does not match")
        self.assertEqual(updated_rec["recommended_pid"], body["recommended_pid"], "recommended_pid does not match")
        self.assertEqual(updated_rec["type"], body["type"], "type does not match")

        resp = self.client.put(BASE_URL+"/9999", json=body, content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_badrequest(self):
        """It should give a bad request error when input doesn't contain required fields for update"""
        pid = 100
        rec = make_recommendation(pid, 200)
        resp = self.client.post(
            BASE_URL, json=rec.serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        created_rec = resp.get_json()
        body = {"pid": pid}
        resp = self.client.put(
            BASE_URL+"/"+str(created_rec["id"]), json=body,
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_type(self):
        """It should update the given recommendation type"""
        pid = 400
        rec = make_recommendation(pid, 200)
        resp = self.client.post(
            BASE_URL, json=rec.serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        created_rec = resp.get_json()

        body = {"pid": pid, "recommended_pid": 500, "type": RecommendationType.CROSS_SELL}
        resp = self.client.put(
            BASE_URL+"/"+str(created_rec["id"]), json=body,
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_rec = resp.get_json()
        self.assertEqual(updated_rec["pid"], body["pid"], "pid does not match")
        self.assertEqual(updated_rec["recommended_pid"], body["recommended_pid"], "recommended_pid does not match")
        self.assertEqual(updated_rec["type"], body["type"], "type does not match")

    def test_bad_request(self):
        """It should not Create when sending the wrong data"""
        resp = self.client.post(BASE_URL, json={"name": "not enough data"})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_method_not_allowed(self):
        """It should not allow an illegal method call"""
        resp = self.client.put(BASE_URL, json={"not": "today"})
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete(self):
        """It should Delete a Recommendation if exists"""
        # Create a new Recommendation
        pid = 100
        rec = make_recommendation(pid, 200, RecommendationType.DEFAULT)
        resp = self.client.post(
            BASE_URL, json=rec.serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        created_rec = resp.get_json()

        # Deleting again should have no effect
        resp = self.client.post(
            BASE_URL, json=rec.serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Check that the location header was correct by deleting it
        resp = self.client.delete(f"{BASE_URL}/{created_rec['id']}")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

        # Check GET status is 404_NOT_FOUND
        resp = self.client.get(f"{BASE_URL}/{created_rec['id']}")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_like(self):
        """It should like the given recommendation"""
        pid = 100
        rec = make_recommendation(pid, 200, RecommendationType.DEFAULT)
        resp = self.client.post(
            BASE_URL, json=rec.serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        created_rec = resp.get_json()

        resp = self.client.put(BASE_URL+"/"+str(created_rec["id"])+"/like")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_rec = resp.get_json()
        self.assertEqual(updated_rec["liked"], True, "pid does not match")

    def test_unlike(self):
        """It should unlike the given recommendation"""
        pid = 100
        rec = make_recommendation(pid, 200, RecommendationType.DEFAULT, True)
        resp = self.client.post(
            BASE_URL, json=rec.serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        created_rec = resp.get_json()

        resp = self.client.put(BASE_URL+"/"+str(created_rec["id"])+"/unlike")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_rec = resp.get_json()
        self.assertEqual(updated_rec["liked"], False, "pid does not match")

    def test_like_unlike_not_found_recommendation(self):
        """It should failed to like/unlike a non-exist recommendation"""
        pid = 100
        resp = self.client.put(BASE_URL+"/"+str(pid)+"/like")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

        resp = self.client.put(BASE_URL+"/"+str(pid)+"/unlike")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_k_recommendation(self):
        """It should GET k Recommendations"""
        i = 100
        for j in range(5):
            rec = make_recommendation(i, j)
            resp = self.client.post(
                BASE_URL, json=rec.serialize(), content_type="application/json"
            )
        # pid and amount
        resp = self.client.get(BASE_URL+"?pid=100&amount=3")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 3)

        # Only pid
        resp = self.client.get(BASE_URL+"?pid=100")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 5)

        # Only amount
        resp = self.client.get(BASE_URL+"?amount=1")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 1)

        # Invalid amount
        resp = self.client.get(BASE_URL+"?amount=-1")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
