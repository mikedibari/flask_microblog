import itertools
from flask import Blueprint, jsonify, abort, request
from ..models import Post, User, db

bp = Blueprint('posts', __name__, url_prefix='/posts')

# SELECT * FROM posts ORDER BY id DESC LIMIT 20;
@bp.route('', methods=['GET'])
def index():
    posts = Post.query.all() 
    result = []
    for p in itertools.islice(reversed(posts), 20):
        result.append(p.serialize())
    return jsonify(result)

