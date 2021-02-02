"""empty message

Revision ID: a867624cd782
Revises: c55970f88dd1
Create Date: 2020-12-24 22:01:06.983381

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a867624cd782'
down_revision = 'c55970f88dd1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Artist', sa.Column('genres2', sa.ARRAY(sa.String()), server_default='{}', nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Artist', 'genres2')
    # ### end Alembic commands ###