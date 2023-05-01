"""
My Service

Describe what your service does here
"""

from flask import abort
from flask_restx import Resource, fields, inputs, reqparse
from service.common import status  # HTTP Status Codes
from service.models import DataValidationError, Recommendation, RecommendationType

# Import Flask application
from . import app, init_api


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Base URL for our service"""
    return app.send_static_file("index.html")


# Note: Delay flask_restx initialization to prevent
#       conflicting with original Flask handler for '/'
api = init_api()


@api.errorhandler(DataValidationError)
def request_validation_error(error):
    """Handles Value Errors from bad data"""
    message = str(error)
    app.logger.error(message)
    return {
        'status_code': status.HTTP_400_BAD_REQUEST,
        'error': 'Bad Request',
        'message': message
    }, status.HTTP_400_BAD_REQUEST


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


# Define the model so that the docs reflect what can be sent
create_model = api.model('Recommendation', {
    'pid': fields.Integer(required=True, description='Product ID'),
    'recommended_pid': fields.Integer(required=True, description='Recommended product ID'),
    'type': fields.String(enum=[member.value for member in RecommendationType], description='Recommendation type'),
    'liked': fields.Boolean(description='Is the Recommendation liked?'),
})

recommendation_model = api.inherit(
    'RecommendationModel',
    create_model,
    {
        'id': fields.Integer(readOnly=True,
                             description='The unique id assigned internally by service'),
    }
)

# query string arguments
rec_args = reqparse.RequestParser()
rec_args.add_argument('pid', type=int, location='args', required=False, help='List Recommendations by product ID')
rec_args.add_argument('type', type=str, location='args', required=False, help='List Recommendations by type')
rec_args.add_argument('liked', type=inputs.boolean, location='args', required=False, help='List Recommendations by liked')
rec_args.add_argument('amount', type=int, location='args', required=False,
                      help='Maximum number of Recommendations to be returned')


######################################################################
# LIST ALL RECOMMENDATIONS
######################################################################
def get_recommendation_based_on_filter(rec_type, liked):
    """Returns list of the Recommendations with or without specific type and liked filters"""
    recommendations = []
    cond_type = None
    cond_liked = None

    if rec_type is not None:
        if rec_type in list(RecommendationType):
            cond_type = rec_type
        else:
            abort(
                status.HTTP_400_BAD_REQUEST,
                f"Type '{rec_type}' is an invalid recommendation type.",
            )

    if liked is not None:
        cond_liked = liked

    if cond_type is None and cond_liked is None:
        recommendations = Recommendation.all()
    else:
        recommendations = Recommendation.find_by_attributes(rec_type=cond_type, liked=cond_liked)

    return recommendations


######################################################################
#  PATH: /recommendations
######################################################################
@api.route('/recommendations', strict_slashes=False)
class RecommendationCollection(Resource):
    """
    Handles all interactions with collections of Recommendations
    """

    # ------------------------------------------------------------------
    #  LIST ALL RECOMMENDATIONS
    # ------------------------------------------------------------------
    @api.doc('list_recommendations')
    @api.expect(rec_args, validate=True)
    @api.response(400, 'The query parameter was not valid')
    @api.marshal_list_with(recommendation_model, code=200)
    def get(self):
        """Returns list of the Recommendations"""
        app.logger.info("Request for Recommendations list")

        args = rec_args.parse_args()
        rec_type = args.get("type")
        liked = args.get("liked")
        recommendations = get_recommendation_based_on_filter(rec_type, liked)

        pid = None
        amount = None

        try:
            pid = int(args.get('pid'))
        except TypeError:  # pylint: disable=broad-except
            pass

        try:
            amount = int(args.get('amount'))
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

        return result, status.HTTP_200_OK

    # ------------------------------------------------------------------
    #  CREATE A NEW RECOMMENDATION
    # ------------------------------------------------------------------
    @api.doc('create_recommendations')
    @api.response(400, 'The posted data was not valid')
    @api.expect(create_model)
    @api.marshal_with(recommendation_model, code=201)
    def post(self):
        """ Create a new recommendation """

        app.logger.info("Request to create a Recommendation")

        # Create the account
        rec = Recommendation()
        rec.deserialize(api.payload)
        rec.create()

        # Create a message to return
        message = rec.serialize()
        location_url = api.url_for(RecommendationResource, recommendation_id=rec.id, _external=True)

        return message, status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
#  PATH: /recommendations/{id}
######################################################################
@api.route('/recommendations/<int:recommendation_id>')
@api.param('recommendation_id', 'The recommendation identifier')
class RecommendationResource(Resource):
    """
    RecommendationResource class

    Allows the manipulation of a single Recommendation
    GET /recommendations/{id} - Returns a Recommendation with the id
    PUT /recommendations/{id} - Update a Recommendation with the id
    DELETE /recommendations/{id} -  Deletes a Recommendation with the id
    """

    # ------------------------------------------------------------------
    #  RETRIEVE A RECOMMENDATION
    # ------------------------------------------------------------------
    @api.doc('get_recommendations')
    @api.response(404, 'Recommendation not found')
    @api.marshal_with(recommendation_model)
    def get(self, recommendation_id):
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

        return rec.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    #  UPDATE A RECOMMENDATION
    # ------------------------------------------------------------------
    @api.doc('update_recommendations')
    @api.response(404, 'Recommendation not found')
    @api.response(400, 'The posted Recommendation data was not valid')
    @api.expect(create_model)
    @api.marshal_with(recommendation_model)
    def put(self, recommendation_id):
        """ Update a recommendation """
        app.logger.info("Request to update a Recommendation")

        rec = Recommendation.find(recommendation_id)
        if not rec:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Recommendation with id '{recommendation_id}' could not be found.",
            )

        rec.deserialize(api.payload)
        rec.update()
        return rec.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    #  DELETE A RECOMMENDATION
    # ------------------------------------------------------------------
    @api.doc('delete_recommendations')
    @api.response(204, 'Recommendation deleted')
    def delete(self, recommendation_id):
        """ Create a new recommendation """

        app.logger.info("Request to delete a Recommendation")

        # Delete the recommendation
        rec = Recommendation.find(recommendation_id)
        if rec:
            rec.delete()
            app.logger.info('Recommendation with id [%s] was deleted', recommendation_id)

        return "", status.HTTP_204_NO_CONTENT


######################################################################
#  PATH: /recommendations/{id}/like
######################################################################
@api.route('/recommendations/<int:recommendation_id>/like')
@api.param('recommendation_id', 'The Recommendation identifier')
class LikeResource(Resource):
    """ Like actions on a Recommendation """
    @api.doc('like_recommendations')
    @api.response(404, 'Recommendation not found')
    @api.response(409, 'The Recommendation is not available for being liked')
    @api.marshal_with(recommendation_model, code=200)
    def put(self, recommendation_id):
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
        return rec.serialize(), status.HTTP_200_OK


######################################################################
#  PATH: /recommendations/{id}/unlike
######################################################################
@api.route('/recommendations/<int:recommendation_id>/unlike')
@api.param('recommendation_id', 'The Recommendation identifier')
class UnlikeResource(Resource):
    """ Unlike actions on a Recommendation """
    @api.doc('unlike_recommendations')
    @api.response(404, 'Recommendation not found')
    @api.response(409, 'The Recommendation is not available for being unliked')
    @api.marshal_with(recommendation_model, code=200)
    def put(self, recommendation_id):
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
        return rec.serialize(), status.HTTP_200_OK
