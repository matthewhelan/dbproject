from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.db import connection
from django.contrib.auth.decorators import login_required

#NOTE: for the scope of this project since we need to execute custom SQL queries
#we will be using connection.cursor() from django.db module to access the db directly
#in this way we can execute custom SQL queries (with cursor.execute())

def login(request): 
    if request.user.is_authenticated: 
        return HttpResponseRedirect('/index')
    else:
        return render(request, 'login.html')

def getBalance(user_email): 
    cursor = connection.cursor()
    cursor.execute('SELECT balance FROM aaa_user WHERE email = "{}"'.format(user_email))
    user_balance = cursor.fetchall()[0][0]

    return user_balance

@login_required
def index(request):
    cursor = connection.cursor()

    cursor.execute('SELECT * FROM aaa_user WHERE email = "{}"'.format(request.user.email))

    DBuser = cursor.fetchall()

    if ( len(DBuser) == 0 ): 
        cursor.execute('INSERT INTO aaa_user (user_name, email, balance) VALUES ("{}", "{}", "{}")'.format(request.user.username, request.user.email, 0))
    
    user_balance = getBalance(request.user.email)
    print(user_balance)

    # check if the user email exists in the database

    # if it does we extract the user's current money and display it

    # otherwise we create a user and set their currency to 0

    # either way at the end we extract the user's money and pass it to the render

    cursor = connection.cursor()
    return render(request, 'index.html', context={'balance':user_balance})

@login_required
def parlays(request): 
    return render(request, 'index.html')

@login_required
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