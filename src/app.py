import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Character, Planet, Favorite

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///./instance/mydatabase.db"
    instance_path = os.path.join(app.root_path, 'instance')
    os.makedirs(instance_path, exist_ok=True)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

@app.route('/')
def sitemap():
    return generate_sitemap(app)

def get_current_user_id():
    return 1

@app.route('/people', methods=['GET'])
def all_people():
    people = Character.query.all()
    if not people:
        return jsonify([]), 200
    serialized_people = [person.serialize() for person in people]
    return jsonify(serialized_people), 200

@app.route('/people/<int:people_id>', methods=['GET'])
def get_person(people_id):
    person = Character.query.get(people_id)
    if person is None:
        raise APIException(f"Person with id {people_id} not found", status_code=404)
    return jsonify(person.serialize()), 200

@app.route('/planets', methods=['GET'])
def all_planets():
    planets = Planet.query.all()
    if not planets:
        return jsonify([]), 200
    serialized_planets = [planet.serialize() for planet in planets]
    return jsonify(serialized_planets), 200

@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if planet is None:
        raise APIException(f"Planet with id {planet_id} not found", status_code=404)
    return jsonify(planet.serialize()), 200

@app.route('/users', methods=['GET'])
def all_users():
    users = User.query.all()
    if not users:
        return jsonify([]), 200
    serialized_users = [user.serialize() for user in users]
    return jsonify(serialized_users), 200

@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():
    current_user_id = get_current_user_id()
    user = User.query.get(current_user_id)
    if user is None:
        raise APIException(f"User with id {current_user_id} not found", status_code=404)

    favorites = user.favorites
    if not favorites:
        return jsonify([]), 200
    serialized_favorites = [fav.serialize() for fav in favorites]
    return jsonify(serialized_favorites), 200

@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    current_user_id = get_current_user_id()
    planet = Planet.query.get(planet_id)
    if planet is None:
        raise APIException(f"Planet with id {planet_id} not found", status_code=404)
    user = User.query.get(current_user_id)
    if user is None:
         raise APIException(f"User with id {current_user_id} not found", status_code=404)

    existing = Favorite.query.filter_by(user_id=current_user_id, planet_id=planet_id).first()
    if existing:
         return jsonify({"message": "Favorite planet already exists"}), 409

    new_favorite = Favorite(user_id=current_user_id, planet_id=planet_id)
    try:
        db.session.add(new_favorite)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error adding favorite planet DB: {e}")
        raise APIException("Database error adding favorite", status_code=500)

    return jsonify({"message": "Favorite planet added", "favorite": new_favorite.serialize()}), 201

@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_person(people_id):
    current_user_id = get_current_user_id()
    person = Character.query.get(people_id)
    if person is None:
        raise APIException(f"Person with id {people_id} not found", status_code=404)
    user = User.query.get(current_user_id)
    if user is None:
         raise APIException(f"User with id {current_user_id} not found", status_code=404)

    existing = Favorite.query.filter_by(user_id=current_user_id, character_id=people_id).first()
    if existing:
         return jsonify({"message": "Favorite person already exists"}), 409

    new_favorite = Favorite(user_id=current_user_id, character_id=people_id)
    try:
        db.session.add(new_favorite)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error adding favorite person DB: {e}")
        raise APIException("Database error adding favorite", status_code=500)

    return jsonify({"message": "Favorite person added", "favorite": new_favorite.serialize()}), 201

@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_planet_favorite(planet_id):
    current_user_id = get_current_user_id()
    favorite = Favorite.query.filter_by(user_id=current_user_id, planet_id=planet_id).first()
    if favorite is None:
        raise APIException("Favorite planet not found for this user", status_code=404)

    try:
        db.session.delete(favorite)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting favorite planet DB: {e}")
        raise APIException("Database error deleting favorite", status_code=500)

    return jsonify({"message": "Favorite planet deleted"}), 200

@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_person_favorite(people_id):
    current_user_id = get_current_user_id()
    favorite = Favorite.query.filter_by(user_id=current_user_id, character_id=people_id).first()
    if favorite is None:
        raise APIException("Favorite person not found for this user", status_code=404)

    try:
        db.session.delete(favorite)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting favorite person DB: {e}")
        raise APIException("Database error deleting favorite", status_code=500)

    return jsonify({"message": "Favorite person deleted"}), 200

if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)