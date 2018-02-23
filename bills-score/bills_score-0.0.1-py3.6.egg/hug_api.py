"""
Uses hug api to expose an http endpoint.
"""
from .bills_model import main
from falcon import HTTP_404
from .user_schema_db import User, db_session
import hug
import logging
import bcrypt

logger = logging.getLogger(__name__)


def api_token_verify(token):
    """Return 401 unauthorized if token does no exists

    Use Bcrypt for encrpytion checking
    """

    users = db_session.query(User).all()
    tokens = [t.token for t in users]
    for user in users:
        if bcrypt.checkpw(token.encode(), user.token):
            return user
    return False


api_key_authentication = hug.authentication.api_key(api_token_verify)


# @hug.cli()
# @hug.get(examples='biller_code=MWSIN&account_no=57699266&transaction_id=231312')
# @hug.local()
def cbci_connect(biller_code: hug.types.text,
                 account_no: hug.types.text,
                 transaction_id: hug.types.text,
                 response, hug_timer=10):
    """Endpoint for getting bills score

    Parameters:
        biller_code   :    string
        account_no    :    string
        transaction_id:    string

    Takes an average of 6 seconds to return a response

    Used for testing purposes only

    """
    try:
        score = main(biller_code, account_no)
    except Exception as e:
        response.status = HTTP_404
        return {"error": e.__str__()}
    data = {
            'score_type': 'BC',
            'transaction_id': transaction_id,
            'account_no': account_no,
            'score': score,
            'biller_code': biller_code,
            'timer': float(hug_timer)}
    return data


@hug.cli()
@hug.post(versions=1, requires=api_key_authentication)
@hug.local()
def cbci_score(biller_code: hug.types.text,
               account_no: hug.types.text,
               transaction_id: hug.types.text,
               response, hug_timer=10):
    """ Post API endpoint for grabbing Bayad Center Score
    Parameters:
        biller_code   :    string
        account_no    :    string
        transaction_id:    string

    Takes an average of 6 seconds to return a response
    """
    try:
        score = main(biller_code, account_no)
    except Exception as e:
        response.status = HTTP_404
        return {"error": e.__str__()}
    data = {
            'score_type': 'BC',
            'transaction_id': transaction_id,
            'score': score,
            'timer': float(hug_timer)}
    return data


@hug.get('/key_auth', requires=api_key_authentication)
def key_check(user: hug.directives.user):
    return "valid"


if __name__ == '__main__':
    cbci_connect.interface.cli()
