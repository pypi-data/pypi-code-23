# Copyright 2014 - Rackspace
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""add username to assembly table

Revision ID: 269f9da4b38e
Revises: 586c15b92842
Create Date: 2014-11-14 20:48:25.457672

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '269f9da4b38e'
down_revision = '586c15b92842'


def upgrade():
    op.add_column('assembly',
                  sa.Column('username', sa.String(length=256)))


def downgrade():
    op.drop_column('assembly', 'username')
