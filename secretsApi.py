from flask import Blueprint
from frontegg.flask import frontegg, withAuthentication

secretsApi = Blueprint('account_api', __name__)


@secretsApi.route("/secret1")
@withAuthentication()
def secret1():
    return "Jack Daniel (the founder of the whiskey) died from kicking a safe. When he kicked it, he broke his toe which got infected. He eventually died from blood poisoning."