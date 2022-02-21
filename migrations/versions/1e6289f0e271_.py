"""empty message

Revision ID: 1e6289f0e271
Revises: 
Create Date: 2022-02-20 17:51:23.224351

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1e6289f0e271'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('employee',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('surname', sa.Integer(), nullable=True),
    sa.Column('email_address', sa.String(length=50), nullable=False),
    sa.Column('isManager', sa.Boolean(), nullable=True),
    sa.Column('national_insurance_number', sa.String(length=50), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email_address'),
    sa.UniqueConstraint('national_insurance_number')
    )
    op.create_table('guest_user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=20), nullable=False),
    sa.Column('email', sa.String(length=50), nullable=False),
    sa.Column('phone', sa.String(length=50), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('phone'),
    sa.UniqueConstraint('username')
    )
    op.create_table('hiring_place',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('address', sa.String(length=50), nullable=False),
    sa.Column('max_capacity', sa.Integer(), nullable=True),
    sa.Column('scooter_availability', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=50), nullable=False),
    sa.Column('password', sa.String(length=80), nullable=False),
    sa.Column('phone', sa.String(length=50), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('phone')
    )
    op.create_table('card__payment',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('card_holder', sa.String(length=80), nullable=False),
    sa.Column('card_number', sa.String(length=20), nullable=False),
    sa.Column('card_expiry_date', sa.DateTime(), nullable=False),
    sa.Column('card_cvv', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('card_number')
    )
    op.create_table('feedback',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('scooter_id', sa.Integer(), nullable=False),
    sa.Column('priority', sa.Integer(), nullable=True),
    sa.Column('feedback_text', sa.String(length=5000), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('scooter_id')
    )
    op.create_table('scooter',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('status', sa.Boolean(), nullable=True),
    sa.Column('real_time_location', sa.Integer(), nullable=True),
    sa.Column('location_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['location_id'], ['hiring_place.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('hire_session',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('cost', sa.Float(), nullable=True),
    sa.Column('start_date', sa.DateTime(), nullable=False),
    sa.Column('period', sa.String(length=50), nullable=False),
    sa.Column('scooter_id', sa.Integer(), nullable=False),
    sa.Column('guest_id', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['guest_id'], ['guest_user.id'], ),
    sa.ForeignKeyConstraint(['scooter_id'], ['scooter.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('hire_session')
    op.drop_table('scooter')
    op.drop_table('feedback')
    op.drop_table('card__payment')
    op.drop_table('user')
    op.drop_table('hiring_place')
    op.drop_table('guest_user')
    op.drop_table('employee')
    # ### end Alembic commands ###
