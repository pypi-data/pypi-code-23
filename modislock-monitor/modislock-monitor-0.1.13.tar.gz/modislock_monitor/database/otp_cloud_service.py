# coding: utf-8
from sqlalchemy import Column, ForeignKey, Integer, Unicode
from .database import Base


class OtpCloudService(Base):
    __tablename__ = 'otp_cloud_service'

    cloud_id = Column(Integer, primary_key=True, autoincrement=True)
    yubico_user_name = Column(Unicode(45), nullable=True)
    yubico_secret_key = Column(Unicode(45), nullable=True)
    # Foreign keys
    otp_key_key = Column(Unicode(16), ForeignKey('otp_key.key'), nullable=False)

    def __repr__(self):
        return "OtpCloudService(cloud_id={self.cloud_id}, yubico_user_name={self.yubico_user_name}, " \
               "yubico_secret_key={self.yublico_secret_key}, " \
               "otp_key_key={self.otp_key_key})".format(self=self)
