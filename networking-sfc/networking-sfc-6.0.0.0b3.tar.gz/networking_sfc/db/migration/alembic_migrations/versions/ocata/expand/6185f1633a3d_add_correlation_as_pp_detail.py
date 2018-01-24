# Copyright 2017 Intel Corporation.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#

"""description of revision

Revision ID: 6185f1633a3d
Revises: b3adaf631bab
Create Date: 2017-02-19 00:00:00.000000

"""

# revision identifiers, used by Alembic.
revision = '6185f1633a3d'
down_revision = 'b3adaf631bab'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('sfc_portpair_details',
                  sa.Column('correlation',
                            sa.String(length=255),
                            nullable=True))
