from django.shortcuts import render
from django.db import connection

#NOTE: for the scope of this project since we need to execute custom SQL queries
#we will be using connection.cursor() from django.db module to access the db directly
#in this way we can execute custom SQL queries (with cursor.execute())

def index(request):
    cursor = connection.cursor()
    cursor.execute('SELECT city, team_name FROM aaa_team')
    return render(request, 'index.html', {})


def players(request):
    cursor = connection.cursor()
    cursor.execute('SELECT city, team_name FROM aaa_team')
    teamList = cursor.fetchall()
    teamList = [t[0] + " " + t[1] for t in teamList]

    if request.method == 'POST':
        playerName = request.POST.get('player')
        teamName = request.POST.get('team')

        if playerName == "" and teamName == "":
            #query is all players from all teams
            cursor.execute('SELECT * FROM aaa_player NATURAL JOIN aaa_team')
            playerResult = cursor.fetchall()
            return render(request, 'players.html', {'teamList': teamList, 'playerResult': playerResult})
        elif teamName == "":
            #query is a specific player
            cursor.execute('SELECT * FROM aaa_player NATURAL JOIN aaa_team WHERE name LIKE %s', ['%' + playerName + '%'])
            playerResult = cursor.fetchall()
            return render(request, 'players.html', {'teamList': teamList, 'playerResult': playerResult})
        elif playerName == "":
            #query is all players from one team

            #split into city and team name
            if ' ' in teamName:
                teamCity, teamNm = teamName.split(' ', 1)
                cursor.execute('SELECT * FROM aaa_player NATURAL JOIN aaa_team where city LIKE %s AND team_name LIKE %s', ['%' + teamCity + '%', '%' + teamNm + '%'])
            else:
                cursor.execute('SELECT * FROM aaa_player NATURAL JOIN aaa_team where city LIKE %s OR team_name LIKE %s', ['%' + teamName + '%', '%' + teamName + '%'])
            playerResult = cursor.fetchall()
            return render(request, 'players.html', {'teamList': teamList, 'playerResult': playerResult})
        else:
            #query is both player and team matching

            #split into city and team name
            if ' ' in teamName:
                teamCity, teamNm = teamName.split(' ', 1)
                cursor.execute('SELECT * FROM aaa_player NATURAL JOIN aaa_team where city LIKE %s AND team_name LIKE %s AND name LIKE %s', ['%' + teamCity + '%', '%' + teamNm + '%', '%' + playerName + '%'])
            else:
                cursor.execute('SELECT * FROM aaa_player NATURAL JOIN aaa_team where name LIKE %s AND (city LIKE %s OR team_name LIKE %s)', ['%' + playerName + '%', '%' + teamName + '%', '%' + teamName + '%'])
            playerResult = cursor.fetchall()
            return render(request, 'players.html', {'teamList': teamList, 'playerResult': playerResult})


    return render(request, 'players.html', {'teamList': teamList, 'playerResult': []})



def playerPage(request, player_id):
    #get the relevant player information
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM aaa_player NATURAL JOIN aaa_team WHERE player_id = %s', [player_id])
    playerInfo = cursor.fetchall()
    #get all the line info
    cursor.execute('SELECT * FROM aaa_line where player_id = %s', [player_id])
    lineInfo = cursor.fetchall()
    gameList = set(l[2] for l in lineInfo)
    gameInfo = []
    statInfo = []
    for game in gameList:
        #get all of the game and stats info for the given player for that game
        cursor.execute('SELECT * FROM aaa_stats NATURAL JOIN aaa_game WHERE player_id = %s AND game_id = %s', [player_id, game])
        statInfo.append(cursor.fetchall())
    statCategories = set()
    statDict = {} #format for this dict is {stat_category : [stats_for_game, line_for_game]}
    #if the player has stats make the dictionary
    if statInfo:
        #get all of the different stat categories
        statCategories = set(s[2] for s in statInfo[0])
        for stat in statCategories: #init dict
            statDict[stat] = []
            #now add all of the game infos
            for statistic in statInfo[0]:
                # print(statistic)
                if statistic[2] == stat:
                    #get line info for this game and value
                    cursor.execute('SELECT * FROM aaa_line where player_id = %s AND game_id = %s AND attribute = %s', [player_id, statistic[0], statistic[2]])
                    line = cursor.fetchall()
                    statDict[stat].append([statistic, line])


        
    return render(request, 'playerPage.html', {'playerInfo': playerInfo, 'lineInfo':lineInfo, 'gameInfo':gameInfo, 'statCategories':statCategories, 'statInfo':statInfo, 'statDict': statDict})
