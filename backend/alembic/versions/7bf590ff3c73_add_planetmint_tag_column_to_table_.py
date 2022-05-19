"""Add planetmint_tag column to table projects

Revision ID: 7bf590ff3c73
Revises: 3f27a8c6fc94
Create Date: 2022-05-19 17:07:49.613511

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7bf590ff3c73'
down_revision = '3f27a8c6fc94'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('projects', sa.Column('planetmint_tag', sa.String(), nullable=True))
    op.create_index(op.f('ix_projects_planetmint_tag'), 'projects', ['planetmint_tag'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_projects_planetmint_tag'), table_name='projects')
    op.drop_column('projects', 'planetmint_tag')

