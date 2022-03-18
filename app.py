from flask import Flask, redirect, render_template, request, session
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, Team, Player, Game, PlayerStat, PlayerTeam
from sqlalchemy import or_
from functions import find_nba_teams, is_nba_game
from forms import DateForm
from datetime import datetime
from api_key import API_KEY
import requests

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///nba_app'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

connect_db(app)
db.drop_all()
db.create_all()

app.config['SECRET_KEY'] = "secret"
debug = DebugToolbarExtension(app)

headers = {
    'x-rapidapi-host': "api-nba-v1.p.rapidapi.com",
    'x-rapidapi-key': API_KEY
    }

@app.route('/')
def return_homepage():  

    response = requests.request("GET", "https://api-nba-v1.p.rapidapi.com/teams", headers=headers)
    res = response.json()
    teams = res.get("response")
    nba_teams = find_nba_teams(teams)
    
    for team in nba_teams:
        new_team = Team(id = team.get("id"), name = team.get("name"), code = team.get("code"), city = team.get("city"), logo = team.get("logo") )
        db.session.add(new_team)
        db.session.commit()
    
    querystring = {"season":"2021"}
    response = requests.request("GET", "https://api-nba-v1.p.rapidapi.com/games", headers=headers, params=querystring)
    res = response.json()
    games = res.get("response")


    for game in games:
        if(is_nba_game(game) == True):
            new_game = Game(id = game.get("id"), arena = game.get("arena").get("name"), date = game.get("date").get("start")[:10:], home_name = game.get("teams").get("home")
            .get("name"), visitor_name = game.get("teams").get("visitors").get("name"), home_score = game.get("scores").get("home").get("points"),
            visitor_score = game.get("scores").get("visitors").get("points") )
            db.session.add(new_game)
            db.session.commit()


    return render_template("index.html")

@app.route('/home')
def show_homepage():
    return render_template("index.html")

@app.route('/teams')
def show_teams():
    teams = Team.query.all()
    return render_template("teams.html", teams=teams)

@app.route('/teams/<int:id>')
def show_team_details(id):
    team = Team.query.get_or_404(id)
    querystring = {"team":f"{id}", "season":"2021"}
    response = requests.request("GET", "https://api-nba-v1.p.rapidapi.com/players", headers=headers, params=querystring)
    res = response.json()
    players = res.get("response")
    for player in players:
        if Player.query.get(player.get("id")) == None:
            new_player = Player(id = player.get("id"), first_name = player.get("firstname"), last_name = player.get("lastname"), birth = player.get("birth").get("date"),
            height = player.get("height").get("meters"), college = player.get("college"), weight = player.get("weight").get("kilograms"))
            new_player_team = PlayerTeam(team_id = id, player_id = player.get("id"))
            db.session.add(new_player_team)
            db.session.add(new_player)
            db.session.commit()

        result = PlayerTeam.query.filter(PlayerTeam.team_id == id, PlayerTeam.player_id == player.get("id")).first()
        if not result:
            new_player_team = PlayerTeam(team_id = id, player_id = player.get("id"))
            db.session.add(new_player_team)
            db.session.commit()

      
    teams_players = team.players
    teams_games = Game.query.filter(or_(Game.home_name == team.name, Game.visitor_name == team.name)).order_by(Game.date).all()

    return render_template("team_details.html", teams_players = teams_players, teams_games = teams_games)

@app.route('/games', methods = ["GET", "POST"])
def show_games():
    form = DateForm()

    if form.validate_on_submit():
        date = form.date.data
        games_dates = Game.query.filter(Game.date == date.strftime("%Y-%m-%d"))
        return render_template("games.html", date = date.strftime("%Y-%m-%d"), games_dates = games_dates)
    else:
        return render_template("game_form.html", form=form)

@app.route('/games/<int:id>')
def show_game_details(id):
    result = PlayerStat.query.filter(PlayerStat.game_id == id).first()
    if result != None and result.game_id == id:
        players_stats = PlayerStat.query.filter(PlayerStat.game_id == id)

        return render_template("player_stats.html", players_stats = players_stats)
    else:
        querystring = {"game":f"{id}"}
        response = requests.request("GET", "https://api-nba-v1.p.rapidapi.com/players/statistics", headers=headers, params=querystring)
        res = response.json()
        players = res.get("response")

        for player in players:
            new_player_stat = PlayerStat(first_name = player.get("player").get("firstname"), last_name = player.get("player").get("lastname"), 
            game_id = id, points = player.get("points"), rebounds = player.get("totReb"),
            steals = player.get("steals"), assists = player.get("assists"), blocks = player.get("blocks"))
            db.session.add(new_player_stat)
            db.session.commit()
    
        players_stats = PlayerStat.query.filter(PlayerStat.game_id == id)

        return render_template("player_stats.html", players_stats = players_stats)


   


