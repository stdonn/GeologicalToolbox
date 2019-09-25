"""Initial Database

Revision ID: cb4184696326
Revises: 
Create Date: 2019-09-24 15:26:52.159736

"""
from alembic import op
import sqlalchemy as sq


# revision identifiers, used by Alembic.
revision = 'cb4184696326'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('stratigraphy',
    sq.Column('id', sq.INTEGER(), nullable=False),
    sq.Column('unit_name', sq.VARCHAR(length=50), nullable=True),
    sq.Column('age', sq.FLOAT(), nullable=True),
    sq.PrimaryKeyConstraint('id'),
    sq.UniqueConstraint('unit_name')
    )
    op.create_table('wells',
    sq.Column('name_col', sq.VARCHAR(length=100), nullable=True),
    sq.Column('comment_col', sq.VARCHAR(length=100), nullable=True),
    sq.Column('east', sq.FLOAT(), nullable=True),
    sq.Column('north', sq.FLOAT(), nullable=True),
    sq.Column('alt', sq.FLOAT(), nullable=True),
    sq.Column('reference', sq.TEXT(), nullable=True),
    sq.Column('id', sq.INTEGER(), nullable=False),
    sq.Column('drill_depth', sq.FLOAT(), nullable=True),
    sq.Column('wellname', sq.VARCHAR(length=100), nullable=True),
    sq.Column('shortwellname', sq.VARCHAR(length=100), nullable=True),
    sq.PrimaryKeyConstraint('id'),
    sq.UniqueConstraint('wellname')
    )
    op.create_table('lines',
    sq.Column('name_col', sq.VARCHAR(length=100), nullable=True),
    sq.Column('comment_col', sq.VARCHAR(length=100), nullable=True),
    sq.Column('id', sq.INTEGER(), nullable=False),
    sq.Column('closed', sq.BOOLEAN(), nullable=True),
    sq.Column('horizon_id', sq.INTEGER(), nullable=True),
    sq.ForeignKeyConstraint(['horizon_id'], ['stratigraphy.id'], ),
    sq.PrimaryKeyConstraint('id')
    )
    op.create_table('well_logs',
    sq.Column('name_col', sq.VARCHAR(length=100), nullable=True),
    sq.Column('comment_col', sq.VARCHAR(length=100), nullable=True),
    sq.Column('prop_name', sq.VARCHAR(length=50), nullable=True),
    sq.Column('prop_unit', sq.VARCHAR(length=100), nullable=True),
    sq.Column('id', sq.INTEGER(), nullable=False),
    sq.Column('well_id', sq.INTEGER(), nullable=True),
    sq.ForeignKeyConstraint(['well_id'], ['wells.id'], ),
    sq.PrimaryKeyConstraint('id')
    )
    op.create_table('well_marker',
    sq.Column('name_col', sq.VARCHAR(length=100), nullable=True),
    sq.Column('comment_col', sq.VARCHAR(length=100), nullable=True),
    sq.Column('id', sq.INTEGER(), nullable=False),
    sq.Column('drill_depth', sq.FLOAT(), nullable=True),
    sq.Column('horizon_id', sq.INTEGER(), nullable=True),
    sq.Column('well_id', sq.INTEGER(), nullable=True),
    sq.ForeignKeyConstraint(['horizon_id'], ['stratigraphy.id'], ),
    sq.ForeignKeyConstraint(['well_id'], ['wells.id'], ),
    sq.PrimaryKeyConstraint('id')
    )
    op.create_table('geopoints',
    sq.Column('name_col', sq.VARCHAR(length=100), nullable=True),
    sq.Column('comment_col', sq.VARCHAR(length=100), nullable=True),
    sq.Column('east', sq.FLOAT(), nullable=True),
    sq.Column('north', sq.FLOAT(), nullable=True),
    sq.Column('alt', sq.FLOAT(), nullable=True),
    sq.Column('reference', sq.TEXT(), nullable=True),
    sq.Column('id', sq.INTEGER(), nullable=False),
    sq.Column('has_z', sq.BOOLEAN(), nullable=True),
    sq.Column('horizon_id', sq.INTEGER(), nullable=True),
    sq.Column('line_id', sq.INTEGER(), nullable=True),
    sq.Column('line_pos', sq.INTEGER(), nullable=True),
    sq.ForeignKeyConstraint(['horizon_id'], ['stratigraphy.id'], ),
    sq.ForeignKeyConstraint(['line_id'], ['lines.id'], ),
    sq.PrimaryKeyConstraint('id')
    )
    op.create_table('logging_association',
    sq.Column('name_col', sq.VARCHAR(length=100), nullable=True),
    sq.Column('comment_col', sq.VARCHAR(length=100), nullable=True),
    sq.Column('id', sq.INTEGER(), nullable=False),
    sq.Column('log_depth', sq.FLOAT(), nullable=True),
    sq.Column('log_value', sq.FLOAT(), nullable=True),
    sq.Column('log_id', sq.INTEGER(), nullable=True),
    sq.ForeignKeyConstraint(['log_id'], ['well_logs.id'], ),
    sq.PrimaryKeyConstraint('id')
    )
    op.create_index('welllogdepth_index', 'logging_association', ['log_depth'], unique=False)
    op.create_table('properties',
    sq.Column('name_col', sq.VARCHAR(length=100), nullable=True),
    sq.Column('comment_col', sq.VARCHAR(length=100), nullable=True),
    sq.Column('prop_name', sq.VARCHAR(length=50), nullable=True),
    sq.Column('prop_unit', sq.VARCHAR(length=100), nullable=True),
    sq.Column('id', sq.INTEGER(), nullable=False),
    sq.Column('point_id', sq.INTEGER(), nullable=True),
    sq.Column('prop_value', sq.TEXT(), nullable=True),
    sq.Column('prop_type', sq.VARCHAR(length=20), nullable=True),
    sq.ForeignKeyConstraint(['point_id'], ['geopoints.id'], ),
    sq.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('properties')
    op.drop_index('welllogdepth_index', table_name='logging_association')
    op.drop_table('logging_association')
    op.drop_table('geopoints')
    op.drop_table('well_marker')
    op.drop_table('well_logs')
    op.drop_table('lines')
    op.drop_table('wells')
    op.drop_table('stratigraphy')
    # ### end Alembic commands ###
