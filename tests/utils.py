from service.models import Recommendation


################################
# Util functions for testing
################################

def make_recommendation(pid, recommendated_pid, rec_type=0):
    rec = Recommendation()
    rec.pid = pid
    rec.recommended_pid = recommendated_pid
    rec.type = rec_type
    return rec
