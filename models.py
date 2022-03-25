"""Models for nba betting app."""

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()
db = SQLAlchemy()

class Team(db.Model):
    """model for nba team"""

    __tablename__ = "teams"

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    code = db.Column(db.Text, nullable=False)
    city = db.Column(db.Text, nullable=False)
    logo = db.Column(db.Text)

    players = db.relationship('Player', secondary = 'player_teams', backref = 'teams')

class PlayerTeam(db.Model):
    __tablename__ = "player_teams"

    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'), primary_key=True)

class Player(db.Model):
    """model for player on nba team"""

    __tablename__ = "players"

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    first_name = db.Column(db.Text, nullable=False)
    last_name = db.Column(db.Text, nullable=False)
    birth = db.Column(db.Text)
    college = db.Column(db.Text)
    height = db.Column(db.Float)
    weight = db.Column(db.Float)
   
    playerstats = db.relationship('PlayerStat', backref = "players")
    games = db.relationship('Game', secondary = 'player_stats', backref = 'players')
class Game(db.Model):
    """model for nba game"""

    __tablename__ = "games"

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    arena = db.Column(db.Text)
    date = db.Column(db.Text)
    home_score = db.Column(db.Integer)
    visitor_score = db.Column(db.Integer)
    home_name = db.Column(db.Text)
    visitor_name = db.Column(db.Text)

    playerstats = db.relationship('PlayerStat', backref = "games")
    bets = db.relationship('Bet', backref = "games")

class PlayerStat(db.Model):
    """model for player statistics"""

    __tablename__  = "player_stats"

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    points = db.Column(db.Integer)
    rebounds = db.Column(db.Integer)
    assists = db.Column(db.Integer)
    steals = db.Column(db.Integer)
    blocks = db.Column(db.Integer)
    team_name = db.Column(db.Text)
    team_logo = db.Column(db.Text)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'))
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'))

class Odd(db.Model):
    """ model for odds for specific game"""

    __tablename__ = "odds"

    id = db.Column(db.Text, nullable=False, primary_key=True)
    date = db.Column(db.Text, nullable=False)
    home_name = db.Column(db.Text, nullable=False)
    visitor_name = db.Column(db.Text, nullable=False)
    home_spread = db.Column(db.Float, nullable=False)
    visitor_spread = db.Column(db.Float, nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'))

class Bet(db.Model):
    """model for user bet """

    __tablename__ = "bets"

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    user = db.Column(db.Text, db.ForeignKey('users.username'))
    team_bet = db.Column(db.Text, nullable=False)
    team_spread = db.Column(db.Float, nullable=False)
    wager = db.Column(db.Integer, nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'))
class User(db.Model):
    __tablename__ = "users"

    username = db.Column(db.String(20), primary_key=True, unique=True,
    nullable=False)
    password = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)

    games = db.relationship('Game', secondary = 'bets', backref = 'users')
    @classmethod
    def register(cls, username, pwd, email, first_name, last_name):
        """Register user w/hashed password & return user."""

        hashed = bcrypt.generate_password_hash(pwd)
        # turn bytestring into normal (unicode utf8) string
        hashed_utf8 = hashed.decode("utf8")

        # return instance of user w/username and hashed pwd
        return cls(username=username, password=hashed_utf8, email=email, first_name=first_name, last_name=last_name)

    @classmethod
    def authenticate(cls, username, pwd):
        """Validate that user exists & password is correct.

        Return user if valid; else return False.
        """

        u = User.query.filter_by(username=username).first()

        if u and bcrypt.check_password_hash(u.password, pwd):
            # return user instance
            return u
        else:
            return False

def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    db.app = app
    db.init_app(app)


    