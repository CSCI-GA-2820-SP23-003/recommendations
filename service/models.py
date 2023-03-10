"""
Models for Recommendation

All of the models are stored in this module
"""
import logging
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


# Function to initialize the database
def init_db(app):
    """ Initializes the SQLAlchemy app """
    Recommendation.init_db(app)


class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """


class Recommendation(db.Model):
    """
    Class that represents a Recommendation
    """

    app = None

    # Table Schema
    id = db.Column(db.Integer, primary_key=True)
    pid = db.Column(db.Integer)
    recommended_pid = db.Column(db.Integer)
    type = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f"<Recommendation id=[{self.id}] ({self.pid} - {self.recommended_pid})>"

    def create(self):
        """
        Creates a Recommendation to the database
        """
        logger.info("Creating recommendation %s (%s - %s)", self.id, self.pid, self.recommended_pid)
        self.id = None  # pylint: disable=invalid-name
        db.session.add(self)
        db.session.commit()

    def update(self):
        """
        Updates a Recommendation to the database
        """
        logger.info("Updating recommendation %s (%s - %s)", self.id, self.pid, self.recommended_pid)
        db.session.commit()

    def delete(self):
        """ Removes a Recommendation from the data store """
        logger.info("Deleting recommendation %s (%s - %s)", self.id, self.pid, self.recommended_pid)
        db.session.delete(self)
        db.session.commit()

    def serialize(self):
        """ Serializes a Recommendation into a dictionary """
        return {
            "id": self.id,
            "pid": self.pid,
            "recommended_pid": self.recommended_pid,
            "type": self.type,
        }

    def deserialize(self, data):
        """
        Deserializes a Recommendation from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.pid = data["pid"]
            self.recommended_pid = data["recommended_pid"]
            self.type = data["type"]
        except KeyError as error:
            raise DataValidationError(
                "Invalid Recommendation: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Recommendation: body of request contained bad or no data - "
                "Error message: " + str(error)
            ) from error
        return self

    @classmethod
    def init_db(cls, app):
        """ Initializes the database session """
        logger.info("Initializing database")
        cls.app = app
        # This is where we initialize SQLAlchemy from the Flask app
        db.init_app(app)
        app.app_context().push()
        db.create_all()  # make our sqlalchemy tables

    @classmethod
    def all(cls):
        """ Returns all of the Recommendation in the database """
        logger.info("Processing all Recommendation")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """ Finds a Recommendation by it's ID """
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.get(by_id)

    @classmethod
    def find_by_pid(cls, pid):
        """Returns all Recommendation with the given pid

        Args:
            pid (int): the pid of the Recommendation you want to match
        """
        logger.info("Processing pid query for %s ...", pid)
        return cls.query.filter(cls.pid == pid)
