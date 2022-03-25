from models import Team, Game
import requests
from api_key import NBA_API_KEY
from models import db

from datetime import datetime, date
today = date.today()
headers = {
    'x-rapidapi-host': "api-nba-v1.p.rapidapi.com",
    'x-rapidapi-key': NBA_API_KEY
    }

def find_nba_teams(teams):
    nba_teams = []
    for team in teams:
        if team.get("nbaFranchise") == True and team.get("name") != "Home Team Stephen A":
            nba_teams.append(team)

    return nba_teams

def is_nba_game(game):
    visitor_id = game.get("teams").get("visitors").get("id") 
    home_id = game.get("teams").get("home").get("id") 
    if(Team.query.get(visitor_id) == None or Team.query.get(home_id) == None):
            return False
    return True

def is_player_active(player):
    if player.get("leagues").get("standard").get("active") == True:
        return True
    else:
        return False

def update_game_scores(games):
    for game in games:
        if today.strftime("%Y-%m-%d") > game.date and game.home_score == None or game.home_score == 0:
            querystring = {"id":f"{game.id}"}
            response = requests.request("GET", "https://api-nba-v1.p.rapidapi.com/games", headers=headers, params=querystring)
            res = response.json()
            games_stats = res.get("response")
            game.home_score = games_stats[0].get("scores").get("home").get("points")
            game.visitor_score = games_stats[0].get("scores").get("visitors").get("points")
            game.arena = games_stats[0].get("arena").get("name")
            db.session.add(game)
            db.session.commit()

def is_winning_bet(game_id, team_name, point_spread):
    game = Game.query.get(game_id)
    if game.home_score == None:
        return "Pending"
    
    home_spread = game.home_score - game.visitor_score
    visitor_spread = game.visitor_score - game.home_score

    if game.home_name == team_name and point_spread < 0 and home_spread > abs(point_spread):
        return True
    elif game.home_name == team_name and point_spread < 0 and home_spread < abs(point_spread):
        return False
    elif game.home_name == team_name and point_spread > 0 and home_spread > 0:
        return True
    elif game.home_name == team_name and point_spread > 0 and abs(home_spread) < point_spread:
        return True
    elif game.home_name == team_name and point_spread > 0 and abs(home_spread) > point_spread:
        return False
    elif game.visitor_name == team_name and point_spread < 0 and visitor_spread > abs(point_spread):
        return True
    elif game.visitor_name == team_name and point_spread < 0 and visitor_spread < abs(point_spread):
        return False
    elif game.visitor_name == team_name and point_spread > 0 and visitor_spread > 0:
        return True
    elif game.visitor_name == team_name and point_spread > 0 and abs(visitor_spread) < point_spread:
        return True
    elif game.visitor_name == team_name and point_spread > 0 and abs(visitor_spread) > point_spread:
        return False
    else:
        return None