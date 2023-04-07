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