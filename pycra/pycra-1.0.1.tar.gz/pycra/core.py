import hashlib
import hmac
import datetime
import pbkdf2helper


# To Remember use HMAC with this signature H Hmac(key, Msg, digestmod)
# see update and copy for manipulation on hmac object
# see digest, hexdigest and new for generation


def create_challenge():
    """
    Create a new Nonce (Challange) based on random salt and time

    :return: nonce as HMAC
    """

    key = pbkdf2helper.generate_salt(12)
    msg = str(datetime.datetime.utcnow())
    nonce = hmac.new(key.encode(), msg.encode(), hashlib.sha256).hexdigest()

    return nonce


def auth_check(nonce, password_hash, response):
    """
    Compare Answer for the given challenge

    :param nonce: nonce as String
    :param password_hash: Hash password as String
    :param response: Answer from Client
    :return: True | False

    """
    print("______Auth Check________")
    print("Response from client: " + str(response))

    answer = calculate_answer(nonce, password_hash).hexdigest()

    print("Answer on server: " + str(answer))

    check = hmac.compare_digest(answer, response)
    print("Is Auth: " + str(check))

    return check


def calculate_answer(nonce, password_hash):
    """
    Calculate Answer on Server
    -> Answer = HMAC(nonce, password_hash, sha256)

    :param nonce:
    :param password:

    :return: answer
    """

    answer = hmac.new(key=password_hash.encode(), msg=nonce.encode(), digestmod=hashlib.sha256)
    #    answer = hmac.new(msg=password_hash.encode(), key=nonce.encode(), digestmod=hashlib.sha256)


    return answer


def calculate_answer_for_pbkdf2(nonce, password, algorithm, salt, iterations):
    """
    Calculate Answer on Client for PBKDF2 hashed Passwords.

    :param nonce
    :param password:
    :param algorithm:
    :param salt:
    :param iterations:
    :return: answer
    """

    password_hash = pbkdf2helper.encode(password, algorithm, salt, int(iterations))
    answer = calculate_answer(nonce, password_hash)

    return answer.hexdigest()
