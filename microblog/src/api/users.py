import itertools
from flask import Blueprint, jsonify, abort, request
from ..models import User, db, Post

bp = Blueprint('users', __name__, url_prefix='/users')

# SELECT * FROM users ORDER BY id DESC LIMIT 30;
@bp.route('', methods=['GET'])
def index():
    users = User.query.all()
    result = []
    for u in itertools.islice(reversed(users), 30):
        result.append(u.serialize())
    return jsonify(result)

@bp.route('/<int:id>/posts', methods=['GET'])
def posts(id: int):
    User.query.get_or_404(id)
    result = []
    engine = db.get_engine()
    with engine.connect() as conn:
        rows = conn.execute(
            '''SELECT u.username, p.content 
               FROM users u 
               JOIN posts p ON u.id = p.user_id 
               WHERE u.id = %s;''', (id)
            )
        for r in rows:
            result.append({'username': r[0], 'content': r[1]})
    return jsonify(result)

# @bp.route('/<int:id>/posts', methods=['GET'])
# def posts(id):
#     result = []
#     posts = Post.query.filter_by(user_id=id)
#     for p in posts:
#         result.append(p.serialize())
#     return jsonify(result)

@bp.route('/<int:id>/followers', methods=['GET'])
def followers(id: int):
    User.query.get_or_404(id)
    result = []
    engine = db.get_engine()
    with engine.connect() as conn:
        rows = conn.execute(
            '''SELECT uf.username 
               FROM users u
               JOIN followers f ON u.id = f.user_id
               JOIN users uf ON uf.id = f.follower_id
               WHERE u.id = %s;''', (id)
            )
        for r in rows:
            result.append({'username': r[0]})
    return jsonify(result)
