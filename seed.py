  # seed team table
  response = requests.request("GET", "https://api-nba-v1.p.rapidapi.com/teams", headers=headers)
    res = response.json()
    teams = res.get("response")
    nba_teams = find_nba_teams(teams)
    
    for team in nba_teams:
        new_team = Team(id = team.get("id"), name = team.get("name"), code = team.get("code"), city = team.get("city"), logo = team.get("logo") )
        db.session.add(new_team)
        db.session.commit()
    
    #seed game table
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