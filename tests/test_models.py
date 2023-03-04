"""
Test cases for Recommendation Model

"""
import os
import logging
import unittest
from service import app
from service.models import Recommendation, DataValidationError, db

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)

######################################################################
#  Recommendation   M O D E L   T E S T   C A S E S
######################################################################
class TestRecommendation(unittest.TestCase):
    """ Test Cases for Recommendation Model """

    @classmethod
    def setUpClass(cls):
        """ This runs once before the entire test suite """
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Recommendation.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """ This runs once after the entire test suite """

    def setUp(self):
        """ This runs before each test """
        db.session.query(Recommendation).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """ This runs after each test """
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_recommendation(self):
        """ It should Create a Recommendation and assert that it exists """
        # pylint: disable=unexpected-keyword-arg
        rec = Recommendation(
            pid=100,
            recommended_pid=200,
            type=0,
        )
        self.assertIsNotNone(rec)
        self.assertEqual(rec.id, None)
        self.assertEqual(rec.pid, 100)
        self.assertEqual(rec.recommended_pid, 200)

    def test_add_a_recommendation(self):
        """It should Create a Recommendation and add it to the database"""
        recs = Recommendation.all()
        self.assertEqual(recs, [])
        rec = Recommendation()
        rec.pid = 10
        rec.recommended_pid = 20
        rec.type = 0
        rec.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(rec.id)
        recs = Recommendation.all()
        self.assertEqual(len(recs), 1)

    def test_read_recommendation(self):
        """It should Read a recommendation"""
        PID_1 = 100
        PID_2 = 200

        rec = Recommendation()
        rec.pid = PID_1
        rec.recommended_pid = PID_2
        rec.create()

        # Read it back
        found_rec = Recommendation.find(rec.id)
        self.assertEqual(found_rec.id, rec.id)
        self.assertEqual(found_rec.pid, rec.pid)
        self.assertEqual(found_rec.recommended_pid, rec.recommended_pid)

    def test_filter_recommendation(self):
        """It should Read a filtered list of recommendation"""
        PID_1 = 100
        PID_2 = 200
        PID_3 = 300

        rec = Recommendation()
        rec.pid = PID_1
        rec.recommended_pid = PID_2
        rec.create()

        # Read it back
        found_rec = Recommendation.find(rec.id)
        self.assertEqual(found_rec.id, rec.id)
        self.assertEqual(found_rec.pid, rec.pid)
        self.assertEqual(found_rec.recommended_pid, rec.recommended_pid)

        rec2 = Recommendation()
        rec2.pid = PID_1
        rec2.recommended_pid = PID_3
        rec2.create()

        rec3 = Recommendation()
        rec3.pid = PID_3
        rec3.recommended_pid = PID_2
        rec3.create()

        found_rec = Recommendation.find_by_pid(PID_1).all()
        self.assertEqual(len(found_rec), 2)