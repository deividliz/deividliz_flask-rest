from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Integer
from typing import List, Optional
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(80), nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    apellido: Mapped[str] = mapped_column(String(100), nullable=False)

    favorites: Mapped[List["Favorite"]] = relationship(back_populates="user")

    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "nombre": self.nombre,
            "apellido": self.apellido,
            "favorites": [fav.serialize_basic() for fav in self.favorites]
        }

class Planet(db.Model):
    __tablename__ = 'planet'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    climate: Mapped[str] = mapped_column(String(250), nullable=True)
    terrain: Mapped[str] = mapped_column(String(250), nullable=True)
    population: Mapped[int] = mapped_column(Integer, nullable=True)
    favorites: Mapped[List["Favorite"]] = relationship(back_populates="planet")
    characters: Mapped[List["Character"]] = relationship(back_populates="homeworld")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "climate": self.climate,
            "terrain": self.terrain,
            "population": self.population,
            "character_ids": [char.id for char in self.characters],
            "favorite_ids": [fav.id for fav in self.favorites]
        }

    def serialize_basic(self):
         return {
            "id": self.id,
            "name": self.name
         }

class Character(db.Model):
    __tablename__ = 'character'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    birth_year: Mapped[str] = mapped_column(String(50), nullable=True)
    gender: Mapped[str] = mapped_column(String(50), nullable=True)
    height: Mapped[int] = mapped_column(Integer, nullable=True)
    skin_color: Mapped[str] = mapped_column(String(50), nullable=True)
    eye_color: Mapped[str] = mapped_column(String(50), nullable=True)
    homeworld_id: Mapped[int] = mapped_column(ForeignKey('planet.id'), nullable=True)
    homeworld: Mapped["Planet"] = relationship(back_populates="characters")
    favorites: Mapped[List["Favorite"]] = relationship(back_populates="character")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "birth_year": self.birth_year,
            "gender": self.gender,
            "height": self.height,
            "skin_color": self.skin_color,
            "eye_color": self.eye_color,
            "homeworld_id": self.homeworld_id,
            "homeworld_name": self.homeworld.name if self.homeworld else None,
            "favorite_ids": [fav.id for fav in self.favorites]
        }

    def serialize_basic(self):
         return {
            "id": self.id,
            "name": self.name
         }

class Favorite(db.Model):
    __tablename__ = 'favorites'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)
    planet_id: Mapped[int] = mapped_column(ForeignKey('planet.id'), nullable=True)
    character_id: Mapped[int] = mapped_column(ForeignKey('character.id'), nullable=True)
    user: Mapped["User"] = relationship(back_populates="favorites")
    planet: Mapped["Planet"] = relationship(back_populates="favorites")
    character: Mapped["Character"] = relationship(back_populates="favorites")

    def serialize(self):
        return {
            "favorite_id": self.id,
            "user_id": self.user_id,
            "character_id": self.character_id,
            "planet_id": self.planet_id
        }

    def serialize_basic(self):
         return {
            "id": self.id,
            "name": self.name
         }