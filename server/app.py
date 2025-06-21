#!/usr/bin/env python3

from flask import Flask, request, make_response, jsonify
from flask_migrate import Migrate

from models import db, Bakery, BakedGood

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def home():
    return '<h1>Bakery GET-POST-PATCH-DELETE API</h1>'

@app.route('/bakeries')
def bakeries():
    bakeries = [bakery.to_dict() for bakery in Bakery.query.all()]
    return make_response(  bakeries,   200  )

@app.route('/bakeries/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
def bakery_by_id(id):
    bakery = Bakery.query.get(id)
    if not bakery:
        return jsonify({"error": "Review not found"}), 404
    if request.method == 'GET':
        return jsonify(bakery.to_dict()), 200
    elif request.method == 'PATCH':
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON"}), 400

        for attr, value in data.items():
            setattr(bakery, attr, value)
        db.session.commit()
        return jsonify(bakery.to_dict()), 200
    elif request.method == 'DELETE':
        db.session.delete(bakery)
        db.session.commit()
        return jsonify({"message": "Bakery deleted"}), 200
  
@app.route('/baked_goods', methods=['POST'])
def create_baked_goods():
    data = request.get_json ()
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400
    
    new_baked = BakedGood(
        name=data.get("name"),
        price=data.get("price"),
        bakery_id=data.get("bakery_id"),
    )
    db.session.add(new_baked)
    db.session.commit()
    
    return jsonify(new_baked.to_dict()), 201

@app.route('/baked_goods/<int:id>', methods=['DELETE'])
def delete_baked_good(id):
    baked_good = BakedGood.query.get(id)
    if not baked_good:
        return jsonify({"error": "Baked good not found"}), 404

    db.session.delete(baked_good)
    db.session.commit()
    return jsonify({"message": "Baked good deleted"}), 200


@app.route('/baked_goods/most_expensive')
def most_expensive_baked_good():
    most_expensive = BakedGood.query.order_by(BakedGood.price.desc()).limit(1).first()
    most_expensive_serialized = most_expensive.to_dict()
    return make_response( most_expensive_serialized,   200  )

if __name__ == '__main__':
    app.run(port=5555, debug=True)