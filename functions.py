from models import Team

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