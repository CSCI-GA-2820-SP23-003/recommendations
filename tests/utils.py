# pylint: disable=R0401
'''
Util functions for test cases
'''

from service.models import Recommendation, RecommendationType


def make_recommendation(pid, recommendated_pid, rec_type=RecommendationType.DEFAULT, liked=False):
    "Generate a Recommendation by the given arguments"
    rec = Recommendation()
    rec.pid = pid
    rec.recommended_pid = recommendated_pid
    rec.type = rec_type
    rec.liked = liked
    return rec
