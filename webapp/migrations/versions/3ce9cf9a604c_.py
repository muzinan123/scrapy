"""empty message

Revision ID: 3ce9cf9a604c
Revises: 4ffd5f98d41e
Create Date: 2016-08-16 19:38:29.458348

"""

# revision identifiers, used by Alembic.
revision = '3ce9cf9a604c'
down_revision = '4ffd5f98d41e'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_index('uk_name_file_keyword_idx', 'github_record', ['full_name', 'file_path', 'keyword'], unique=True)
    op.drop_index('uk_full_name_file_path_idx', table_name='github_record')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_index('uk_full_name_file_path_idx', 'github_record', ['full_name', 'file_path'], unique=1)
    op.drop_index('uk_name_file_keyword_idx', table_name='github_record')
    ### end Alembic commands ###
