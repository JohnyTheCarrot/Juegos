#user asking to start a game > Matchmaking server / client > game /w id > live updates via messages/reactions > render game via emoji in user DM's
import random
import discord
import ast
discordtoken = (open("_stream/token.cfg","r")).read()
bot = discord.Client()
games = ["testgame","test1","mp"]
gamesinfo = {"test1":{"minplayers":2,"maxplayers":4,"firstrender":[[0,0,0],[0,0,0],[0,0,0]]}}
def gamerun(game,cmd,args):
    if cmd == "firstrender":
        crgme = gamesinfo[game]
        return crgme["firstrender"]
def findgame(game_name):
    if game_name in games:
        return games[games.index(game_name)+1]
    else:
        return False
def makegame(game_id,privacy):
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
        exinf = (open("_stream/activegames","r")).read()
        matchw = (open("_stream/activegames","w")).write(exinf+"||"+str(matchinfo))
        return matchinfo
    else:
        return None
def closematch(match_id):
    activegames = ((open("_stream/activegames","r")).read()).split("||")
    concat = ""
    for x in activegames:
        if (x != None) and (x != ""):
            if dict(ast.literal_eval(x))["match_id"] == match_id:
                pass
            else:
                concat += "||" + str(x)
    activew = (open("_stream/activegames","w")).write(concat)
def tryjoin(message):
    if message.author.bot == False:
        if message.content.startswith("~"):
            params = (message.content.replace("~","")).rsplit()
            if len(params) == 2:
                if params[0] == "joinid":
                    try:
                        match = (open("_stream/activegames","r").read())
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
            match = (open("_stream/activegames","r").read())
            if params[1] in match:
                return True
            else:
                return False
        except:
            return False
    return False
def joingame(matchinfo,user_id):
    if user_id not in matchinfo["users"]:
        matchinfo["users"].append(user_id)
        updategame(matchinfo["match_id"],matchinfo)
        return matchinfo
    else:
        return None
def updategame(match_id,matchinfo):
    activegames = ((open("_stream/activegames","r")).read()).split("||")
    concat = ""
    for x in activegames:
        if (x != None) and (x != ""):
            if dict(ast.literal_eval(x))["match_id"] == match_id:
                concat += "||"+str(matchinfo)
            else:
                concat += "||" + str(x)
    activew = (open("_stream/activegames","w")).write(concat)
def leavegame(matchinfo,user_id):
    if user_id in matchinfo["users"]:
        matchinfo["users"].remove(user_id)
        return matchinfo
    else:
        return None
def firstrender(rows):
    rowmsgs = []
    for x in rows:
        concat = ""
        for z in x:
            if z == 0:
                z = "⬛"
            concat += z
        rowmsgs.append(concat)
    return rowmsgs
@bot.event
async def on_ready():
    print("connected")
@bot.event
async def on_message(message):
    if message.author.bot == False:
        if message.content.startswith("~"):
            print("command passed")
            params = (message.content.replace("~","")).rsplit()
            if params[0] == "newgame":
                print("   command ID: Newgame")
                if len(params) > 1:
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
                        toembed = discord.Embed(
                            title = params[1]+" game created",
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
                        gameinit = await bot.send_message(message.author,embed = toembed)
                        messages = [gameinit]
                        while resp != None:
                            resp = await bot.wait_for_message(check = tryjoin,timeout = game["timeout"])
                            if resp != None:
                                toembed = discord.Embed(
                                    title = params[1]+" game created",
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
                                    useradd = await bot.get_user_info(params[2])
                                    addmsg = await bot.send_message(useradd,embed = toembed)
                                    resp1 = joingame(game,useradd.id)
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
                                    title = params[1]+" game created",
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
                                await bot.edit_message(m,embed = toembed)
                        closematch(game["match_id"])
                        print("match with ID: "+game["match_id"]+" closed from matchmaking")
                        if matchmade == True:
                            game["usermessages"] = []
                            for dm in game["users"]:
                                msgs = []
                                tosend = firstrender(gamerun(game["gameid"],"firstrender",None))
                                usr = await bot.get_user_info(dm)
                                for ms in tosend:
                                    msgs.append(await bot.send_message(usr,ms))
                                dictadd = {dm:msgs}
                                (game["usermessages"]).append(dictadd)
            elif params[0] == "findgame":
                if len(params) == 2:
                    gameid = findgame(params[1])
                    if gameid != False:
                        print("   game search started with game ID: "+gameid)
                        activegames = ((open("_stream/activegames","r")).read()).split("||")
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
                            d = await bot.send_message(message.author,"selfjoin "+currentgame["match_id"]+" "+message.author.id)
                            await bot.delete_message(d)
                        else:
                            await bot.send_message(message.channel,"couldn't find an active lobby for this game, you can make one with `~newgame "+params[1]+"`")
bot.run(discordtoken)