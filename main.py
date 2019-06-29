"""
Juegos - A matchmaking and 2D game rendering framework for Discord.py
---------------------------------------------------------------------
This script was made for Discord hack week by @Panley#3274 with art assets by @pixelflow#2332
This script is not made to be an exhaustive selection of games, rather it's build with the intention of providing an easy method
for Python developers to port Singleplayer and Multiplayer 2D games to discord with realitve ease.

**TO ADD A NEW GAME**
create a new PY script akin to ox.py as presented here.
The exiting framework in this script will let you easily pass updates based on emoji reactions or text responses with support for time-based board updates
Add the game ID and aliases to the games list below as formatted below
Add the game info dict to gamesinfo below as formatted below
Import your complted PY file below
You can now add game functions to the existing framework on predetermined events, or if you really want to, code your own events!
"""
import random
import discord
import ast
import ox
import cn4
import requests
import os
import sys
botauthorid = "249287049482338305" # <<<<<<<<<<<<<<<< IF YOU ARE MANUALLY HOSTING, REPLACE THIS STRING WITH YOUR OWN DISCORD ID OR YOU WILL NOT BE ABLE TO USE DEV COMMANDS!
discordtoken = (open("token.cfg","r")).read()
if discordtoken == "":
    discordtoken = input("No bot token detected, please set it now: ")
    (open("token.cfg","w")).write(discordtoken)
bot = discord.Client()
games = list(ast.literal_eval((open("gameslist.cfg","r")).read()))
gamesinfo = dict(ast.literal_eval((open("gamesdict.cfg","r")).read()))
print("Flushing ratleimiter & matchmaking file...")
(open("lookingusers","w")).write("")
(open("activegames","w")).write("")
def limituser(id):
    #This function is used to add a user who has created a game or joined a game to the one active game per-person ratelimit
    pre = (open("lookingusers","r")).read()
    pre = pre + " " + id
    (open("lookingusers","w")).write(pre)
def unlimituser(id):
    #This function is used to remove a user who has left or finished a game from the one active game per-person ratelimit
    pre = (open("lookingusers","r")).read()
    pre = pre.replace(" "+id,"")
    (open("lookingusers","w")).write(pre)
def checklimited(id):
    #This function checks if a user currently limited by the one active game per-person ratelimit
    pre = (open("lookingusers","r")).read()
    if id in pre:
        return True
    else:
        return False
def findgame(game_name):
    #this function comapres given game names to a set game ID so one game ID can have multiple aliases
    if game_name in games:
        return games[games.index(game_name)+1]
    else:
        return False
def makegame(game_id,privacy):
    #This function will create a matchmaking match for a given game
    vars = {"game_id":game_id,"privacy":privacy}
    if game_id != None:
        if game_id in games:
            vars["s"] = True
            if games[games.index(game_id)+1] == "mp":
                vars["mp"] = True
                if privacy == "invite":
                    token = ""
                    while len(token) < 10:
                        token += str(random.randint(0,9))
                    vars["pass"] = token 
            else:
                vars["mp"] = False
        else:
            vars["s"] = False
    else:
        vars["s"] = False
    return vars
def matchmaking(vars,creator_id):
    #This function adds a matchmaking dict to the global matchmaking file
    if vars["mp"] == True:
        match_id = vars["game_id"] + "-"
        token = ""
        while len(token) < 10:
            token += str(random.randint(0,9))
        match_id+=str(token)
        if vars["privacy"] != None:
            if vars["pass"] != None:
                match_id+="-"+vars["pass"]
        matchinfo = {"timeout":300,"match_id":match_id,"users":[creator_id],"gameid":vars["game_id"]}
        matchinfo["ctrls"] = (gamesinfo[vars["game_id"]])["cscheme"]
        if ((gamesinfo[vars["game_id"]])["cscheme"])[0] == 1:
            vars["reactions"] == (gamesinfo[vars["game_id"]])["reactions"]
        exinf = (open("activegames","r")).read()
        (open("activegames","w")).write(exinf+"||"+str(matchinfo))
        return matchinfo
    else:
        return None
def closematch(match_id):
    #This function removes a matchmaking dict from the global matchmaking file
    print("looking to close match: "+match_id)
    activegames = ((open("activegames","r")).read()).split("||")
    concat = ""
    for x in activegames:
        if (x != None) and (x != ""):
            if dict(ast.literal_eval(x))["match_id"] == match_id:
                print("   match identified with ID: "+dict(ast.literal_eval(x))["match_id"]+" = closeID "+match_id)
            else:
                print("   match identified with ID: "+dict(ast.literal_eval(x))["match_id"])
                concat += "||" + str(x)
    (open("activegames","w")).write(concat)
def tryjoin(message):
    #This function attempts to parse for a matchmaking session search from user messages
    if message.author.bot == False:
        if message.content.startswith("~"):
            params = (message.content.replace("~","")).rsplit()
            if len(params) == 2:
                if params[0] == "joinid":
                    try:
                        match = (open("activegames","r").read())
                        if params[1] in match:
                            return True
                        else:
                            return False
                    except:
                        return False
                elif params[0] == "join":
                    if findgame(params[1]) != False:
                        return True
                else:
                    return False
    elif message.author.id == "592997793434697728":
        params = (message.content.replace("~","")).rsplit()
        try:
            match = (open("activegames","r").read())
            if params[1] in match:
                return True
            else:
                return False
        except:
            return False
    return False
def joingame(matchinfo,user_id):
    #This function attempts to add a user to a matchmaking session, requires the user isn't already in it
    if user_id not in matchinfo["users"]:
        matchinfo["users"].append(user_id)
        updategame(matchinfo["match_id"],matchinfo)
        return matchinfo
    else:
        return None
def updategame(match_id,matchinfo):
    #this function updates a matchmaking dict from the global matchmaking file
    activegames = ((open("activegames","r")).read()).split("||")
    concat = ""
    for x in activegames:
        if (x != None) and (x != ""):
            if dict(ast.literal_eval(x))["match_id"] == match_id:
                concat += "||"+str(matchinfo)
            else:
                concat += "||" + str(x)
    (open("activegames","w")).write(concat)
def leavegame(matchinfo,user_id):
    #This function removes a user from a matchmaking session
    if user_id in matchinfo["users"]:
        matchinfo["users"].remove(user_id)
        return matchinfo
    else:
        return None
@bot.event
async def on_ready():
    #Basic custom presence because a e s t h e t i c s
    print("Discord connected")
    game = discord.Game(name = "panley.co.uk/juegos",type = 3,url = "https://panley.co.uk/juegos")
    await bot.change_presence(game = game)
@bot.event
async def on_message(message):
    if checklimited(message.author.id) == False:
        if message.author.bot == False:
            if message.content.startswith("~"):
                params = (message.content.replace("~","")).rsplit()
                if (params[0] == "help"):
                    toembed = discord.Embed(
                        title = "Juegos Commands",
                        description = "format: `~command|alias <required argument> (optional argument)`\n`~help` - Shows this!\n`~newgame|ng <game name> (private)` - Create a new game for the given game name\n`~findgame|fg <game name>` - Finds a public match for the given game name\n`~joinid <match ID>` - Joins the user to a given match/private match\n`~games` - Lists all games present on the bot\n`~addgamefile` - **Bot owner only!** lets the bot owner dynamically add a new game to the bot (Experimental)",
                        color = 7506394
                    )
                    toembed.add_field(
                        name = "Programmed by Panley#3274 in Python",
                        value = "[Creators server](https://discord.gg/tBs8MRE) | [Official website](https://panley.co.uk/juegos) | [GitHub](https://github.com/panley01/Juegos)"
                    )
                    await bot.send_message(message.channel,embed = toembed)
                elif (params[0] == "games"):
                    toembed = discord.Embed(
                        title = "Installed Games",
                        color = 7506394
                    )
                    for x in gamesinfo:
                        x = gamesinfo[x]
                        toembed.add_field(
                            name = ("**"+x["selfname"]+"** - Aliases: "+x["aliases"]),
                            value = ("Created by "+x["creator"]+"\n"+x["desc"]+"\nPlayers - Min: "+str(x["minplayers"])+" Max: "+str(x["maxplayers"]))
                        )
                    await bot.send_message(message.channel,embed = toembed)
                elif (params[0] == "addgamefile") and (message.author.id == botauthorid):
                    await bot.send_message(message.channel,"**THIS FEATURE IS EXPERIMENTAL AND CURRENTLY DISABLED!**")
                elif (params[0] == "newgame") or (params[0] == "ng"):
                    print("   command ID: Newgame")
                    if len(params) > 1:
                        # Privacy is expandable, there is potential for cross-bot communication via a web API or dedicated bot interaction server. Right now there's just invite only (private after the game name) and public
                        if len(params) > 2:
                            if params[2] == "private":
                                priv = "invite"
                            else:
                                priv = None
                        else:
                            priv = None
                        gameid = findgame(params[1])
                        game = makegame(gameid,privacy = priv)
                        if game["mp"] == True:
                            game = matchmaking(game,message.author.id)
                            resp = ""
                            gamenameconst = params[1]
                            toembed = discord.Embed(
                                title = gamenameconst+" game created",
                                description = "Match ID: "+game["match_id"],
                                color = 7506394
                            )
                            usrprint = ""
                            for u in game["users"]:
                                u = await bot.get_user_info(u)
                                usrprint += u.name + "\n"
                            toembed.add_field(
                                name = "Players ["+str(len(game["users"]))+"/"+str((gamesinfo[game["gameid"]])["maxplayers"])+"]",
                                value = usrprint
                            )
                            gameinit = await bot.send_message(message.author,embed = toembed)
                            messages = [gameinit]
                            limituser(message.author.id)
                            while resp != None:
                                resp = await bot.wait_for_message(check = tryjoin,timeout = game["timeout"])
                                if resp != None:
                                    print("   Active lobby recived join request: "+resp.content)
                                    toembed = discord.Embed(
                                        title = gamenameconst+" game created",
                                        description = "Match ID: "+game["match_id"]
                                    )
                                    usrprint = ""
                                    for u in game["users"]:
                                        u = await bot.get_user_info(u)
                                        usrprint += u.name + "\n"
                                    toembed.add_field(
                                        name = "Players ["+str(len(game["users"]))+"/"+str((gamesinfo[game["gameid"]])["maxplayers"])+"]",
                                        value = usrprint
                                    )
                                    params = (resp.content.replace("~","")).rsplit()
                                    if resp.author.bot == False:
                                        resp1 = joingame(game,resp.author.id)
                                        addmsg = await bot.send_message(resp.author,embed = toembed)
                                    else:
                                        gameid = params[1]
                                        if gameid == game["match_id"]:
                                            useradd = await bot.get_user_info(params[2])
                                            addmsg = await bot.send_message(useradd,embed = toembed)
                                            resp1 = joingame(game,useradd.id)
                                        else:
                                            resp1 = None
                                    if resp1 != None:
                                        game = resp1
                                        messages.append(addmsg)
                                else:
                                    if len(game["users"]) >= (gamesinfo[game["gameid"]])["minplayers"]:
                                        matchmade = True
                                    else:
                                        matchmade = False
                                if len(game["users"]) >= (gamesinfo[game["gameid"]])["maxplayers"]:
                                    matchmade = True
                                    resp = None
                                for m in messages:
                                    toembed = discord.Embed(
                                        title = gamenameconst+" game created",
                                        description = "Match ID: "+game["match_id"],
                                        color = 7506394
                                    )
                                    usrprint = ""
                                    for u in game["users"]:
                                        u = await bot.get_user_info(u)
                                        usrprint += u.name + "\n"
                                    toembed.add_field(
                                        name = "Players ["+str(len(game["users"]))+"/"+str((gamesinfo[game["gameid"]])["maxplayers"])+"]",
                                        value = usrprint
                                    )
                                    await bot.edit_message(m,embed = toembed)
                            closematch(game["match_id"])
                            print("match with ID: "+game["match_id"]+" closed from matchmaking")
                            if matchmade == True:
                                for zz in messages:
                                    toembed = discord.Embed(
                                        title = gamenameconst+" game created",
                                        description = "Match ID: "+game["match_id"],
                                        color = 10070709
                                    )
                                    usrprint = ""
                                    for u in game["users"]:
                                        u = await bot.get_user_info(u)
                                        usrprint += u.name + "\n"
                                    toembed.add_field(
                                        name = "Players ["+str(len(game["users"]))+"/"+str((gamesinfo[game["gameid"]])["maxplayers"])+"]",
                                        value = usrprint,
                                        inline = True
                                    )
                                    ctrlmsg = (gamesinfo[game["gameid"]])["ctrlmsg"]
                                    toembed.add_field(
                                        name = "Game instructions:",
                                        value = ctrlmsg,
                                        inline = True
                                    )
                                    toembed.add_field(
                                        name = "Rendering boards...",
                                        value = "This may take some time depending on game complexity and bot usage",
                                        inline = True
                                    )
                                    await bot.edit_message(zz,embed = toembed)
                                userstatuses = []
                                #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Initial board rendering is declared here
                                gamesafe = game
                                messagessafe = messages
                                try:
                                    if game["gameid"] == "ox":
                                        toprint = ox.firstrender()
                                    elif game["gameid"] == "cn4":
                                        toprint = cn4.firstrender()
                                    #DO NOT EDIT THIS COMMENT! THIS LINE IS REFERENCED FOR DYNAMIC FILE UPDATING!
                                    #initrenderhere
                                    for plr in game["users"]:
                                        chnl = await bot.get_user_info(plr)
                                        msgs = []
                                        for rdr in toprint:
                                            concat = ""
                                            for rdr1 in rdr:
                                                concat += rdr1
                                            msgr = await bot.send_message(chnl,concat)
                                            msgs.append(msgr.id)
                                            dmchl = msgr.channel.id
                                        if (game["ctrls"])[0] == 1:
                                            for emji in game["reactions"]:
                                                await bot.add_reaction(msgr,emji)
                                        userinf = {"id":plr,"board":toprint,"messages":msgs,"dmchannel":dmchl,"team":(game["users"]).index(plr)}
                                        userstatuses.append(userinf)
                                        game["usrstatuses"] = userstatuses
                                        game["currentplay"] = 0
                                    print("Game started with ID: "+str(game["match_id"]))
                                    while matchmade == True:
                                        for zz in messages:
                                            toembed = discord.Embed(
                                                title = gamenameconst+" game created",
                                                description = "Match ID: "+game["match_id"],
                                                color = 10070709
                                            )
                                            usrprint = ""
                                            for u in game["users"]:
                                                uu = await bot.get_user_info(u)
                                                usrprint += uu.name + "\n"
                                                if (game["users"]).index(u) == game["currentplay"]:
                                                    plrname = uu.name
                                            toembed.add_field(
                                                name = "Players ["+str(len(game["users"]))+"/"+str((gamesinfo[game["gameid"]])["maxplayers"])+"]",
                                                value = usrprint,
                                                inline = True
                                            )
                                            ctrlmsg = (gamesinfo[game["gameid"]])["ctrlmsg"]
                                            toembed.add_field(
                                                name = "Game instructions:",
                                                value = ctrlmsg,
                                                inline = True
                                            )
                                            toembed.add_field(
                                                name = "Game active",
                                                value = plrname+"'s turn",
                                                inline = True
                                            )
                                            await bot.edit_message(zz,embed = toembed)
                                        userwaitfor = await bot.get_user_info((game["users"])[game["currentplay"]])
                                        if (game["ctrls"])[0] == 0:
                                            if (game["ctrls"])[1] == 0:
                                                resp = await bot.wait_for_message(author = userwaitfor,timeout = game["timeout"])
                                            else:
                                                resp = await bot.wait_for_message(author = userwaitfor,timeout = 1)
                                        elif (game["ctrls"])[0] == 1:
                                            if (game["ctrls"])[1] == 0:
                                                resp = await bot.wait_for_reaction(user = userwaitfor,timeout = game["timeout"])
                                            else:
                                                resp = await bot.wait_for_reaction(user = userwaitfor,timeout = 1)
                                        if str(resp) == "exit":
                                            #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Handling for a user leaving the game by choice
                                            game = leavegame(game,(game["users"])[game["currentplay"]])
                                            if len(game["users"]< (gamesinfo[game["gameid"]])["minplayers"]):
                                                matchmade = False
                                                for jjjj in game["users"]:
                                                    unlimituser(jjjj)
                                                for jjj in messages:
                                                    toembed = discord.Embed(
                                                        title = gamenameconst+" game created",
                                                        description = "Match ID: "+game["match_id"],
                                                        color = 10070709
                                                    )
                                                    usrprint = ""
                                                    for u in game["users"]:
                                                        u = await bot.get_user_info(u)
                                                        usrprint += u.name + "\n"
                                                    toembed.add_field(
                                                        name = "Players ["+str(len(game["users"]))+"/"+str((gamesinfo[game["gameid"]])["maxplayers"])+"]",
                                                        value = usrprint,
                                                        inline = True
                                                    )
                                                    toembed.add_field(
                                                        name = "GAME OVER",
                                                        value = "Too many users disconnected.",
                                                        inline = True
                                                    )
                                                    await bot.edit_message(jjj,embed = toembed)
                                            else:
                                                if game["currentplay"] == len(game["users"])-1:
                                                    game["currentplay"] = 0
                                                else:
                                                    game["currentplay"] += 1
                                        elif (resp != None) and ((game["ctrls"])[1] == 0):
                                            #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< On message events here
                                            if game["gameid"] == "ox":
                                                r1 = ox.makeplay(((game["usrstatuses"])[game["currentplay"]]),resp.content)
                                            elif game["gameid"] == "cn4":
                                                r1 = cn4.makeplay(((game["usrstatuses"])[game["currentplay"]]),resp.content)
                                            #DO NOT EDIT THIS COMMENT! THIS LINE IS REFERENCED FOR DYNAMIC FILE UPDATING!
                                            #msgeventhere
                                            if r1 != False:
                                                ((game["usrstatuses"])[game["currentplay"]]) = r1
                                                for usrs in game["usrstatuses"]:
                                                    for clmn in (usrs)["board"]:
                                                        concat = ""
                                                        for xzzx in clmn:
                                                            concat += xzzx
                                                        chnl = bot.get_channel(usrs["dmchannel"])
                                                        msgs = (usrs["messages"])[(usrs["board"]).index(clmn)]
                                                        msgobj = await bot.get_message(chnl,msgs)
                                                        if msgobj.content != concat:
                                                            await bot.edit_message(msgobj,concat)
                                                if game["gameid"] == "ox":
                                                    winchk = ox.wincond(((game["usrstatuses"])[game["currentplay"]]))
                                                elif game["gameid"] == "cn4":
                                                    winchk = cn4.wincond(((game["usrstatuses"])[game["currentplay"]]))
                                                #DO NOT EDIT THIS COMMENT! THIS LINE IS REFERENCED FOR DYNAMIC FILE UPDATING!
                                                #msgwincondhere
                                                if winchk == True:
                                                    for jjj in messages:
                                                        toembed = discord.Embed(
                                                            title = gamenameconst+" game created",
                                                            description = "Match ID: "+game["match_id"],
                                                            color = 10070709
                                                        )
                                                        usrprint = ""
                                                        for u in game["users"]:
                                                            u = await bot.get_user_info(u)
                                                            usrprint += u.name + "\n"
                                                        toembed.add_field(
                                                            name = "Players ["+str(len(game["users"]))+"/"+str((gamesinfo[game["gameid"]])["maxplayers"])+"]",
                                                            value = usrprint,
                                                            inline = True
                                                        )
                                                        usrget = await bot.get_user_info((game["users"])[game["currentplay"]])
                                                        toembed.add_field(
                                                            name = "GAME OVER",
                                                            value = usrget.name+" has won!",
                                                            inline = True
                                                        )
                                                        await bot.edit_message(jjj,embed = toembed)
                                                    for jjjj in game["users"]:
                                                        unlimituser(jjjj)
                                                    matchmade = False
                                                if game["gameid"] == "ox":
                                                    losschk = ox.losscond(((game["usrstatuses"])[game["currentplay"]]))
                                                elif game["gameid"] == "cn4":
                                                    losschk = cn4.losscond(((game["usrstatuses"])[game["currentplay"]]))
                                                #DO NOT EDIT THIS COMMENT! THIS LINE IS REFERENCED FOR DYNAMIC FILE UPDATING!
                                                #msglosscondhere
                                                if losschk == True:
                                                    for jjj in messages:
                                                        toembed = discord.Embed(
                                                            title = gamenameconst+" game created",
                                                            description = "Match ID: "+game["match_id"],
                                                            color = 10070709
                                                        )
                                                        usrprint = ""
                                                        for u in game["users"]:
                                                            u = await bot.get_user_info(u)
                                                            usrprint += u.name + "\n"
                                                        toembed.add_field(
                                                            name = "Players ["+str(len(game["users"]))+"/"+str((gamesinfo[game["gameid"]])["maxplayers"])+"]",
                                                            value = usrprint,
                                                            inline = True
                                                        )
                                                        toembed.add_field(
                                                            name = "GAME OVER",
                                                            value = "No-one won!",
                                                            inline = True
                                                        )
                                                        await bot.edit_message(jjj,embed = toembed)
                                                    for jjjj in game["users"]:
                                                        unlimituser(jjjj)
                                                    matchmade = False
                                                if game["currentplay"] == len(game["users"])-1:
                                                    game["currentplay"] = 0
                                                else:
                                                    game["currentplay"] += 1
                                        elif (resp != None) and ((game["ctrls"])[1] == 1):
                                            #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< On reaction events here
                                            if game["gameid"] == "some emoji controlled game":
                                                r1 = ox.makeplay(((game["usrstatuses"])[game["currentplay"]]),resp.content)
                                            #DO NOT EDIT THIS COMMENT! THIS LINE IS REFERENCED FOR DYNAMIC FILE UPDATING!
                                            #reacteventhere
                                            if r1 != False:
                                                ((game["usrstatuses"])[game["currentplay"]]) = r1
                                                for usrs in game["usrstatuses"]:
                                                    for clmn in (usrs)["board"]:
                                                        concat = ""
                                                        for xzzx in clmn:
                                                            concat += xzzx
                                                        chnl = bot.get_channel(usrs["dmchannel"])
                                                        msgs = (usrs["messages"])[(usrs["board"]).index(clmn)]
                                                        msgobj = await bot.get_message(chnl,msgs)
                                                        if msgobj.content != concat:
                                                            await bot.edit_message(msgobj,concat)
                                                if game["gameid"] == "some emoji controlled game":
                                                    winchk = ox.wincond(((game["usrstatuses"])[game["currentplay"]]))
                                                #DO NOT EDIT THIS COMMENT! THIS LINE IS REFERENCED FOR DYNAMIC FILE UPDATING!
                                                #reactwincondhere
                                                if winchk == True:
                                                    for jjj in messages:
                                                        toembed = discord.Embed(
                                                            title = gamenameconst+" game created",
                                                            description = "Match ID: "+game["match_id"],
                                                            color = 10070709
                                                        )
                                                        usrprint = ""
                                                        for u in game["users"]:
                                                            u = await bot.get_user_info(u)
                                                            usrprint += u.name + "\n"
                                                        toembed.add_field(
                                                            name = "Players ["+str(len(game["users"]))+"/"+str((gamesinfo[game["gameid"]])["maxplayers"])+"]",
                                                            value = usrprint,
                                                            inline = True
                                                        )
                                                        usrget = await bot.get_user_info((game["users"])[game["currentplay"]])
                                                        toembed.add_field(
                                                            name = "GAME OVER",
                                                            value = usrget.name+" has won!",
                                                            inline = True
                                                        )
                                                        await bot.edit_message(jjj,embed = toembed)
                                                    for jjjj in game["users"]:
                                                        unlimituser(jjjj)
                                                    matchmade = False
                                                if game["gameid"] == "some emoji controlled game":
                                                    losschk = ox.losscond(((game["usrstatuses"])[game["currentplay"]]))
                                                #DO NOT EDIT THIS COMMENT! THIS LINE IS REFERENCED FOR DYNAMIC FILE UPDATING!
                                                #reactlosscondhere
                                                if losschk == True:
                                                    for jjj in messages:
                                                        toembed = discord.Embed(
                                                            title = gamenameconst+" game created",
                                                            description = "Match ID: "+game["match_id"],
                                                            color = 10070709
                                                        )
                                                        usrprint = ""
                                                        for u in game["users"]:
                                                            u = await bot.get_user_info(u)
                                                            usrprint += u.name + "\n"
                                                        toembed.add_field(
                                                            name = "Players ["+str(len(game["users"]))+"/"+str((gamesinfo[game["gameid"]])["maxplayers"])+"]",
                                                            value = usrprint,
                                                            inline = True
                                                        )
                                                        toembed.add_field(
                                                            name = "GAME OVER",
                                                            value = "No-one won!",
                                                            inline = True
                                                        )
                                                        await bot.edit_message(jjj,embed = toembed)
                                                    for jjjj in game["users"]:
                                                        unlimituser(jjjj)
                                                    matchmade = False
                                                if game["currentplay"] == len(game["users"])-1:
                                                    game["currentplay"] = 0
                                                else:
                                                    game["currentplay"] += 1
                                        else:
                                            game = leavegame(game,(game["users"])[game["currentplay"]])
                                            if len(game["users"]< (gamesinfo[game["gameid"]])["minplayers"]):
                                                matchmade = False
                                                for jjjj in game["users"]:
                                                    unlimituser(jjjj)
                                            else:
                                                if game["currentplay"] == len(game["users"])-1:
                                                    game["currentplay"] = 0
                                                else:
                                                    game["currentplay"] += 1
                                except Exception as e:
                                    for jjjj in game["users"]:
                                        unlimituser(jjjj)
                                    for zz in messagessafe:
                                        toembed = discord.Embed(
                                            title = gamenameconst+" game created",
                                            description = "Match ID: "+game["match_id"],
                                            color = 10070709
                                        )
                                        usrprint = ""
                                        for u in game["users"]:
                                            uu = await bot.get_user_info(u)
                                            usrprint += uu.name + "\n"
                                            if (game["users"]).index(u) == game["currentplay"]:
                                                plrname = uu.name
                                        toembed.add_field(
                                            name = "Players ["+str(len(game["users"]))+"/"+str((gamesinfo[game["gameid"]])["maxplayers"])+"]",
                                            value = usrprint,
                                            inline = True
                                        )
                                        ctrlmsg = (gamesinfo[game["gameid"]])["ctrlmsg"]
                                        toembed.add_field(
                                            name = "Game instructions:",
                                            value = ctrlmsg,
                                            inline = True
                                        )
                                        toembed.add_field(
                                            name = "GAME CRASHED",
                                            value = "The game encountered an internal script error and was forced to close. Please send the author this error message:\n`"+str(e)+"`",
                                            inline = True
                                        )
                                        await bot.edit_message(zz,embed = toembed)
                            else:
                                for jjj in messages:
                                    toembed = discord.Embed(
                                        title = gamenameconst+" game created",
                                        description = "Match ID: "+game["match_id"],
                                        color = 10070709
                                    )
                                    usrprint = ""
                                    for u in game["users"]:
                                        u = await bot.get_user_info(u)
                                        usrprint += u.name + "\n"
                                    toembed.add_field(
                                        name = "Players ["+str(len(game["users"]))+"/"+str((gamesinfo[game["gameid"]])["maxplayers"])+"]",
                                        value = usrprint,
                                        inline = True
                                    )
                                    toembed.add_field(
                                        name = "GAME OVER",
                                        value = "Lobby timed out.",
                                        inline = True
                                    )
                                    await bot.edit_message(jjj,embed = toembed)
                                for usrs in gamesafe["users"]:
                                    unlimituser(usrs)
                        else:
                            pass
                            # <<<<<<<<<<<< Singleplayer games go here, the code would be a minor variation of the MP code that removes the current player, players list and match ID arguments
                            # I would code a simple SP game but it'd be boring compared to tic-tac-toe
                            # So you get one MP game instead
                            # Please feel free to add your own SP game though <3
                elif (params[0] =="findgame") or (params[0] == "fg"):
                    if len(params) == 2:
                        gameid = findgame(params[1])
                        if gameid != False:
                            print("   game search started with game ID: "+gameid)
                            activegames = ((open("activegames","r")).read()).split("||")
                            potentgames = []
                            for x in activegames:
                                if (x != None) and (x != ""):
                                    print(x)
                                    if len((dict(ast.literal_eval(x))["gameid"]).rsplit("-")) <3:
                                        if dict(ast.literal_eval(x))["gameid"] == str(gameid):
                                            potentgames.append(dict(ast.literal_eval(x)))
                            filled = 0
                            currentgame = None
                            for z in potentgames:
                                if len(z["users"]) > filled:
                                    filled = len(z["users"])
                                    currentgame = z
                            if currentgame != None:
                                print("   attempting to join user "+message.author.id+" to game "+str(currentgame["match_id"]))
                                d = await bot.send_message(message.author,"selfjoin "+currentgame["match_id"]+" "+message.author.id)
                                await bot.delete_message(d)
                                limituser(message.author.id)
                            else:
                                await bot.send_message(message.channel,"couldn't find an active lobby for this game, you can make one with `~newgame "+params[1]+"`")
bot.run(discordtoken)
