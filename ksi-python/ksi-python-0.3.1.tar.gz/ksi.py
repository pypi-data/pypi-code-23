#####################################################################
# Copyright (C) 2015-18 Guardtime, Inc
# This file is part of the Guardtime client SDK.
#
# Licensed under the Apache License, Version 2.0 (the "License").
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES, CONDITIONS, OR OTHER LICENSES OF ANY KIND, either
# express or implied. See the License for the specific language governing
# permissions and limitations under the License.
# "Guardtime" and "KSI" are trademarks or registered trademarks of
# Guardtime, Inc., and no license to trademarks is granted; Guardtime
# reserves and retains all trademark rights.

import os
import hashlib
from datetime import datetime
import _ksi


class KsiSignature(object):
    """ KSI Signature object.

    Exists only in instantiated, integrity-checked form. Created by the KSI class only.
    Do not initialize directly.

    Please dispose with ``del`` if not needed.

    Args:
        ksi (class KSI): KSI class. Necessary to avoid early garbage collection.
        token: reference to a signature.
    """

    def __init__(self, ksi, token):
        self.__ksi_ref = ksi
        self.__token = token

    def __del__(self):
        self.__ksi_ref.verification.ksi_cleanup_sig(self.__token)

    def get_opaque_token(self):
        """ Returns a reference to a signature, ready to be passed to C language binding.
            Internal use.
        """
        return self.__token

    def set_opaque_token(self, new_token):
        """ Sets a reference to a signature, ready to be passed to C language binding
            Internal use.
        """
        _ksi.ksi_cleanup_sig(self.__token)
        self.__token = new_token

    def serialize(self):
        """ Returns a data blob which can be stored into file or db field.

        The blob can be used later to instantiate a `KsiSignature`, e.g.::

            sig = KSI.parse(blob)

        Returns:
            str or buffer: binary blob.

        Raises:
            ksi.ParseError: on corrupted input
            ksi.Error: or its subclass on other KSI errors
        """
        return _ksi.ksi_serialize(self.__token)

    def get_hash_algorithm(self):
        """ Returns the hash algorithm name used for hashing data during signing.

        It is important to use exactly the same hash algorithm for hashing data during
        signing and during signature verification.

        Note:
            Returns algorithm names like ``SHA2-256``. Some older libraries, like Python's
            hashlib and OpenSSL use names like ``SHA256``. Use some processing to get
            legacy compatible name, for example:

                sig.get_hash_algorithm().replace("SHA2-", "sha")

        Returns:
            str: hash algorithm name

        Raises:
            ksi.Error: or its subclass on KSI errors
        """
        return _ksi.ksi_get_hash_algorithm(self.__token)

    def get_data_hash(self):
        """ Returns the hash algorithm and hash value of signed data

        See the note about `get_hash_algorithm()`

        Returns:
            (str, str/buffer): A tuple of hash algorithm name and a binary data hash.

        Raises:
            ksi.Error: or its subclass on KSI errors
        """
        return _ksi.ksi_get_data_hash(self.__token)

    def get_hasher(self):
        """ Returns a data hasher object from hashlib.

        Used hash algorithm matches the one which was used during the signature creation.

        Returns:
            Object: a new hashing object from `hashlib`

        Raises:
            ksi.Error: or its subclass on KSI errors
            ValueError: hashlib does not support used hash algorithm
        """
        algname = _ksi.ksi_get_hash_algorithm(self.__token).lower()
        algname = algname.replace("sha2-", "sha")
        algname = algname.replace("-", "")
        return hashlib.new(algname)

    def get_signing_time_utc(self):
        """ Extract cryptographically protected signing time from a signature.

        Returns:
            Object: ``datetime.datetime`` object, using UTC timezone.

        Raises:
            ksi.Error: or its subclass on KSI errors
        """
        signing_time = _ksi.ksi_get_signing_time(self.__token)
        return datetime.utcfromtimestamp(signing_time)

    def get_signing_time(self):
        """ Extract cryptographically protected signing time from a signature.

        Returns:
            Object: ``datetime.datetime`` object, in local timezone.

        Raises:
            ksi.Error: or its subclass on KSI errors
        """
        signing_time = _ksi.ksi_get_signing_time(self.__token)
        return datetime.fromtimestamp(signing_time)

    def get_signer_id(self):
        """ Extract cryptographically protected data signer's identity.

        This identifier contains hierarchical namespace of KSI aggregators, gateway and end user.
        May look like ``GT :: GT :: Company :: user.name``.

        Returns:
            str: a signer's id prefixed with full aggregator hierarchy.

        Raises:
            ksi.Error: or its subclass on KSI errors
        """
        return _ksi.ksi_get_signer_id(self.__token)

    def is_extended(self):
        """ Checks if signature is extened and contains a publication record.

        Returns:
            Bool: True if extended, False if not.

        Raises:
            ksi.Error: or its subclass on KSI errors
        """
        return _ksi.ksi_is_extended(self.__token)

    def get_publication_data(self):
        """ Returns publication data used for extending this signature.

        Returned data can be used to validate the signature in strongest possible form,
        using an independent publication. Publications references refer to the choice of mediums;
        publication code can be compared with one printed in chosen medium.

        Returns:
            None if publication record is not available. A dictionary on success, see example below::

            {
                'refs': [
                    u'ref1',
                    u'Financial Times, ISSN: 0307-1766, 2015-06-17',
                    u'https://twitter.com/Guardtime/status/611103980870070272'
                ],
                'publication': 'AAAAAA-CVPYKY-AANVCV-Q7IJFM-ZJ5YBK-BNXRKG-IWIFER-5XXL73-4NXXLS-D6CROT-QUMAHA-JDWBQI',
                'publishing_time_t': 1434326400L,
                'publishing_time': datetime.datetime(2015, 6, 15, 0, 0)
            }

        Raises:
            ksi.Error: or its subclass on KSI errors
        """
        r = _ksi.ksi_get_publication_data(self.__token)
        if r and r['publishing_time_t']:
            r['publishing_time'] = datetime.utcfromtimestamp(r['publishing_time_t'])
        return r


class KSI(object):
    """KSI service provider class. Holds context and service parameters.

    Please dispose with ``del`` if not needed, just like signatures created by this class.

    Args:
        signing_service (dict):   Signing/aggregation service access parameters. A dictionary
                                  with following keys: {'url': .., 'user': ..., 'pass': ...}
        extending_service (dict): Extending service access parameters. A dictionary
                                  with following keys: {'url': .., 'user': ..., 'pass': ...}
        publications_file (str, optional):  Publications file download URL. Default one works
                                  with Guardtime commercial KSI service.
        publications_cnstr (dict, optional):  Publications file verification constraints: signing
                                  certificate (must be issued under a root in global system
                                  truststore) fields are validated against provided rules, e.g.::

                                        {"email" : "publications@guardtime.com"}

                                  Default one works with Guardtime commercial KSI service.

    Properties:
        verification: constants specifying verification policies. see ``set_verification_policy()``
    """
    def __init__(self, signing_service, extending_service,
                 publications_file='http://verify.guardtime.com/ksi-publications.bin',
                 publications_cnstr={"email" : "publications@guardtime.com"}
                ):

        self.__ctx = _ksi.ksi_init(signing_service['url'], signing_service['user'], signing_service['pass'],
                                   extending_service['url'], extending_service['user'], extending_service['pass'],
                                   publications_file, publications_cnstr)

        self.verification = _ksi
        self.__policy = _ksi.POLICY_GENERAL_EXT

    def __del__(self):
        self.verification.ksi_cleanup(self.__ctx)

    def sign_hash(self, data_hash):
        """ Signs a data hash.

        Note:
            Signing is a synchronous operation, blocks for 1..2 seconds.
            Signing server parameters must be specified.

        Args:
            Object: hash created using a hasher from Python ``hashlib``.

        Returns:
            KsiSignature: see ``KsiSignature`` class in this module.

        Raises:
            ksi.Error: or its subclass on KSI errors
        """
        return KsiSignature(self, _ksi.ksi_sign(self.__ctx, data_hash.name, data_hash.digest()))

    def sign_blob(self, blob):
        """ Signs a data blob.

        Note:
            Signing is a synchronous operation, blocks for 1..2 seconds.
            Signing server parameters must be specified.

        Args:
            str/buffer: data to be signed.

        Returns:
            KsiSignature: see ``KsiSignature`` class in this module.

        Raises:
            ksi.Error: or its subclass on KSI errors
        """
        h = hashlib.sha256(blob)
        return KsiSignature(self, _ksi.ksi_sign(self.__ctx, h.name, h.digest()))

    def parse(self, blob):
        """ Instatiates a KsiSignature object from earlier serialized binary representation.

        Args:
            str/buffer: binary representation of signature data.

        Returns:
            KsiSignature: A newly instantiated ``KsiSignature`` object.

        Raises:
            ksi.Error: or its subclass on KSI errors
        """
        return KsiSignature(self, _ksi.ksi_parse(self.__ctx, blob))

    def extend(self, sig):
        """ Extend the signature to the latest available publication.

        Modifies the signature in-place. Extender sever must be specified earlier.
        Possible, if there is at least 1 publication created after signing, i.e.
        quite safe to try if 35 days have passed from signing.

        Extending a signature is very useful before long-term archiving. This makes
        distant-future verification possible without access to extender service.

        Args:
            KsiSignature:

        Returns:
            `True` if extending was successful, `False` if no suitable publication was found.

        Raises:
            ksi.Error: or its subclass on KSI errors
        """
        success, ext = _ksi.ksi_extend(self.__ctx, sig.get_opaque_token())
        if success:
            sig.set_opaque_token(ext)
        return success

    def verify(self, sig):
        """ Verify signature consistency. No document content check.

        No return value.

        Raises:
            ksi.Error: or its subclass on KSI errors
        """
        return _ksi.ksi_verify_sig(self.__ctx, sig.get_opaque_token())

    def set_verification_policy(self, new_policy):
        """ Specify a verification policy for future verifications.

            Note that it is hard to fail with the default one.
            Change only if necessary. Suffix ``_EXT`` instructs verification
            to transparently extend the signature if possible.

        Args:
            policy_id: A property from the KSI object::

               KSI.verification.POLICY_GENERAL
               KSI.verification.POLICY_GENERAL_EXT
               KSI.verification.POLICY_KEY_BASED
               KSI.verification.POLICY_CALENDAR_BASED
               KSI.verification.POLICY_PUBLICATIONS_FILE_BASED
               KSI.verification.POLICY_PUBLICATIONS_FILE_BASED_EXT

        """
        self.__policy = new_policy

    def get_verification_policy(self):
        """ Retrieves the current verification policy.

        Returns:
            int: Identifier. see ``set_verification_policy()`` for a list of values.
        """
        return self.__policy

    def verify_hash(self, sig, data_hash):
        """ Verify a signature and a provided data hash of signed data.

        Args:
            KsiSignature: Signature object.
            data_hash: A hasher from ``hashlib``, after processing its input data.

        Returns:
            (result (boolean), code (str), reason (str)): A 3-tuple with following data:
                True if signature is OK; False if there is conslusive evidence that signature
                is invalid and further action can not change the situation.
                Code: error code as string.
                See https://github.com/guardtime/libksi/blob/v3.16.2482/src/ksi/policy.h#L70.
                Reason: Human readable message.

        Raises:
            ValueError: Final decision is not possible given current input data. Changing something,
                e.g. verification policy, might help to find a conclusive answer.

            ksi.Error: or its subclass on KSI errors
        """
        return _ksi.ksi_verify_hash_with_policy(self.__ctx, sig.get_opaque_token(),
                                                data_hash.name, data_hash.digest(), self.__policy)

    def verify_blob(self, sig, blob):
        """ Verify a data blob and its signature.

        Args:
            KsiSignature: Signature object.
            blob: A string or buffer containing binary data bytes.

        Returns:
            (result (boolean), code (str), reason (str)): A 3-tuple with following data:
                True if signature is OK; False if there is conslusive evidence that signature
                is invalid and further action can not change the situation.
                Code: error code as string.
                See https://github.com/guardtime/libksi/blob/v3.16.2482/src/ksi/policy.h#L70.
                Reason: Human readable message.

        Raises:
            ValueError: Final decision is not possible given current input data. Changing something,
                e.g. verification policy, might help to find a conclusive answer.

            ksi.Error: or its subclass on KSI errors
        """
        hasher = sig.get_hasher()
        hasher.update(blob)
        return _ksi.ksi_verify_hash_with_policy(self.__ctx, sig.get_opaque_token(),
                                                hasher.name, hasher.digest(), self.__policy)

def ksi_env():
    """ Helper for initializing a KSI class with KSI service parameters from the environment.

    Please use default KSI_PUBFILE... parameters if using Guardtime commercial KSI service.
    System environment parameters should look like::

        KSI_AGGREGATOR='url=http://url user=name pass=xyz'
        KSI_EXTENDER='url=http://url user=name pass=xyz'
        KSI_PUBFILE='http://verify.guardtime.com/ksi-publications.bin'
        KSI_PUBFILE_CNSTR='{"email" : "publications@guardtime.com"}'

    Example:
        ``KSI = ksi.KSI(**ksi.ksi_env())``

    Raises:
        ksi.FormatError: when an environment variable misses required component.
    """

    def __parse_value(value):
        struct = {}
        for thing in value.split():
            key, val = thing.split('=')
            struct[key] = val
        if 'url' not in struct:
            raise FormatError('KSI service parameter misses required component "url"')
        if 'user' not in struct:
            raise FormatError('KSI service parameter misses required field "user"')
        if 'pass' not in struct:
            raise FormatError('KSI service parameter misses required field "pass"')
        return struct

    ret = {}
    if 'KSI_AGGREGATOR' in os.environ:
        ret['signing_service'] = __parse_value(os.environ['KSI_AGGREGATOR'])
    if 'KSI_EXTENDER' in os.environ:
        ret['extending_service'] = __parse_value(os.environ['KSI_EXTENDER'])
    if 'KSI_PUBFILE' in os.environ:
        ret['publications_file'] = os.environ['KSI_PUBFILE']
    if 'KSI_PUBFILE_CNSTR' in os.environ:
        ret['publications_cnstr'] = os.environ['KSI_PUBFILE_CNSTR']
    return ret


# Note: following exceptions are expected to be here by _ksi.c. Throws RuntimeError if not found
class Error(Exception):
    """ Unspecfied KSI error """
    pass

class ConfigurationError(Error):
    """ Necessary parameters are not configured """
    pass

class FormatError(Error):
    """ Invalid argument, format, or parameter. Untrusted or unavailable hash algorithm. """
    pass

class InvalidSignatureError(Error):
    """
         * Invalid KSI signature.
         * Invalid PKI signature.
         * The PKI signature is not trusted by the API.
         * The objects used are in an invalid state.
    """
    pass

class NetworkError(Error):
    """
         * A network error occurred.
         * A network connection timeout occurred.
         * A network send timeout occurred.
         * A network receive timeout occurred.
         * A HTTP error occurred.
    """
    pass

class PublicationError(Error):
    """  Problems with publication based verification.

         * The extender returned a wrong calendar chain.
         * No suitable publication to extend to.
         * The publication in the signature was not found in the publications file.
         * Invalid publication.
         * The publications file is not signed.
    """
    pass

class CryptoError(Error):
    """
         * Cryptographic operation could not be performed. Likely causes are
           unsupported cryptographic algorithms, invalid keys and lack of
           resources.
    """
    pass

class ServiceAuthError(Error):
    """
         * The request could not be authenticated (missing or unknown login
           identifier, MAC check failure, etc).
    """
    pass

class ServiceError(Error):
    """ Various service errors.

        * The request is still pending.
        * The request ID in response does not match with request ID in request.
        * Pattern for errors with client request.
        * The request contained invalid payload (unknown payload type, missing
          mandatory elements, unknown critical elements, etc).
        * The server encountered an unspecified internal error.
        * The server encountered unspecified critical errors connecting to
          upstream servers.
        * No response from upstream aggregators.
        * The extender returned an error.
        * The request indicated client-side aggregation tree larger than allowed
          for the client (retrying would not succeed either).
        * The request combined with other requests from the same client in the same
          round would create an aggregation sub-tree larger than allowed for the client
          (retrying in a later round could succeed).
        * Too many requests from the client in the same round (retrying in a later
          round could succeed)
        * Input hash value in the client request is longer than the server allows.
        * Received PDU v2 response to PDU v1 request. Configure the SDK to use PDU
          v2 format for the given aggregator.
        * Received PDU v1 response to PDU v2 request. Configure the SDK to use PDU
          v1 format for the given aggregator.
    """
    pass

class ServiceExtenderBlockchainError(ServiceError):
    """ The Extender server does not have required period of Calendar Blockchain.

        * The request asked for a hash chain going backwards in time Pattern for
          local errors in the server.
        * The server misses the internal database needed to service the request
          (most likely it has not been initialized yet).
        * The server's internal database is in an inconsistent state.
        * The request asked for hash values older than the oldest round in the
          server's database.
        * The request asked for hash values newer than the newest round in the
          server's database.
    """
