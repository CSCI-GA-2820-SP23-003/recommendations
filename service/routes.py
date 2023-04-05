"""
My Service

Describe what your service does here
"""

from flask import jsonify, request, url_for, make_response, abort
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
# HEALTH CHECK
######################################################################
@app.route("/health")
def health():
    """ For health check """
    return (
        {"status": "OK"},
        status.HTTP_200_OK,
    )


######################################################################
# LIST ALL RECOMMENDATIONS
######################################################################
@app.route("/recommendations", methods=["GET"])
def list_recommendations():  # noqa: C901
    """Returns list of the Recommendations"""
    app.logger.info("Request for Recommendations list")

    recommendations = Recommendation.all()
    pid = None
    amount = None
    rec_type = None

    try:
        pid = int(request.args.get('pid'))
    except TypeError:  # pylint: disable=broad-except
        pass

    try:
        amount = int(request.args.get('amount'))
    except TypeError:  # pylint: disable=broad-except
        pass

    try:
        rec_type = str(request.args.get('type'))
    except TypeError:  # pylint: disable=broad-except
        pass

    results = [recommendation.serialize() for recommendation in recommendations]
    if pid is not None:
        results = []
        for recommendation in recommendations:
            if recommendation.pid == pid:
                results.append(recommendation.serialize())

    result = results
    if rec_type != "default":
        if rec_type != "cross-sell" or rec_type != "up-sell" or \
                rec_type != "accessory" or rec_type != "frequently_together":
            abort(
                status.HTTP_400_BAD_REQUEST,
                f"Recommendation with incorrect type '{rec_type}' is invalid.",
            )
        else:
            result = []
            for recommendation in results:
                if recommendation.type == rec_type:
                    result.append(recommendation.serialize())

    if amount is not None:
        # Get top k recommendations (Sort first if adding priority)
        result = result[0:amount]
    # else:
    #     result = result

    return make_response(jsonify(result), status.HTTP_200_OK)


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
        rec.delete()

    return make_response("", status.HTTP_204_NO_CONTENT)


######################################################################
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

    rec.deserialize(request.get_json())
    rec.id = recommendation_id
    rec.update()

    # Create a message to return
    message = rec.serialize()
    return make_response(
        jsonify(message), status.HTTP_200_OK
    )


######################################################################
# (ACTION) LIKE A RECOMMENDATION
######################################################################
@app.route("/recommendations/<int:recommendation_id>/like", methods=["PUT"])
def like(recommendation_id):
    """ Like a recommendation """
    app.logger.info("Request to like a Recommendation")

    rec = Recommendation.find(recommendation_id)
    if not rec:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Recommendation with id '{recommendation_id}' could not be found.",
        )

    rec.liked = True
    rec.update()

    # Create a message to return
    message = rec.serialize()
    return make_response(
        jsonify(message), status.HTTP_200_OK
    )


######################################################################
# (ACTION) UNLIKE A RECOMMENDATION
######################################################################
@app.route("/recommendations/<int:recommendation_id>/unlike", methods=["PUT"])
def unlike(recommendation_id):
    """ Unlike a recommendation """
    app.logger.info("Request to unlike a Recommendation")

    rec = Recommendation.find(recommendation_id)
    if not rec:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Recommendation with id '{recommendation_id}' could not be found.",
        )

    rec.liked = False
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
