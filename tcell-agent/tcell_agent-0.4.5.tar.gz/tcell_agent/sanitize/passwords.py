from __future__ import unicode_literals

import hmac
import hashlib

from tcell_agent.config.configuration import CONFIGURATION


def fingerprint_password(password, user_id):
    if CONFIGURATION.app_id and CONFIGURATION.password_hmac_key and password and password.strip():
        string_builder = [CONFIGURATION.app_id, ":", password, ":"]
        if user_id:
            string_builder.append(user_id)

        try:
            hmac_key_enc = bytes(CONFIGURATION.password_hmac_key, "utf-8")
        except:
            hmac_key_enc = bytes(CONFIGURATION.password_hmac_key)

        digest = hmac.new(hmac_key_enc, "".join(string_builder).encode('utf-8'), hashlib.sha256).hexdigest()
        return digest[:8]

    return None
