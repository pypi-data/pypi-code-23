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

"""Add ip_allocation to port """

from alembic import op
import sqlalchemy as sa

from neutron.db import migration


# revision identifiers, used by Alembic.
revision = '5cd92597d11d'
down_revision = '6b461a21bcfc'

# milestone identifier, used by neutron-db-manage
neutron_milestone = [migration.NEWTON]


def upgrade():
    op.add_column('ports',
                  sa.Column('ip_allocation',
                            sa.String(length=16),
                            nullable=True))
