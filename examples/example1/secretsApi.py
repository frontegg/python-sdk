from flask import Blueprint
from frontegg.flask import withAuthentication

secretsApi = Blueprint('secretsApi', __name__)


@secretsApi.route("/secret1")
@withAuthentication()
def secret1():
    return "Jack Daniel (the founder of the whiskey) died from kicking a safe. When he kicked it, he broke his toe " \
           "which got infected. He eventually died from blood poisoning. "


@secretsApi.route("/secret2")
@withAuthentication()
def secret2():
    return "By applying even pressure on an egg, it is nearly impossible to break the shell by squeezing it."
