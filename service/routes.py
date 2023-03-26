"""
My Service

Describe what your service does here
"""

from flask import jsonify, request, url_for, make_response, abort
from service.common import error_handlers, status  # HTTP Status Codes
from service.models import DataValidationError, Recommendation

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
# LIST ALL RECOMMENDATIONS
######################################################################
@app.route("/recommendations", methods=["GET"])
def list_recommendations():
    """Returns all of the Recommendations"""
    app.logger.info("Request for Recommendations list")

    recommendations = Recommendation.all()

    # Return as an array of dictionaries
    results = [recommendation.serialize() for recommendation in recommendations]

    return make_response(jsonify(results), status.HTTP_200_OK)


######################################################################
# RETRIEVE A RECOMMENDATION
######################################################################
@app.route("/recommendations/<int:recommendation_id>", methods=["GET"])
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
@app.route("/recommendations", methods=["POST"])
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
@app.route("/recommendations/<int:recommendation_id>", methods=["DELETE"])
def delelte(recommendation_id):
    """ Create a new recommendation """

    app.logger.info("Request to delete a Recommendation")

    # Delete the recommendation
    rec = Recommendation.find(recommendation_id)
    if rec:
        # rec.deserialize(request.get_json())
        rec.delete()

    return make_response("", status.HTTP_204_NO_CONTENT)


# UPDATE A RECOMMENDATION
######################################################################
@app.route("/recommendations/<int:recommendation_id>", methods=["PUT"])
def update(recommendation_id):
    """ Update a recommendation """
    app.logger.info("Request to update a Recommendation")
    check_content_type("application/json")

    rec = Recommendation.find(recommendation_id)
    if not rec:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Recommendation with id '{recommendation_id}' could not be found.",
        )

    request_body = request.json
    if 'recommended_pid' not in request_body and 'type' not in request_body:
        abort(
            status.HTTP_400_BAD_REQUEST,
            "Request Body invalid",
        )

    if not isinstance(request_body['recommended_pid'], int):
        abort(
            status.HTTP_400_BAD_REQUEST,
            "Recommended PID Invalid",
        )

    if not isinstance(request_body['type'], int):
        abort(
            status.HTTP_400_BAD_REQUEST,
            "Type Invalid",
        )

    if 'recommended_pid' in request_body:
        rec.recommended_pid = request_body['recommended_pid']

    if 'type' in request_body:
        rec.type = request_body['type']

    rec.update()
    # Create a message to return
    message = rec.serialize()
    return make_response(
        jsonify(message), status.HTTP_200_OK
    )


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
