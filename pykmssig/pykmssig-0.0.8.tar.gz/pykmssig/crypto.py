import aws_encryption_sdk
import boto3
import json

from pykmssig.hashes import get_digests
from pykmssig import settings


class Operation(object):
    def __init__(self, boto_session=None):
        self.boto_session = boto_session
        self.key_provider = None
        self.sts_client = None

    def sign(self, plaintext):
        digests = get_digests(plaintext)
        encrypted_digests = self._encrypt_data(json.dumps(digests))
        return encrypted_digests

    def verify(self, ciphertext, plaintext):
        """Verify Operation.

        Verify the signature for a given piece of data by
        decrypting the signatures and comparing the hashes
        to the new digests from the plaintext payload.
        :param ciphertext: Ciphertext from your prior signature.
        :param plaintext: Payload you're comparing against.
        :return: Dict response
        """

        sigs_a = get_digests(plaintext)
        sigs_b = json.loads(self._decrypt_data(ciphertext))

        if sigs_a == sigs_b:
            return {
                'status': 'valid',
                'sigs_a': sigs_a,
                'sigs_b': sigs_b
            }
        else:
            return {
                'status': 'invalid',
                'sigs_a': sigs_a,
                'sigs_b': sigs_b
            }

    def _decrypt_data(self, ciphertext):
        if not self.key_provider:
            self.key_provider = \
                self._build_multiregion_kms_master_key_provider()

        # Decrypt data using only static master key provider
        plaintext, header = aws_encryption_sdk.decrypt(
            source=ciphertext,
            key_provider=self.key_provider
        )

        return plaintext

    def _encrypt_data(self, plaintext):
        # Get all the master keys needed
        if not self.key_provider:
            self.key_provider = \
                self._build_multiregion_kms_master_key_provider()

        # Encrypt the provided data
        ciphertext, header = aws_encryption_sdk.encrypt(
            source=plaintext,
            key_provider=self.key_provider
        )
        return ciphertext

    def _build_multiregion_kms_master_key_provider(self):
        """Setup KMS Envelope Operations as Per the Guide.

        :return: string
        """
        self._get_sts_client()
        regions = ['us-west-2']
        alias = settings.SIGNING_KEY_ALIAS
        arn_template = 'arn:aws:kms:{region}:{account_id}:{alias}'

        # Create AWS KMS master key provider
        if self.boto_session is not None:
            kms_master_key_provider = aws_encryption_sdk.KMSMasterKeyProvider(
                botocore_session=self.boto_session._session
            )
        else:
            kms_master_key_provider = aws_encryption_sdk.KMSMasterKeyProvider()

        # Find your AWS account ID
        if settings.SIGNING_KEY_ACCOUNT_ID is None:
            account_id = self.sts_client.get_caller_identity()['Account']

        else:
            account_id = settings.SIGNING_KEY_ACCOUNT_ID

        # Add the KMS alias in each region to the master key provider
        for region in regions:
            kms_master_key_provider.add_master_key(
                arn_template.format(
                    region=region,
                    account_id=account_id,
                    alias=alias
                )
            )

        return kms_master_key_provider

    def _get_sts_client(self):
        if not self.sts_client:
            self.sts_client = boto3.client('sts')
