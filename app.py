from flask import Flask, redirect, render_template, request, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, Team, Player, Game, PlayerStat, PlayerTeam, User, Odd, Bet
from sqlalchemy import or_, func
from functions import find_nba_teams, is_nba_game, update_game_scores, is_player_active, is_winning_bet
from forms import DateForm, RegisterForm, LoginForm
from datetime import datetime, date
from api_key import NBA_API_KEY, ODDS_API_KEY, STRIPE_API_KEY
import requests
import stripe

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///nba_app'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

connect_db(app)
#db.drop_all()
db.create_all()

app.config['SECRET_KEY'] = "secret"
debug = DebugToolbarExtension(app)

today = date.today()
stripe.api_key = "sk_test_51KdQeLEtCEqhAcFn4fh6k2WSM2iFmfUlCdouwjTJkrFRFR5wOqGchZUHyl7y0M1C7oPik6ALjDYvoqML9wU2AriE00QOAmoNzH"
headers = {
    'x-rapidapi-host': "api-nba-v1.p.rapidapi.com",
    'x-rapidapi-key': NBA_API_KEY
    }

@app.route('/')
def return_homepage():  

    """
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
    """

    return redirect('/home')

@app.route('/home')
def show_homepage():
    if Bet.query.first() == None:
        recommend_game = Odd.query.first()
        game_id = recommend_game.game_id
        home_team = recommend_game.home_name
        visitor_team = recommend_game.visitor_name
    else:
        recommend_game = db.session.query(Bet.game_id, func.count(Bet.id)).group_by(Bet.game_id).order_by(func.count(Bet.id)).first()
        recommend_game2 = Game.query.get(recommend_game[0])
        game_id = recommend_game
        home_team = Team.query.filter(recommend_game2.home_name == Team.name).first()
        visitor_team = Team.query.filter(recommend_game2.visitor_name == Team.name).first()
    
    return render_template("homepage.html", home_team = home_team, visitor_team = visitor_team, game_id = game_id)

@app.route('/teams')
def show_teams():
    teams = Team.query.all()
    return render_template("teams.html", teams=teams)

@app.route('/teams/<int:id>')
def show_team_details(id):
    team = Team.query.get_or_404(id)

    """
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
        if not result and player.get("leagues").get("standard") != None and player.get("leagues").get("standard").get("active") == True:
            new_player_team = PlayerTeam(team_id = id, player_id = player.get("id"))
            db.session.add(new_player_team)
            db.session.commit()
    """
    
    teams_players = team.players
    teams_games = Game.query.filter(or_(Game.home_name == team.name, Game.visitor_name == team.name)).order_by(Game.date).all()
    #update_game_scores(teams_games)
    return render_template("team_details.html", teams_players = teams_players, teams_games = teams_games)

@app.route('/games', methods = ["GET", "POST"])
def show_games():
    form = DateForm()

    if form.validate_on_submit():
        date = form.date.data
        games_dates = Game.query.filter(Game.date == date.strftime("%Y-%m-%d"))
        update_game_scores(games_dates)
        return render_template("games.html", date = date.strftime("%Y-%m-%d"), games_dates = games_dates)
    else:
        return render_template("game_form.html", form=form)

@app.route('/games/<int:id>')
def show_game_details(id):
    result = PlayerStat.query.filter(PlayerStat.game_id == id).first()
    if result != None and result.game_id == id:
        players_stats = PlayerStat.query.filter(PlayerStat.game_id == id)

    else:
        querystring = {"game":f"{id}"}
        response = requests.request("GET", "https://api-nba-v1.p.rapidapi.com/players/statistics", headers=headers, params=querystring)
        res = response.json()
        players = res.get("response")

        for player in players:
            new_player_stat = PlayerStat( player_id = player.get("player").get("id"),
            team_name = player.get("team").get("name"), team_logo = player.get("team").get("logo"), 
            game_id = id, points = player.get("points"), rebounds = player.get("totReb"),
            steals = player.get("steals"), assists = player.get("assists"), blocks = player.get("blocks"))
            db.session.add(new_player_stat)
            db.session.commit()
    
        players_stats = PlayerStat.query.filter(PlayerStat.game_id == id)

    return render_template("player_stats.html", players_stats = players_stats)

#------------------------------------------------------------------------------------------------------------------------
@app.route('/register', methods = ["GET", "POST"])
def register_user():
    form = RegisterForm()

    if form.validate_on_submit():
        username = form.username.data 
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        new_user = User.register(username, password, email, first_name, last_name)
        db.session.add(new_user)
        db.session.commit()
        session['username'] = new_user.username
        return redirect('/login')
    else:
        return render_template("register.html", form=form)

@app.route('/login', methods = ["GET", "POST"])
def login_user():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data 
        password = form.password.data
        user = User.authenticate(username, password)
        if user:
            session['username'] = user.username
            return redirect(f'/home')
            form.username.errors = ['Invalid username/password']
    return render_template("login.html", form=form)

@app.route('/logout')
def logout_user():
    session.pop('username')
    return redirect('/home')

#---------------------------------------------------------------------------------------------

@app.route('/bet')
def show_odds():
    
    """
    response = requests.request("GET", f"https://api.the-odds-api.com/v4/sports/basketball_nba/odds/?regions=us&markets=spreads&apiKey={ODDS_API_KEY}")
    games = response.json()
    for game in games:
        id = game.get("id")
        date = game.get("commence_time")[:10:]
        home_name = game.get("home_team")
        visitor_name = game.get("away_team")
        
        bookmakers = game.get("bookmakers")
        for bookmaker in bookmakers:
            if bookmaker.get("key") == "draftkings":
                markets = bookmaker.get("markets")
                for market in markets:
                    outcomes = markets[0].get("outcomes")
                    home_spread = outcomes[0].get("point")
                    visitor_spread = outcomes[1].get("point")
        game_id = Game.query.filter(Game.date == date, Game.home_name == home_name).first().id
        new_game_odds = Odd(id = id, date = date, home_name = home_name, visitor_name = visitor_name, home_spread = home_spread, visitor_spread = visitor_spread,
        game_id = game_id)
        db.session.add(new_game_odds)
        db.session.commit()
    """

    if "username"  not in session:
        flash("you must log in to bet")
        return redirect('/home')
    odds = Odd.query.all()
    return render_template("bet.html", odds = odds)

@app.route('/charge', methods = ['POST'])
def charge():
    # Set your secret key. Remember to switch to your live secret key in production.
# See your keys here: https://dashboard.stripe.com/apikeys
    stripe.api_key = STRIPE_API_KEY

# Token is created using Stripe Checkout or Elements!
# Get the payment token ID submitted by the form:
    token = request.form['stripeToken'] # Using Flask
    game_id = request.form['game_id']
    team_name = request.form['team_name']
    point_spread = request.form['point_spread']
    wager = request.form['wagers']

    new_bet = Bet(user = session['username'], team_bet = team_name, team_spread = point_spread, wager = wager, game_id = game_id)
    db.session.add(new_bet)
    db.session.commit()

    charge = stripe.Charge.create(
    amount=wager,
    currency='usd',
    description='Example charge',
    source=token,
    )

    return redirect('/bethistory')

@app.route('/bethistory')
def show_bets():
    if "username"  not in session:
        flash("you must log in to view bet history")
        return redirect('/home')
        
    user_bets = Bet.query.filter(session['username'] == Bet.user)
    user = User.query.get(session['username'])
    user_games_bets = user.games
    update_game_scores(user_games_bets)
    return render_template('bethistory.html', user_bets = user_bets, func = is_winning_bet)