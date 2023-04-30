import decimal
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.db import connection, transaction
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from .models import AaaUser
from django.contrib import messages

#NOTE: for the scope of this project since we need to execute custom SQL queries
#we will be using connection.cursor() from django.db module to access the db directly
#in this way we can execute custom SQL queries (with cursor.execute())

# utility function get userid: 
def getUserId(request): 
    cursor = connection.cursor()
    cursor.execute('SELECT user_id FROM aaa_user WHERE email = \"{}\"'.format(request.user.email))
    return cursor.fetchall()[0][0]

def balance(request):
    user_balance = decimal.Decimal(getBalance(request.user.email)) 
    if request.method == 'POST': 
        if (request.POST['button'] == 'withdrawAmountSubmit'):            
            balance_to_withdraw = request.POST['my_value']
            balance_to_withdraw = decimal.Decimal(balance_to_withdraw)
            if ( user_balance - balance_to_withdraw >= 0 ):
                setBalanceTo(request, user_balance - balance_to_withdraw)
                user_balance = user_balance - balance_to_withdraw

        elif (request.POST['button'] == 'depositAmountSubmit'): 
            balance_to_add = decimal.Decimal(request.POST['my_value'])
            if ( user_balance + balance_to_add <= 1000.00 ): 
                setBalanceTo(request, user_balance + balance_to_add)
                user_balance = user_balance + balance_to_add
    
    # max amount in bank is 1000
    # and obv can't withdraw more than value in account
    return render(request, 'balance.html', context={'balance':user_balance})

def setBalanceTo(request, balance): 
    user_id = getUserId(request)
    cursor = connection.cursor()
    cursor.execute('UPDATE aaa_user SET balance = {} WHERE user_id = {}'.format(balance, user_id))

def addBalance(request, balance_to_add): 
    user_balance = getBalance(request.user.email)
    if ( user_balance + balance_to_add <= 1000.00 ): 
        setBalanceTo(user_balance + balance_to_add)

    return HttpResponseRedirect(reverse('balance'))

def withdrawBalance(request, balance_to_withdraw): 
    user_balance = getBalance(request.user.email)
    if ( user_balance - balance_to_withdraw >= 1000.00 ): 
        setBalanceTo(user_balance + balance_to_withdraw)

    return HttpResponseRedirect(reverse('balance'))

def logout_view(request): 
    if not request.user.is_authenticated: 
        return HttpResponseRedirect(reverse('index'))

    logout(request)
    return redirect('/index/')

def follow(request, user_id): 
    cursor = connection.cursor()

    # SQL Looks like
    # INSERT INTO `aaa_following` (`user_id`, `user_id_follows`) 
    # VALUES ((SELECT user_id 
    #          FROM aaa_user
    #          WHERE email = "{}"), {})


    cursor.execute('INSERT INTO `aaa_following` (`user_id`, `user_id_follows`) VALUES ((SELECT user_id FROM aaa_user WHERE email = "{}"), {})'.format(request.user.email, user_id))
    return HttpResponseRedirect(reverse('index'))

def unfollow(request, user_id):
    cursor = connection.cursor() 
    try: 
        # first have to find the user id of our user
        cursor.execute("SELECT user_id FROM aaa_user WHERE email=\"{}\"".format(request.user.email))
        mainUserID = cursor.fetchall()
        
        # then have to match our userid (fetched from above here)
        cursor.execute("DELETE FROM aaa_following WHERE user_id = {} AND user_id_follows = {}".format(mainUserID[0][0], user_id))
        connection.commit() 

    except Exception as e: 
        print("error occured")
        print(e)

    return HttpResponseRedirect(reverse('index'))

def like(request, parlay_id): 
    mainUserID = getUserId(request)

    cursor = connection.cursor()
    cursor.execute("INSERT INTO aaa_likes(user_id, parlay_id) VALUES ({},{})".format(mainUserID, parlay_id))

    return HttpResponseRedirect(reverse('index'))

def unlike(request, parlay_id): 
    mainUserID = getUserId(request)

    cursor = connection.cursor()
    cursor.execute("DELETE FROM aaa_likes WHERE user_id={} AND parlay_id={}".format(mainUserID, parlay_id))

    return HttpResponseRedirect(reverse('index'))

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

    # check if the user email exists in the database

    # if it does we extract the user's current money and display it

    # otherwise we create a user and set their currency to 0

    # either way at the end we extract the user's money and pass it to the render



    # getting list of all users, that are not friends with user, (going to display five or so)
    # with a "add friend button"
    # SQL looks like: 

    # SELECT * from aaa_user 
    # WHERE aaa_user.user_id NOT IN (SELECT user_id_follows 
    #                                FROM aaa_following
    #                                WHERE user_id = (SELECT user_id 
    #                                                 FROM aaa_user 
    #                                                 WHERE email = request.user.email))
    # ORDER BY RAND()
    # LIMIT 5

    cursor.execute('SELECT * FROM aaa_user WHERE aaa_user.user_id NOT IN (SELECT user_id_follows FROM aaa_following WHERE user_id = (SELECT user_id FROM aaa_user WHERE email = "{}")) ORDER BY RAND() LIMIT 5'.format(request.user.email))
    addableUsers = cursor.fetchall()
    addableUsersList = []

    for userInfo in addableUsers: 
        user = AaaUser()
        user.user_id = userInfo[0]
        user.user_name = userInfo[1]
        user.name = userInfo[2]
        user.email = userInfo[3]

        addableUsersList.append(user)

    # display list of current friends (five or so) 
    # with a "remove friend button"

    cursor.execute('SELECT * FROM aaa_user WHERE aaa_user.user_id IN (SELECT user_id_follows FROM aaa_following WHERE user_id = (SELECT user_id FROM aaa_user WHERE email = "{}")) ORDER BY RAND() LIMIT 5'.format(request.user.email))
    followedUsers = cursor.fetchall()

    followedUsersList = []

    for userInfo in followedUsers:
        user = AaaUser()
        user.user_id = userInfo[0]
        user.user_name = userInfo[1]
        user.name = userInfo[2]
        user.email = userInfo[3]

        followedUsersList.append(user)


    # Need to select the parlays from players you're friends with
    # my userid = 101
    # but how we do this is going to be interesting
    # cause we need to be able to show parlays from users on a per-line basis
    # and add the ability to like the parlay
    # 'SELECT * 
    # FROM ((aaa_following JOIN aaa_parlay ON aaa_following.user_id_follows = aaa_parlay.user_id) JOIN aaa_user ON aaa_following.user_id_follows = aaa_user.user_id) NATURAL JOIN aaa_leg WHERE aaa_user.user_id IN (SELECT user_id_follows FROM aaa_following 
    # WHERE user_id = (SELECT user_id FROM aaa_user WHERE email = "{}"))'

    # cursor.execute('SELECT * FROM ((aaa_following JOIN aaa_parlay ON aaa_following.user_id_follows = aaa_parlay.user_id) JOIN aaa_user ON aaa_following.user_id_follows = aaa_user.user_id) NATURAL JOIN aaa_leg WHERE aaa_user.user_id IN (SELECT user_id_follows FROM aaa_following WHERE user_id = (SELECT user_id FROM aaa_user WHERE email = "{}"))'.format(request.user.email))
    # linesFromFollowedUsers = cursor.fetchall()

    # # print(linesFromFollowedUsers)

    # for followingLines in linesFromFollowedUsers: 
    #     print(followingLines)

    # friend_name, friend_username, likes, parlay details, 

    cursor.execute('SELECT user_id FROM aaa_user WHERE email = \"{}\"'.format(request.user.email))
    userID = cursor.fetchall()[0][0]
    # print(userID)

    # SELECT * 
    # FROM aaa_parlay NATURAL JOIN aaa_leg NATURAL JOIN aaa_line
    # WHERE aaa_parlay.user_id IN (SELECT follow_user_id FROM aaa_following WHERE user_id = {})
    cursor.execute('SELECT parlay_id, user_id, name, attribute, value, under FROM aaa_parlay NATURAL JOIN aaa_leg NATURAL JOIN aaa_line NATURAL JOIN aaa_player WHERE aaa_parlay.user_id IN (SELECT user_id_follows FROM aaa_following WHERE user_id = {})'.format(userID))
    followingParlays = cursor.fetchall()

    # need to group all of this by the parlay_id
    # then we iterate over each of the parlays and extract if 
    # the current user likes the parlay and the user who made the parlay's details
    parlays = {}
    for i in followingParlays: 
        parlays[i[0]] = parlays.get(i[0], [])
        parlays[i[0]].append(i)

    parlayDetails = {}
    for key, values in parlays.items(): 
        cursor.execute('SELECT * FROM aaa_likes WHERE user_id = {} AND parlay_id = {}'.format(userID, key))
        likesResult = cursor.fetchall()

        if ( len(likesResult) == 0 ): 
            likes = False
        else: 
            likes = True

        cursor.execute('SELECT email FROM aaa_parlay NATURAL JOIN aaa_user WHERE parlay_id = {}'.format(key))
        otherUser = cursor.fetchall()[0][0]

        parlayDetails[(key, otherUser, likes)] = values

    return render(request, 'index.html', context={'balance':user_balance, 'addableUsers':addableUsersList, 'followedUsers':followedUsersList, 'parlayDetails':parlayDetails})

@login_required
def parlays(request): 
    #del request.session['parlay']

    #get the active parlays with current user id
    uid = getUserId(request)
    cursor = connection.cursor()
    #find all of parlay IDs
    cursor.execute('SELECT * FROM aaa_parlay WHERE user_id = %s AND open=1', [uid])
    openParlayIDs = cursor.fetchall()
    print(openParlayIDs)
    openParlayDict = {}
    #get all of the leg info
    for id in openParlayIDs:
        cursor.execute('SELECT * FROM aaa_leg NATURAL JOIN aaa_line NATURAL JOIN aaa_player NATURAL JOIN aaa_team WHERE parlay_id=%s', [id[0]])
        openParlayInfo = cursor.fetchall()
        openParlayDict[id[0]] = openParlayInfo

    #get closed parlays with current user id
    cursor.execute('SELECT * FROM aaa_parlay NATURAL JOIN aaa_leg WHERE user_id = %s AND open=0', [uid])
    closedParlays = cursor.fetchall()
    closedParlayDict = {}
    #get all of the leg info
    for id in closedParlays:
        cursor.execute('SELECT * FROM aaa_leg NATURAL JOIN aaa_line NATURAL JOIN aaa_player NATURAL JOIN aaa_team WHERE parlay_id=%s', [id[0]])
        closed = cursor.fetchall()
        closedParlayDict[id[0]] = closed
                   
    return render(request, 'parlays.html', {'closedParlays': closedParlayDict, 'openParlays':openParlayDict, 'op':openParlayIDs, 'cl':closedParlays
                                            })

@login_required
def active(request):
    cursor = connection.cursor()
    parlay = []
    if 'parlay' in request.session:
        parlay = request.session['parlay']
    return render(request, 'createparlay.html', {'parlay':parlay, 'messages': messages.get_messages(request), 'button1_active': False, 'button2_active': False})

@login_required
def submit_parlay(request):
    if request.method == 'POST':
        if 'parlay' in request.session:
            parlay = request.session['parlay']
            lines = []
            #see if all of the over/unders are selected
            for leg in parlay:
                line_id = leg[0][7]
                ou = request.POST.get(line_id)
                #if neither button is selected, return error
                if ou == None:
                    messages.error(request, 'Need to select either over or under for all legs')
                    return redirect(active)
                #add line_id
                lines.append([line_id, ou])


            #make a new parlay with all of the given legs
            #get amount wagered
            amount = decimal.Decimal(request.POST.get('amount'))
            #ensure that the wagered amount is not more than the user balance
            user_balance = decimal.Decimal(getBalance(request.user.email)) 

            if amount > user_balance:
                messages.error(request, 'Amount wagered is greater than your balance!')
                return redirect(active)

            #subtract balance
            setBalanceTo(request, user_balance - amount)
            #get userID
            uid = getUserId(request)

            print(amount)
            cursor = connection.cursor()
            cursor.execute('INSERT INTO aaa_parlay (user_id, open, number_of_legs, amount_wagered) VALUES ("{}", "{}", "{}", "{}") RETURNING parlay_id'.format(uid, 1, len(lines), amount))
            parlay_id = cursor.fetchone()[0]
            #now we need to add the corresponding lines to the parlay in the leg table
            for line in lines:
                if line[1] == 'Over':
                    cursor.execute('INSERT INTO aaa_leg (parlay_id, line_id, under) VALUES ("{}", "{}", "{}")'.format(parlay_id, line[0], 0))
                elif line[1] == 'Under':
                    cursor.execute('INSERT INTO aaa_leg (parlay_id, line_id, under) VALUES ("{}", "{}", "{}")'.format(parlay_id, line[0], 1))
                
            cursor.fetchall()

            connection.commit()

            #now we need to clear out session
            del request.session['parlay']
            return redirect(parlays)

        else:
            print('hi')
            messages.error(request, 'Need at least one leg in the parlay')
            return redirect(active)
        
    return redirect(active)


@login_required
def delete_leg(request, idx):
    if 'parlay' in request.session:
        #get idx
        p = request.session['parlay']
        print(p)
        if len(p) > 1:
            del p[int(idx)]
            request.session['parlay'] = p
        else:    
            del request.session['parlay']
        print(p)
        
    return redirect(active)
    



@login_required
def create_parlay(request):
    
    # create a new active parlay
    if request.method == 'POST':
        name = request.POST.get('player_name')
        team = request.POST.get('team')
        attribute = request.POST.get('attribute')
        over = request.POST.get('over_odds')
        under = request.POST.get('under_odds')
        val = request.POST.get('value')
        book = request.POST.get('sportsbook')
        line_id = request.POST.get('line_id')
        parlay = [name, team, attribute,  val, book, over, under, line_id]
        # print(parlay)

        if 'parlay' in request.session:
            p = request.session['parlay']
            print(p)
            if [parlay, None] in p:
                messages.error(request, 'Cannot add same line to parlay twice!')
            else:
                p.append((parlay, None))
                request.session['parlay'] = p
        else: #add to a new session with the parlay info, over/under
            request.session['parlay'] = [(parlay, None)]

        return redirect(active)

    return redirect(active)


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

    cursor.execute('SELECT * FROM aaa_line WHERE player_id = %s AND sportsbook = \"DRAFTKINGS\"', [player_id])
    addableLines = cursor.fetchall()
    

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

        
    return render(request, 'playerPage.html', {'playerInfo': playerInfo, 'lineInfo':lineInfo, 'addableLines':addableLines, 'gameInfo':gameInfo, 'statCategories':statCategories, 'statInfo':statInfo, 'statDict': statDict})
