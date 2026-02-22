"""Add notes_shared field to Book model

Revision ID: a5ea29d70063
Revises: 83b5ab7a7eb7
Create Date: 2026-02-22 17:41:49.800908

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a5ea29d70063'
down_revision = '83b5ab7a7eb7'
branch_labels = None
depends_on = None


def upgrade():
    # Add notes_shared column to books table
    op.add_column('books', sa.Column('notes_shared', sa.Boolean(), nullable=False, server_default='false'))

    # Add check constraint to ensure notes_shared requires is_shared
    op.create_check_constraint(
        'notes_shared_requires_is_shared',
        'books',
        'NOT notes_shared OR is_shared'
    )


def downgrade():
    # Drop check constraint
    op.drop_constraint('notes_shared_requires_is_shared', 'books', type_='check')

    # Drop notes_shared column
    op.drop_column('books', 'notes_shared')
