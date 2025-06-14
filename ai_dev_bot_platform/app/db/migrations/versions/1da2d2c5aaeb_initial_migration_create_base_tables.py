"""Initial migration, create base tables

Revision ID: 1da2d2c5aaeb
Revises: 
Create Date: 2025-06-13 11:24:37.341253

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1da2d2c5aaeb'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('model_pricing',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('model_provider', sa.String(length=100), nullable=False),
    sa.Column('model_name', sa.String(length=255), nullable=False),
    sa.Column('input_cost_per_million_tokens', sa.DECIMAL(precision=12, scale=6), nullable=False),
    sa.Column('output_cost_per_million_tokens', sa.DECIMAL(precision=12, scale=6), nullable=False),
    sa.Column('image_input_cost_per_image', sa.DECIMAL(precision=12, scale=6), nullable=True),
    sa.Column('image_output_cost_per_image', sa.DECIMAL(precision=12, scale=6), nullable=True),
    sa.Column('currency', sa.String(length=10), nullable=False),
    sa.Column('notes', sa.TEXT(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('model_name')
    )
    op.create_index(op.f('ix_model_pricing_id'), 'model_pricing', ['id'], unique=False)
    op.create_table('users',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('telegram_user_id', sa.BigInteger(), nullable=False),
    sa.Column('username', sa.String(length=255), nullable=True),
    sa.Column('email', sa.String(length=255), nullable=True),
    sa.Column('credit_balance', sa.DECIMAL(precision=10, scale=2), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_telegram_user_id'), 'users', ['telegram_user_id'], unique=True)
    op.create_table('projects',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=500), nullable=False),
    sa.Column('description', sa.TEXT(), nullable=True),
    sa.Column('status', sa.String(length=50), nullable=True),
    sa.Column('tech_stack', sa.JSON(), nullable=True),
    sa.Column('current_todo_markdown', sa.TEXT(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('completed_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('api_key_usage',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('project_id', sa.UUID(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('api_key_identifier', sa.String(length=100), nullable=True),
    sa.Column('model_provider', sa.String(length=100), nullable=False),
    sa.Column('model_name', sa.String(length=255), nullable=False),
    sa.Column('task_type', sa.String(length=100), nullable=True),
    sa.Column('input_tokens_used', sa.Integer(), nullable=True),
    sa.Column('output_tokens_used', sa.Integer(), nullable=True),
    sa.Column('images_processed', sa.Integer(), nullable=True),
    sa.Column('actual_cost_usd', sa.DECIMAL(precision=10, scale=6), nullable=True),
    sa.Column('response_time_ms', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_api_key_usage_id'), 'api_key_usage', ['id'], unique=False)
    op.create_table('project_files',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('project_id', sa.UUID(), nullable=False),
    sa.Column('file_path', sa.String(length=1000), nullable=False),
    sa.Column('file_type', sa.String(length=100), nullable=True),
    sa.Column('content', sa.TEXT(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('credit_transactions',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('project_id', sa.UUID(), nullable=True),
    sa.Column('api_key_usage_id', sa.Integer(), nullable=True),
    sa.Column('transaction_type', sa.String(length=50), nullable=False),
    sa.Column('credits_amount', sa.DECIMAL(precision=10, scale=2), nullable=False),
    sa.Column('real_cost_associated_usd', sa.DECIMAL(precision=10, scale=6), nullable=True),
    sa.Column('external_transaction_id', sa.String(length=255), nullable=True),
    sa.Column('description', sa.TEXT(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['api_key_usage_id'], ['api_key_usage.id'], ),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_credit_transactions_id'), 'credit_transactions', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_credit_transactions_id'), table_name='credit_transactions')
    op.drop_table('credit_transactions')
    op.drop_table('project_files')
    op.drop_index(op.f('ix_api_key_usage_id'), table_name='api_key_usage')
    op.drop_table('api_key_usage')
    op.drop_table('projects')
    op.drop_index(op.f('ix_users_telegram_user_id'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_model_pricing_id'), table_name='model_pricing')
    op.drop_table('model_pricing')
    # ### end Alembic commands ###