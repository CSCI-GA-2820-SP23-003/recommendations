"""
My Service

Describe what your service does here
"""

from flask import Flask, jsonify, request, url_for, make_response, abort
from service.common import status  # HTTP Status Codes
from service.models import Recommendation

# Import Flask application
from . import app


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """ Root URL response """
    return (
        jsonify(
            name="Recommendation REST API Service",
            version="1.0",
            # paths=url_for("list_accounts", _external=True),
        ),
        status.HTTP_200_OK,
    )


######################################################################
# RETRIEVE A RECOMMENDATION
######################################################################
@app.route("/recommendation/<int:recommendation_id>", methods=["GET"])
def get_recommendation(recommendation_id):
    """
    Retrieve a single Recommendation
    This endpoint will return a Recommendation based on it's id
    """
    app.logger.info("Request for Recommendation with id: %s", recommendation_id)

    # See if the account exists and abort if it doesn't
    rec = Recommendation.find(recommendation_id)
    if not rec:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Recommendation with id '{recommendation_id}' could not be found.",
        )

    return make_response(jsonify(rec.serialize()), status.HTTP_200_OK)


######################################################################
# CREATE A NEW RECOMMENDATION
######################################################################
@app.route("/recommendation", methods=["POST"])
def create():
    """ Create a new recommendation """

    app.logger.info("Request to create a Recommendation")
    check_content_type("application/json")

    # Create the account
    rec = Recommendation()
    rec.deserialize(request.get_json())
    rec.create()

    # Create a message to return
    message = rec.serialize()
    location_url = url_for("get_recommendation", recommendation_id=rec.id, _external=True)
    
    return make_response(
        jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}
    )


######################################################################
# DELETE A RECOMMENDATION
######################################################################
@app.route("/recommendation/<int:recommendation_id>", methods=["DELETE"])
def delelte(recommendation_id):
    """ Create a new recommendation """

    app.logger.info("Request to delete a Recommendation")
    check_content_type("application/json")

    # Delete the recommendation
    rec = Recommendation.find(recommendation_id)
    if rec:
        rec.deserialize(request.get_json())
        rec.delete()
    
    return make_response( "", status.HTTP_204_NO_CONTENT)

######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


def check_content_type(media_type):
    """Checks that the media type is correct"""
    content_type = request.headers.get("Content-Type")
    if content_type and content_type == media_type:
        return
    app.logger.error("Invalid Content-Type: %s", content_type)
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {media_type}",
    )