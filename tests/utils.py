'''
Util functions for test cases
'''

from service.models import Recommendation


def make_recommendation(pid, recommendated_pid, rec_type=0):
    "Generate a Recommendation by the given arguments"
    rec = Recommendation()
    rec.pid = pid
    rec.recommended_pid = recommendated_pid
    rec.type = rec_type
    return rec
