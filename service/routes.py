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
def get_recommendation_based_on_filter(request):
    recommendations = []
    rec_type = request.args.get("type", default=None, type=str)
    liked = request.args.get("liked", default=None, type=str)
    if rec_type is not None:
        if rec_type in set(['cross-sell', 'up-sell', 'accessory', 'frequently_together']):
            recommendations = Recommendation.find_by_type(rec_type)
        else:
            abort(
                status.HTTP_400_BAD_REQUEST,
                f"Type '{rec_type}' is an invalid recommendation type.",
            )
    elif liked is not None:
        if liked in set(['true', 'false']):
            recommendations = Recommendation.find_by_liked(liked)
        else:
            abort(
                status.HTTP_400_BAD_REQUEST,
                f"liked = '{liked}' is an invalid liked type.",
            )
    else:
        recommendations = Recommendation.all()

    return recommendations


@app.route("/recommendations", methods=["GET"])
def list_recommendations():
    """Returns list of the Recommendations"""
    app.logger.info("Request for Recommendations list")

    recommendations = get_recommendation_based_on_filter(request)

    pid = None
    amount = None

    try:
        pid = int(request.args.get('pid'))
    except TypeError:  # pylint: disable=broad-except
        pass

    try:
        amount = int(request.args.get('amount'))
    except TypeError:  # pylint: disable=broad-except
        pass

    if pid is not None:
        results = []
        for recommendation in recommendations:
            if recommendation.pid == pid:
                results.append(recommendation.serialize())
    else:
        results = [recommendation.serialize() for recommendation in recommendations]

    if amount is not None:
        # Get top k recommendations (Sort first if adding priority)
        result = results[0:amount]
    else:
        result = results

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
