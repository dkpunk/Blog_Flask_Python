"""new fields added to user table

Revision ID: 8166696f9a88
Revises: 1ae72242b5c3
Create Date: 2019-10-11 03:08:34.167328

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8166696f9a88'
down_revision = '1ae72242b5c3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('about_me', sa.String(length=140), nullable=True))
    op.add_column('user', sa.Column('last_seen', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'last_seen')
    op.drop_column('user', 'about_me')
    # ### end Alembic commands ###
