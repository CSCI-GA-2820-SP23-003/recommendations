"""
Test cases for Recommendation Model

"""
import os
import logging
import unittest
from service import app
from service.models import Recommendation, DataValidationError, db
from .utils import make_recommendation

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
        db.session.query(Recommendation).delete()

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
        rec = make_recommendation(10, 20)
        rec.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(rec.id)
        recs = Recommendation.all()
        self.assertEqual(len(recs), 1)

    def test_read_recommendation(self):
        """It should Read a recommendation"""
        PID_1 = 100
        PID_2 = 200

        rec = make_recommendation(PID_1, PID_2)
        rec.create()

        # Read it back
        found_rec = Recommendation.find(rec.id)
        self.assertEqual(found_rec.id, rec.id)
        self.assertEqual(found_rec.pid, rec.pid)
        self.assertEqual(found_rec.recommended_pid, rec.recommended_pid)

    def test_read_recommendation_by_pid(self):
        """It should Read a filtered list of recommendation by pid"""
        PID_1 = 100
        PID_2 = 200
        PID_3 = 300

        rec = make_recommendation(PID_1, PID_2)
        rec.create()

        # Read it back
        found_rec = Recommendation.find(rec.id)
        self.assertEqual(found_rec.id, rec.id)
        self.assertEqual(found_rec.pid, rec.pid)
        self.assertEqual(found_rec.recommended_pid, rec.recommended_pid)

        rec2 = make_recommendation(PID_1, PID_3)
        rec2.create()

        rec3 = make_recommendation(PID_3, PID_2)
        rec3.create()

        # rec1 should has only 2 recommended products
        # find recommendation by pid (PID_1)
        found_rec = Recommendation.find_by_pid(PID_1).all()
        self.assertEqual(len(found_rec), 2)

    def test_list_all_recommendations(self):
        """It should List all/filtered Recommendations in the database"""
        all_rec = Recommendation.all()
        self.assertEqual(all_rec, [])

        for i in range(5):
            for j in range(3):
                make_recommendation(i, j).create()

        # Assert that there are 5*3=15 recommendations in the database
        all_rec = Recommendation.all()
        self.assertEqual(len(all_rec), 15)

        # each pid has 3 recommended pids
        for i in range(5):
            found_rec = Recommendation.find_by_pid(i).all()
            self.assertEqual(len(found_rec), 3)

    def test_update_recommendation(self):
        """It should Update a recommendation"""
        PID_1 = 100
        PID_2 = 200
        PID_3 = 350

        rec = make_recommendation(PID_1, PID_2)
        rec.create()

        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(rec.id)
        self.assertEqual(rec.recommended_pid, PID_2)

        # Fetch it back
        found_rec = Recommendation.find(rec.id)
        found_rec.recommended_pid = PID_3
        found_rec.update()

        # Fetch it back again
        found_rec_2 = Recommendation.find(rec.id)
        self.assertEqual(found_rec_2.recommended_pid, PID_3)

        found_rec_2.delete()
    
    def test_delete_a_recommendation(self):
        """It should Delete a recommendation from the database"""
        PID_1 = 100
        PID_2 = 200

        all_rec = Recommendation.all()
        self.assertEqual(all_rec, [])

        rec = make_recommendation(PID_1, PID_2)
        rec.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(rec.id)

        all_rec = Recommendation.all()
        self.assertEqual(len(all_rec), 1)

        # Delete the only one record, and fetching again should return empty
        rec = all_rec[0]
        rec.delete()
        all_rec = Recommendation.all()
        self.assertEqual(len(all_rec), 0)

    def test_serialize_a_recommendation(self):
        """It should Serialize a Recommendation"""
        PID_1 = 100
        PID_2 = 200
        rec = make_recommendation(PID_1, PID_2)
        serial_rec = rec.serialize()
        self.assertEqual(serial_rec["id"], rec.id)
        self.assertEqual(serial_rec["pid"], rec.pid)
        self.assertEqual(serial_rec["recommended_pid"], rec.recommended_pid)
        self.assertEqual(serial_rec["type"], rec.type)

    def test_deserialize_a_recommendation(self):
        """It should Deserialize a recommendation"""
        PID_1 = 100
        PID_2 = 200
        rec = make_recommendation(PID_1, PID_2)
        rec.create()
        serial_rec = rec.serialize()
        new_rec = Recommendation()
        new_rec.deserialize(serial_rec)
        self.assertEqual(new_rec.pid, rec.pid)
        self.assertEqual(new_rec.recommended_pid, rec.recommended_pid)
        self.assertEqual(new_rec.type, rec.type)

    def test_deserialize_with_key_error(self):
        """It should not Deserialize a recommendation with a KeyError"""
        rec = Recommendation()
        self.assertRaises(DataValidationError, rec.deserialize, {})

    def test_deserialize_with_type_error(self):
        """It should not Deserialize a recommendation with a TypeError"""
        rec = Recommendation()
        self.assertRaises(DataValidationError, rec.deserialize, [])