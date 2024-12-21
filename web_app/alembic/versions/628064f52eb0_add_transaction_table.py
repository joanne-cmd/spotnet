"""add transaction table

Revision ID: 628064f52eb0
Revises: cda4342b007d
Create Date: 2024-12-14 14:13:07.042305

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "628064f52eb0"
down_revision = "cda4342b007d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """ commands auto generated by Alembic - please adjust! """
    op.create_table(
        "transaction",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("position_id", sa.UUID(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("opened", "closed", name="transaction_status_enum"),
            nullable=False,
        ),
        sa.Column("transaction_hash", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["position_id"],
            ["position.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_transaction_position_id"), "transaction", ["position_id"], unique=False
    )
    op.create_index(
        op.f("ix_transaction_transaction_hash"),
        "transaction",
        ["transaction_hash"],
        unique=True,
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """ commands auto generated by Alembic - please adjust! """
    op.drop_index(op.f("ix_transaction_transaction_hash"), table_name="transaction")
    op.drop_index(op.f("ix_transaction_position_id"), table_name="transaction")
    op.drop_table("transaction")
    # ### end Alembic commands ###
