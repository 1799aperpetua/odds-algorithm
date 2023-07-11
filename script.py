import requests
import json
import sqlite3

# Note:  Would be good to capture date as-well and use it for querying purposes

# :Method: Send a request to The Odds API for the chosen sport's games.  Add each game's data (books/teams/prices) to an empty SQL table
# :params: key - API key, sport - Desired sport
def PullOdds(key, sport):
    # - Pull the chosen sport's odds for [today's] games
    
    url = f'https://api.the-odds-api.com/v4/sports/{sport}/odds/?regions=us&oddsFormat=american&apiKey={key}'

    response = requests.get(url)

    # - Check to make sure that we connected to the right endpoint
    if response.ok:
        pass
    else:
        return print("Invalid request")
    
    odds_data = json.loads(response.text)

    # - Connect to our database
    conn = sqlite3.connect('oddsDatabase.db')
    cur = conn.cursor()

    # - Loop through the data and add each matchup to our database
    drop_table_query = 'DROP TABLE IF EXISTS matchups'
    cur.execute(drop_table_query)

    # matchup: away@home
    create_table_query = '''
    CREATE TABLE matchups (
    matchup TEXT,
    away TEXT,
    awayPrice INTEGER,
    home TEXT,
    homePrice INTEGER,
    book TEXT
    )
    '''
    cur.execute(create_table_query)

    # Make it so that we drop table, create table, executemany for each game; and query the results for each game - Then bucket before moving to the next game

    matches = []
    for game in odds_data:
        matchupID = game['away_team'] + '@' + game['home_team']
        for matchups in game['bookmakers']:
            # These are strictly moneyline odds as of right now
            #print(matchups['title'], ' | ', 'Away:', matchups['markets'][0]['outcomes'][0]['name'], matchups['markets'][0]['outcomes'][0]['price'], ' | ', 'Home:', matchups['markets'][0]['outcomes'][1]['name'], matchups['markets'][0]['outcomes'][1]['price'])

            awayTeam = matchups['markets'][0]['outcomes'][0]['name']
            awayTeam = awayTeam.replace(" ", "_")
            awayPrice = matchups['markets'][0]['outcomes'][0]['price']
            
            homeTeam = matchups['markets'][0]['outcomes'][1]['name']
            homeTeam = homeTeam.replace(" ", "_")
            homePrice = matchups['markets'][0]['outcomes'][1]['price']
            
            book = matchups['title']

            matches.append( (matchupID, awayTeam, awayPrice, homeTeam, homePrice, book) )

        insert_match_query = '''INSERT INTO matchups (matchup, away, awayPrice, home, homePrice, book) VALUES (?, ?, ?, ?, ?, ?);'''
        
    cur.executemany(insert_match_query, matches)

    conn.commit()

# :Method: Query each game to display the top 3 books for each team for each game
def QueryTopThree():
    
    # Pull Odds !!! Set this up

    # - Connect to our database
    try:
        conn = sqlite3.connect('oddsDatabase.db')
        cur = conn.cursor()
    except:
        print("Could not connect to the database")
    
    # - Capture each unique matchup that we pulled
    select_matchups_query = '''
    SELECT DISTINCT matchup FROM matchups
    '''
    cur.execute(select_matchups_query)
    game_list = cur.fetchall()
    
    # - Access each game by their IDs and return the three best prices
    queried_awayPrices = []
    queried_homePrices = []
    for gameID in game_list:
        away_game_prices = []
        home_game_prices = []
        
        # - Select our best home prices
        select_best_homePrices_query = f'''
        SELECT book, home, homePrice from matchups  WHERE matchup = "{gameID[0]}"
        ORDER BY
        CASE
            WHEN (SELECT AVG(homePrice) FROM matchups) >= 0 THEN homePrice
            ELSE -homePrice
        END ASC
        LIMIT 3;
        '''
        cur.execute(select_best_homePrices_query)
        best_home_prices = cur.fetchall()

        # - Add our three picks to a list
        for row in best_home_prices:
            home_game_prices.append(row[0] + ": " + row[1] + " @ " + str(row[2]))
        
        # - Add our list of three picks, to our complete list of [today's] picks
        queried_homePrices.append(home_game_prices)

        # - Select our best away prices
        select_best_awayPrices_query = f'''
        SELECT book, away, awayPrice from matchups  WHERE matchup = "{gameID[0]}"
        ORDER BY
        CASE
            WHEN (SELECT AVG(awayPrice) FROM matchups) >= 0 THEN awayPrice
            ELSE -awayPrice
        END ASC
        LIMIT 3;
        '''
        cur.execute(select_best_awayPrices_query)
        best_away_prices = cur.fetchall()

        # - Add our three picks to a list
        for row in best_away_prices:
            away_game_prices.append(row[0] + ": " + row[1] + " @ " + str(row[2]))
        
        # - Add our list of three picks, to our complete list of [today's] picks
        queried_awayPrices.append(away_game_prices)
    
    print("================================")
    print("Away Plays")
    for item in queried_awayPrices:
        print(item)
    print("================================")
    print("Home Plays")
    for item in queried_homePrices:
        print(item)
        
# :Method: Query each game and display three buckets of value plays indicating the amount of value with each play (if any)
def QueryMispricedPlays(key, sport):

    # Pull Odds !!! Set this up
    PullOdds(key, sport)

    # - Connect to our database
    try:
        conn = sqlite3.connect('oddsDatabase.db')
        cur = conn.cursor()
    except:
        print("Could not connect to the database")
    
    # - Capture each unique matchup that we pulled
    select_matchups_query = '''
    SELECT DISTINCT matchup FROM matchups
    '''
    cur.execute(select_matchups_query)
    game_list = cur.fetchall()
    print("Today's Games:", game_list)

    # - Queries
    select_best_away_price_query = '''
    SELECT book, away, awayPrice from matchups  WHERE matchup = (?) ORDER BY 
    CASE
	    WHEN (SELECT AVG(awayPrice) FROM matchups) >= 0 THEN awayPrice
	    ELSE -awayPrice
    END ASC
    LIMIT 1;
    '''

    select_second_best_away_price_query = f'''
    SELECT book, away, awayPrice from matchups  WHERE matchup = (?)
    ORDER BY
    CASE
	    WHEN (SELECT AVG(awayPrice) FROM matchups) >= 0 THEN awayPrice
	    ELSE -awayPrice
    END ASC
    LIMIT 1 OFFSET 1;
    '''

    select_best_home_price_query = f'''
    SELECT book, home, homePrice from matchups  WHERE matchup = (?)
    ORDER BY
    CASE
	    WHEN (SELECT AVG(homePrice) FROM matchups) >= 0 THEN homePrice
	    ELSE -homePrice
    END ASC
    LIMIT 1;
    '''

    select_second_best_home_price_query = f'''
    SELECT book, home, homePrice from matchups  WHERE matchup = (?)
    ORDER BY
    CASE
	    WHEN (SELECT AVG(homePrice) FROM matchups) >= 0 THEN homePrice
	    ELSE -homePrice
    END ASC
    LIMIT 1 OFFSET 1;
    '''
    # END QUERIES --------------------------------------------------

    bucket1 = [] # 10 - 50 pts
    bucket2 = [] # 51 - 149 pts
    bucket3 = [] # 150+ pts

    # loop through each matchup, checking for a discrepancy between the best price and second best price - also show median and mean
    for game in game_list:
        
        # Query the best away price
        cur.execute(select_best_away_price_query, game)
        best_away_price = cur.fetchone()

        # Query the second best away price
        cur.execute(select_second_best_away_price_query, game)
        second_best_away_price = cur.fetchone()
    
        # Query the best home price
        cur.execute(select_best_home_price_query, game)
        best_home_price = cur.fetchone()

        # Query the second best home price
        cur.execute(select_second_best_home_price_query, game)
        second_best_home_price = cur.fetchone()

        # Determine if/how much value the away team has
        away_result = best_away_price[2] - second_best_away_price[2]
        if away_result >= 150:
            bucket3.append([best_away_price, away_result])
        elif away_result > 50:
            bucket2.append([best_away_price, away_result])
        elif away_result >= 10:
            bucket1.append([best_away_price, away_result])

        # Determine if/how much value the home team has
        home_result = best_home_price[2] - second_best_home_price[2]
        if home_result >= 150:
            bucket3.append([best_home_price, home_result])
        elif home_result > 50:
            bucket2.append([best_home_price, home_result])
        elif home_result >= 10:
            bucket1.append([best_home_price, home_result])
            

    # Display our bucketed plays
    final_str = "\nBucket 3 (150+ pts)"
    if bucket3:
        for item in bucket3:
            final_str += "\n" + str(str(item[0][0]) + " " + str(item[0][1]) + " " + str(item[0][2]) + " (" + str(item[1]) + ")")
    else:
        final_str += "\nNo value picks in this bucket"
    
    final_str += "\n\nBucket 2 ( 51 - 149 pts )"
    if bucket2:
        for item in bucket2:
            final_str += "\n" + str(str(item[0][0]) + " " + str(item[0][1]) + " " + str(item[0][2]) + " (" + str(item[1]) + ")")
    else:
        final_str += "\nNo value picks in this bucket"

    final_str += "\n\nBucket 1 ( 10 - 50 pts )"
    if bucket1:
        for item in bucket1:
            final_str += "\n" + str(str(item[0][0]) + " " + str(item[0][1]) + " " + str(item[0][2]) + " (" + str(item[1]) + ")")
    else:
        final_str += "\nNo value picks in this bucket"

    return final_str