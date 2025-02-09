"""empty message

Revision ID: 264bf88d5503
Revises: 94f6b9439876
Create Date: 2016-09-22 15:20:19.457033

"""

# revision identifiers, used by Alembic.
revision = '264bf88d5503'
down_revision = '94f6b9439876'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('proxy', sa.Column('passwd', sa.String(length=30), nullable=True))
    op.add_column('proxy', sa.Column('src', sa.String(length=30), nullable=True))
    op.add_column('proxy', sa.Column('user', sa.String(length=30), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('proxy', 'user')
    op.drop_column('proxy', 'src')
    op.drop_column('proxy', 'passwd')
    ### end Alembic commands ###
