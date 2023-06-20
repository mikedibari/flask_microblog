import itertools
from flask import Blueprint, jsonify, abort, request
from ..models import Comment, Post, User, db

bp = Blueprint('comments', __name__, url_prefix='/comments')

# SELECT * FROM comments LIMIT 10
@bp.route('', methods=['GET'])
def index():
    comments = Comment.query.all() 
    result = []
    for c in itertools.islice(comments, 10):
        result.append(c.serialize())
    return jsonify(result)

# SELECT * FROM comments WHERE post_id = id;
@bp.route('/<int:id>/post', methods=['GET'])
def post(id: int):
    Comment.query.get_or_404(id)
    result = []
    comments = Comment.query.filter_by(post_id=id)    
    for c in comments:
        result.append(c.serialize())
    return jsonify(result)
