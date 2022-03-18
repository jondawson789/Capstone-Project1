"""Models for nba betting app."""

from flask_sqlalchemy import SQLAlchemy

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


class PlayerStat(db.Model):
    """model for player statistics"""

    __tablename__  = "player_stats"

    id = db.Column(db.Integer, nullable=False, primary_key=True)
    points = db.Column(db.Integer)
    rebounds = db.Column(db.Integer)
    assists = db.Column(db.Integer)
    steals = db.Column(db.Integer)
    blocks = db.Column(db.Integer)
    first_name = db.Column(db.Text)
    last_name = db.Column(db.Text)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'))

def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    db.app = app
    db.init_app(app)


    