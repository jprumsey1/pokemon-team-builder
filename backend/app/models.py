"""ORM data models.

Assumptions:
  * `pokemon.id` is PokeAPI's own id, not a surrogate key. Other tables use a generated surrogate key.
  * `type_1` / `type_2` make 3+ unrepresentable in the database. We assume a Pokemon has 1-2 types.
  * `team_pokemon` is a many-to-many mapping table keyed on `(team_id, position)`, so ordering is enforced by the database.
"""

from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    MetaData,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

# Deterministic constraint/index names. Without this Postgres invents them, and
# Alembic autogenerate then emits migrations that can't reliably drop what it made.
NAMING_CONVENTION = {
    "ix": "ix_%(table_name)s_%(column_0_name)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    teams: Mapped[list[Team]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class Pokemon(Base):
    """PokeAPI Pokemon data. 
    
    Refreshed by background process only when something actually changed."""

    __tablename__ = "pokemon"

    # PokéAPI's id: 1–1025 are base forms, 10001+ are variants.
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    name: Mapped[str] = mapped_column(String(100), index=True)

    # Used to groups variants with their base form in app (charizard, charizard-mega-x)
    species_id: Mapped[int] = mapped_column(Integer, index=True)
    is_default: Mapped[bool] = mapped_column(Boolean)

    type_1: Mapped[str] = mapped_column(String(20), index=True)
    type_2: Mapped[str | None] = mapped_column(String(20), nullable=True, index=True)

    hp: Mapped[int] = mapped_column(Integer)
    attack: Mapped[int] = mapped_column(Integer)
    defense: Mapped[int] = mapped_column(Integer)
    special_attack: Mapped[int] = mapped_column(Integer)
    special_defense: Mapped[int] = mapped_column(Integer)
    speed: Mapped[int] = mapped_column(Integer)

    sprite_url: Mapped[str | None] = mapped_column(String(255), nullable=True)


class Team(Base):
    __tablename__ = "team"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user: Mapped[User] = relationship(back_populates="teams")
    members: Mapped[list[TeamPokemon]] = relationship(
        back_populates="team",
        cascade="all, delete-orphan",
        # Only takes effect alongside ondelete="CASCADE" on the FK; both needed.
        passive_deletes=True,
        order_by="TeamPokemon.position",
    )


class TeamPokemon(Base):
    """Team members with ordering (`position`). The composite primary key is the ordering guarantee."""

    __tablename__ = "team_pokemon"
    __table_args__ = (Index("ix_team_pokemon_pokemon_id", "pokemon_id"),)

    team_id: Mapped[int] = mapped_column(
        ForeignKey("team.id", ondelete="CASCADE"), primary_key=True
    )
    # Part of the primary key, guarantees no two Pokémon occupy the same slot.
    position: Mapped[int] = mapped_column(Integer, primary_key=True)
    pokemon_id: Mapped[int] = mapped_column(ForeignKey("pokemon.id"))

    team: Mapped[Team] = relationship(back_populates="members")
    pokemon: Mapped[Pokemon] = relationship(lazy="joined")


class PokemonChangeEvent(Base):
    """One row per Pokémon per sweep in which at least one field differed.

    `changes` is a list of {`field`, `from`, `to`}. This is the change log.
    """

    __tablename__ = "pokemon_change_event"
    __table_args__ = (Index("ix_pce_detected_at", "detected_at"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    pokemon_id: Mapped[int] = mapped_column(
        ForeignKey("pokemon.id", ondelete="CASCADE"), index=True
    )
    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    changes: Mapped[list[dict]] = mapped_column(JSONB)

    pokemon: Mapped[Pokemon] = relationship()


class TypeMatchup(Base):
    """The 18x18 type chart initially seeded from PokéAPI"""

    __tablename__ = "type_matchup"

    attacking_type: Mapped[str] = mapped_column(String(20), primary_key=True)
    defending_type: Mapped[str] = mapped_column(String(20), primary_key=True)
    # Float is exact here: every multiplier is 0, 1/2, 1 or 2, and so is every product.
    multiplier: Mapped[float] = mapped_column(Float)
