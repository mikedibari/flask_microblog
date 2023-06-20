import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# a user may be followed by many users; a user may follow many users
"""
CREATE TABLE followers (
    user_id INTEGER NOT NULL,
    follower_id INTEGER NOT NULL,
    PRIMARY KEY (user_id, follower_id),
    FOREIGN KEY(user_id) REFERENCES users (id),
    FOREIGN KEY(follower_id) REFERENCES users (id)
);
"""
followers = db.Table('followers', 
     db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True), 
     db.Column('follower_id', db.Integer, db.ForeignKey('users.id'), primary_key=True)
)
# class Follower(db.Model):
#     __tablename__ = 'followers' 
#     user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True) 
#     follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    # user_follows = db.relationship('User', back_populates='followers')
    
# an user may write many posts; a post must be written by one user
"""
CREATE TABLE users (
	id SERIAL PRIMARY KEY,
	username VARCHAR(80) NOT NULL UNIQUE,
	password VARCHAR(80) NOT NULL,
	ON DELETE CASCADE
);
"""

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(160), unique=True, nullable=False)
    password = db.Column(db.String(160), nullable=False)
    posts = db.relationship('Post', backref='user', cascade="all,delete")
    comments = db.relationship('Comment', backref='user', cascade="all,delete")
    
    # may need backref for followers

    # user_followers = db.relationship('Follower', back_populates='users')

    # user_followers = db.relationship(
    #     'User', secondary=followers, lazy='subquery',
    #     primaryjoin = id == followers.c.user_id, 
    #     secondaryjoin = id == followers.c.follower_id, 
    #     backref=db.backref('user_follows', lazy=True)
    # )

    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        
    def serialize(self):
        return {
            'id': self.id,
            'username': self.username
        }

# an user may like many posts; a post may be liked by many users
"""
CREATE TABLE post_likes (
	user_id INTEGER NOT NULL,
	post_id INTEGER NOT NULL,
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
	PRIMARY KEY (user_id, post_id),
    FOREIGN KEY(post_id) REFERENCES posts (id),
    FOREIGN KEY(user_id) REFERENCES users (id)
);
"""

post_likes = db.Table('post_likes', 
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True), 
    db.Column('post_id', db.Integer, db.ForeignKey('posts.id'), primary_key=True),
    db.Column(
        'created_at', db.DateTime, 
        default=datetime.datetime.utcnow, nullable=False)
)

"""
CREATE TABLE posts (
	id SERIAL PRIMARY KEY,
	content VARCHAR(5000) NOT NULL,
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
	user_id INT NOT NULL,
	CONSTRAINT fk_comments_tweets
	FOREIGN KEY (user_id) REFERENCES users
);
"""

class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.String(5000), nullable=False)
    created_at = db.Column(
        db.DateTime, default=datetime.datetime.utcnow, 
        nullable=False
    )
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    comments = db.relationship('Comment', backref='post', lazy=True)
    liking_users = db.relationship(
        'User', secondary=post_likes, lazy='subquery', 
        backref=db.backref('liked_posts', lazy=True)
    )

    def __init__(self, content: str, user_id: int):
        self.content = content
        self.user_id = user_id

    def serialize(self):
        return {
            'id': self.id,
            'content': self.content,
            'created_at': self.created_at.isoformat(),
            'user_id': self.user_id
        }

# a user may like many comments; a comment may be liked by many users 
"""
CREATE TABLE comment_likes (
    user_id INTEGER NOT NULL,
    comment_id INTEGER NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    PRIMARY KEY (user_id, comment_id),
    FOREIGN KEY(comment_id) REFERENCES comments (id),
    FOREIGN KEY(user_id) REFERENCES users (id)
);
"""

comment_likes = db.Table('comment_likes', 
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True), 
    db.Column('comment_id', db.Integer, db.ForeignKey('comments.id'), primary_key=True),
    db.Column(
        'created_at', db.DateTime, 
        default=datetime.datetime.utcnow, nullable=False)
)

# a post may have many comments; a comment must relate to one post
# an user may write many comments; a comment must be written by one user
"""
CREATE TABLE comments (
    id SERIAL NOT NULL,
    content VARCHAR(600) NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    user_id INTEGER NOT NULL,
    post_id INTEGER NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY(post_id) REFERENCES posts (id),
    FOREIGN KEY(user_id) REFERENCES users (id)
);
"""

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.String(600), nullable=False)
    created_at = db.Column(
        db.DateTime, default=datetime.datetime.utcnow, 
        nullable=False
    )    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    liking_users = db.relationship(
        'User', secondary=comment_likes, lazy='subquery', 
        backref=db.backref('liked_comments', lazy=True)
    )

    def __init__(self, content: str, user_id: int, post_id: int):
        self.content = content
        self.user_id = user_id
        self.post_id = post_id

    def serialize(self):
        return {
            'id': self.id,
            'content': self.content,
            'created_at': self.created_at.isoformat(),
            'user_id': self.user_id,
            'post_id': self.post_id
        }
