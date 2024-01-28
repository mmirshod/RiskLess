from flask_sqlalchemy import SQLAlchemy

from validators import validate_user
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


def setup_db(app, mode: str = None):
    """
    setup_db(app)
        binds a flask application and a SQLAlchemy service
    """
    with app.app_context():
        if mode is None:
            app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///opendata.db'
        app.config['SQLALCHEMY_NOTIFICATIONS'] = False
        db.app = app
        db.init_app(app)
        with app.app_context():
            db.create_all()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    first_name = db.Column(db.String(120), nullable=False)
    last_name = db.Column(db.String())
    password_hash = db.Column(db.String(), nullable=False)
    occupation = db.Column(db.String(120))
    place_of_work = db.Column(db.String(120))
    purpose = db.Column(db.String(120))

    @staticmethod
    def create(first_name, last_name, email, password, occupation, place_of_work, purpose):
        """Create New User"""

        if not validate_user(first_name=first_name, email=email, password=password):
            raise AuthError("Invalid Credentials")

        existing_user = User.get_by_email(email)
        if existing_user:
            raise AuthError("Email already registered")

        user = User()
        user.email = email
        user.first_name = first_name
        user.last_name = last_name
        user.password_hash = generate_password_hash(password=password)
        user.occupation = occupation
        user.place_of_work = place_of_work
        user.purpose = purpose

        db.session.add(user)
        db.session.commit()
        return True

    @staticmethod
    def get_by_id(user_id):
        res = db.session.execute(db.select(User).where(User.id == user_id)).fetchone()
        if res:
            return res[0]
        else:
            return None

    @staticmethod
    def get_by_email(email):
        res = db.session.execute(db.select(User).where(User.email == email)).fetchone()
        if res:
            user = res[0]
            return user
        return None

    def check_password(self, password):
        if not check_password_hash(self.password_hash, password):
            raise AuthError("Invalid Credentials")


class AuthError(Exception):
    def __init__(self, message="Authentication error occurred."):
        self.message = message
        super().__init__(self.message)