# coding: utf-8
from sqlalchemy import Column, ForeignKey, Integer, Unicode, TIMESTAMP, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base


class OtpKey(Base):
    __tablename__ = 'otp_key'

    key = Column(Unicode(16), primary_key=True, nullable=False, index=True)
    private_identity = Column(Unicode(16), nullable=False)
    aeskey = Column(Unicode(32), nullable=False)
    enabled = Column(Boolean, nullable=False, default=1)
    counter = Column(Integer, nullable=False, default=1)
    time = Column(Integer, nullable=False, default=1)
    created_on = Column(TIMESTAMP, default=func.now(), nullable=False)
    remote_server = Column(Boolean, default=0)
    # Foreign keys
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)

    # Relationships
    otp_cloud_service = relationship('OtpCloudService', cascade='all, delete-orphan')

    def __repr__(self):
        return "OtpKey(key={self.key}, private_identity={self.private_identity}, " \
               "aeskey={self.aeskey}, enabled={self.enabled}, counter={self.counter}, " \
               "time={self.time}, remote_server={self.remote_server}, created_on={self.created_on}, " \
               "user_id={self.user_id})".format(self=self)
