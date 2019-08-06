from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_marshmallow import Marshmallow
from flask_heroku import Heroku
import os

app = Flask(__name__)
heroku = Heroku(app)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + \
    os.path.join(basedir, "app.sqlite")

CORS(app)

db = SQLAlchemy(app)
ma = Marshmallow(app)


class Meme(db.Model):
    __tablename__ = "memes"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(50))
    image = db.Column(db.String(500))
    favorite = db.Column(db.Boolean)

    def __init__(self, text, image, favorite):
        self.text = text
        self.image = image
        self.favorite = favorite


class MemeSchema(ma.Schema):
    class Meta:
        fields = ("id", "text", "image", "favorite")


meme_schema = MemeSchema()
memes_schema = MemeSchema(many=True)


@app.route("/")
def greeting():
    return "<h1>Meme API</h1>"


@app.route("/memes", methods=["GET"])
def get_memes():
    all_memes = Meme.query.all()
    result = memes_schema.dump(all_memes)
    return jsonify(result.data)


@app.route("/meme/<id>", methods=["GET"])
def get_meme(id):
    meme = Meme.query.get(id)
    return meme_schema.jsonify(meme)


@app.route("/add-meme", methods=["POST"])
def add_meme():
    text = request.json["text"]
    image = request.json["image"]
    favorite = request.json["favorite"]

    new_meme = Meme(text, image, favorite)

    db.session.add(new_meme)
    db.session.commit()

    return jsonify("MEME POSTED!")


@app.route("/meme/<id>", methods=["DELETE"])
def delete_meme(id):
    meme = Meme.query.get(id)
    db.session.delete(meme)
    db.session.commit()

    return jsonify("RECORD DELETED")


@app.route("/meme/<id>", methods=["PUT"])
def update_meme(id):
    meme = Meme.query.get(id)

    new_text = request.json["text"]
    new_favorite = request.json["favorite"]

    meme.text = new_text
    meme.favorite = new_favorite

    db.session.commit()
    return meme_schema.jsonify(meme)


if __name__ == "__main__":
    app.debug = True
    app.run()
