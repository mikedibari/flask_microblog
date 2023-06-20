"""
Populate twitter database with fake data using the SQLAlchemy ORM.
"""

import random
import string
import hashlib
import secrets
from faker import Faker
from microblog.src.models import User, Post, Comment, followers, post_likes, comment_likes, db
from microblog.src import create_app

USER_COUNT = 100
POST_COUNT = 100
COMMENT_COUNT = 100
POST_LIKE_COUNT = 400
COMMENT_LIKE_COUNT = 400
FOLLOWER_COUNT = 50

assert POST_LIKE_COUNT <= (USER_COUNT * POST_COUNT)
assert COMMENT_LIKE_COUNT <= (USER_COUNT * COMMENT_COUNT)
assert FOLLOWER_COUNT <= (USER_COUNT * USER_COUNT)


def random_passhash():
    """Get hashed and salted password of length N | 8 <= N <= 15"""
    raw = ''.join(
        random.choices(
            string.ascii_letters + string.digits + '!@#$%&', # valid pw characters
            k=random.randint(8, 15) # length of pw
        )
    )

    salt = secrets.token_hex(16)

    return hashlib.sha512((raw + salt).encode('utf-8')).hexdigest()


def truncate_tables():
    """Delete all rows from database tables"""
    db.session.execute(post_likes.delete())
    db.session.execute(comment_likes.delete())
    db.session.execute(followers.delete())
    Comment.query.delete()
    Post.query.delete()
    User.query.delete()
    db.session.commit()


def main():
    """Main driver function"""
    app = create_app()
    app.app_context().push()
    truncate_tables()
    fake = Faker()

    last_user = None  # save last user
    for _ in range(USER_COUNT):
        last_user = User(
            username=fake.unique.first_name().lower() + str(random.randint(1,255)),
            password=random_passhash()
        )
        db.session.add(last_user)

    # insert users
    db.session.commit()

    last_post = None  # save last post
    for _ in range(POST_COUNT):
        last_post = Post(
            content=fake.paragraph(nb_sentences=5, variable_nb_sentences=False),
            user_id=random.randint(last_user.id - USER_COUNT + 1, last_user.id)
        )
        db.session.add(last_post)

    # insert posts
    db.session.commit()

    last_comment = None  # save last comment
    for _ in range(COMMENT_COUNT):
        last_comment = Comment(
            content=fake.sentence(),
            user_id=random.randint(last_user.id - USER_COUNT + 1, last_user.id),
            post_id=random.randint(last_post.id - POST_COUNT + 1, last_post.id)
        )
        db.session.add(last_comment)

    # insert comments
    db.session.commit()

    user_post_pairs = set()
    while len(user_post_pairs) < POST_LIKE_COUNT:

        candidate = (
            random.randint(last_user.id - USER_COUNT + 1, last_user.id),
            random.randint(last_post.id - POST_COUNT + 1, last_post.id)
        )

        if candidate in user_post_pairs:
            continue  # pairs must be unique

        user_post_pairs.add(candidate)

    new_post_likes = [{"user_id": pair[0], "post_id": pair[1]} for pair in list(user_post_pairs)]
    insert_post_likes_query = post_likes.insert().values(new_post_likes)
    db.session.execute(insert_post_likes_query)

    # insert post likes
    db.session.commit()

    user_comment_pairs = set()
    while len(user_comment_pairs) < COMMENT_LIKE_COUNT:

        candidate = (
            random.randint(last_user.id - USER_COUNT + 1, last_user.id),
            random.randint(last_comment.id - COMMENT_COUNT + 1, last_comment.id)
        )

        if candidate in user_comment_pairs:
            continue  # pairs must be unique

        user_comment_pairs.add(candidate)

    new_comment_likes = [{"user_id": pair[0], "comment_id": pair[1]} for pair in list(user_comment_pairs)]
    insert_comment_likes_query = comment_likes.insert().values(new_comment_likes)
    db.session.execute(insert_comment_likes_query)

    # insert comment likes
    db.session.commit()

    user_follower_pairs = set()
    while len(user_follower_pairs) < FOLLOWER_COUNT:

        candidate = (
            random.randint(last_user.id - USER_COUNT + 1, last_user.id),
            random.randint(last_user.id - FOLLOWER_COUNT + 1, last_user.id)
        )

        if candidate in user_follower_pairs or candidate[1] - candidate[0] == 0:
            continue  # pairs must be unique

        user_follower_pairs.add(candidate)

    new_followers = [{"user_id": pair[0], "follower_id": pair[1]} for pair in list(user_follower_pairs)]
    insert_followers_query = followers.insert().values(new_followers)
    db.session.execute(insert_followers_query)

    # insert followers
    db.session.commit()


# run script
main()
