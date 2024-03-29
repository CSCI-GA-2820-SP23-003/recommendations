"""
Rec Steps

Steps file for recommendations.feature

For information on Waiting until elements are present in the HTML see:
    https://selenium-python.readthedocs.io/waits.html
"""
import requests
from behave import given
from compare import expect


@given('the following recommendations')
def step_impl(context):
    """ Delete all Recommendations and load new ones """
    # List all of the pets and delete them one by one
    rest_endpoint = f"{context.BASE_URL}/recommendations"
    context.resp = requests.get(rest_endpoint)
    expect(context.resp.status_code).to_equal(200)
    for recommendation in context.resp.json():
        context.resp = requests.delete(f"{rest_endpoint}/{recommendation['id']}")
        expect(context.resp.status_code).to_equal(204)

    # load the database with new recommendations
    for row in context.table:
        payload = {
            "pid": row['pid'],
            "recommended_pid": row['recommended_pid'],
            "type": row['type'],
            "liked": row['liked'] in ['True', 'true', '1']
        }
        context.resp = requests.post(rest_endpoint, json=payload)
        expect(context.resp.status_code).to_equal(201)
