from __future__ import absolute_import
from AuthEncoding.compat import b
from AuthEncoding import constant_time_compare
import bcrypt


WORK_FACTOR = 12  # 12=bcrypt default


class BCryptScheme:
    """Schema for encrypting and validation with bcrypt."""

    def encrypt(self, pw):
        return bcrypt.hashpw(
            b(pw), bcrypt.gensalt(WORK_FACTOR))

    def validate(self, reference, attempt):
        compare = bcrypt.hashpw(b(attempt), b(reference))
        return constant_time_compare(compare, reference)
