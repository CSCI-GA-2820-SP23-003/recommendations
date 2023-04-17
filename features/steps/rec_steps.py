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
    for pet in context.resp.json():
        context.resp = requests.delete(f"{rest_endpoint}/{pet['id']}")
        expect(context.resp.status_code).to_equal(204)

    # load the database with new recommendations
    for row in context.table:
        payload = {
            "Recommendation ID": row['id'],
            "Product ID": row['pid'],
            "Recommended product ID": row['recommended_pid'],
            "Type": row['type'],
            "Liked": row['liked']
        }
        context.resp = requests.post(rest_endpoint, json=payload)
        expect(context.resp.status_code).to_equal(201)
