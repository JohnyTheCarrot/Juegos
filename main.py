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

bot_author_id = "249287049482338305" # <<<<<<<<<<<<<<<< IF YOU ARE MANUALLY HOSTING, REPLACE THIS STRING WITH YOUR OWN DISCORD ID OR YOU WILL NOT BE ABLE TO USE DEV COMMANDS!
discord_token = open("token.cfg", "r").read()
if discord_token == "":
    discord_token = input("No bot token detected, please set it now: ")
    open("token.cfg","w").write(discord_token)
bot = discord.Client()
games = list(ast.literal_eval(open("gameslist.cfg","r").read()))
games_info = dict(ast.literal_eval(open("gamesdict.cfg", "r").read()))
print("Flushing ratleimiter & matchmaking file...")
open("lookingusers","w").write("")
open("activegames","w").write("")

def limit_user(id):
    #This function is used to add a user who has created a game or joined a game to the one active game per-person ratelimit
    pre = (open("lookingusers","r")).read()
    pre = pre + " " + id
    open("lookingusers","w").write(pre)

def unlimit_user(id):
    #This function is used to remove a user who has left or finished a game from the one active game per-person ratelimit
    pre = open("lookingusers","r").read()
    pre = pre.replace(" "+id,"")
    open("lookingusers","w").write(pre)

def check_limited(id):
    #This function checks if a user currently limited by the one active game per-person ratelimit
    pre = open("lookingusers","r").read()
    if id in pre:
        return True
    else:
        return False

def find_game(game_name):
    #this function compares given game names to a set game ID so one game ID can have multiple aliases
    if game_name in games:
        return games[games.index(game_name)+1]
    else:
        return False

def make_game(game_id, privacy):
    #This function will create a matchmaking match for a given game
    vars = {"game_id":game_id,"privacy":privacy}
    if game_id is not None:
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
    if vars["mp"]:
        match_id = vars["game_id"] + "-"
        token = ""
        while len(token) < 10:
            token += str(random.randint(0,9))
        match_id+=str(token)
        if vars["privacy"] is not None and vars["pass"] is not None:
                match_id += "-" + vars["pass"]
        matchinfo = {
            "timeout": 300,
            "match_id": match_id,
            "users": [creator_id],
            "gameid": vars["game_id"]
        }
        matchinfo["ctrls"] = (games_info[vars["game_id"]])["cscheme"]
        if games_info[vars["game_id"]]["cscheme"][0] == 1:
            vars["reactions"] == games_info[vars["game_id"]]["reactions"]
        exinf = open("activegames","r").read()
        open("activegames","w").write(exinf+"||"+str(matchinfo))
        return matchinfo
    else:
        return None

def close_match(match_id):
    #This function removes a matchmaking dict from the global matchmaking file
    print("looking to close match: "+match_id)
    activegames = open("activegames","r").read().split("||")
    concat = ""
    for x in activegames:
        if x is not None and x != "":
            if dict(ast.literal_eval(x))["match_id"] == match_id:
                print(f"   match identified with ID: {dict(ast.literal_eval(x))['match_id']} = closeID {match_id}")
            else:
                print(f"   match identified with ID: {dict(ast.literal_eval(x))['match_id']}")
                concat += "||" + str(x)
    open("activegames","w").write(concat)

def try_join(message):
    #This function attempts to parse for a matchmaking session search from user messages
    if not message.author.bot:
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
                    if not find_game(params[1]):
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

def join_game(match_info, user_id):
    #This function attempts to add a user to a matchmaking session, requires the user isn't already in it
    if user_id not in match_info["users"]:
        match_info["users"].append(user_id)
        update_game(match_info["match_id"], match_info)
        return match_info
    else:
        return None

def update_game(match_id, match_info):
    #this function updates a matchmaking dict from the global matchmaking file
    active_games = ((open("activegames","r")).read()).split("||")
    concat = ""
    for x in active_games:
        if x is not None and x != "":
            if dict(ast.literal_eval(x))["match_id"] == match_id:
                concat += "||"+str(match_info)
            else:
                concat += "||" + str(x)
    (open("activegames","w")).write(concat)

def leave_game(match_info, user_id):
    #This function removes a user from a matchmaking session
    if user_id in match_info["users"]:
        match_info["users"].remove(user_id)
        return match_info
    else:
        return None

@bot.event
async def on_ready():
    #Basic custom presence because a e s t h e t i c s
    print("Discord connected")
    game = discord.Game(name = "panley.co.uk/juegos", type = 3, url = "https://panley.co.uk/juegos")
    await bot.change_presence(game = game)

@bot.event
async def on_message(message):
    if not check_limited(message.author.id):
        if not message.author.bot:
            if message.content.startswith("~"):
                params = message.content.replace("~","").rsplit()
                if params[0] == "help":
                    to_embed = discord.Embed(
                        title = "Juegos Commands",
                        description = "format: `~command|alias <required argument> (optional argument)`\n`~help` - Shows this!\n`~newgame|ng <game name> (private)` - Create a new game for the given game name\n`~findgame|fg <game name>` - Finds a public match for the given game name\n`~joinid <match ID>` - Joins the user to a given match/private match\n`~games` - Lists all games present on the bot\n`~addgamefile` - **Bot owner only!** lets the bot owner dynamically add a new game to the bot (Experimental)",
                        color = 7506394
                    )
                    to_embed.add_field(
                        name = "Programmed by Panley#3274 in Python",
                        value = "[Creators server](https://discord.gg/tBs8MRE) | [Official website](https://panley.co.uk/juegos) | [GitHub](https://github.com/panley01/Juegos)"
                    )
                    await bot.send_message(message.channel,embed = to_embed)
                elif params[0] == "games":
                    to_embed = discord.Embed(
                        title = "Installed Games",
                        color = 7506394
                    )
                    for x in games_info:
                        x = games_info[x]
                        to_embed.add_field(
                            name = f"**{x['selfname']}** - Aliases: {x['aliases']}",
                            value = f"Created by {x['creator']}\n{x['desc']}\nPlayers - Min: {str(x['minplayers'])} Max: {str(x['maxplayers'])}"
                        )
                    await bot.send_message(message.channel,embed = to_embed)
                elif params[0] == "addgamefile" and message.author.id == bot_author_id:
                    await bot.send_message(message.channel,"**THIS FEATURE IS EXPERIMENTAL AND CURRENTLY DISABLED!**")
                elif params[0] == "newgame" or params[0] == "ng":
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
                        game_id = find_game(params[1])
                        game = make_game(game_id, privacy = priv)
                        if game["mp"]:
                            game = matchmaking(game,message.author.id)
                            resp = ""
                            newgame_const = params[1]
                            to_embed = discord.Embed(
                                title = f"{newgame_const} game created",
                                description = f"Match ID: {game['match_id']}",
                                color = 7506394
                            )
                            usr_print = ""
                            for u in game["users"]:
                                u = await bot.get_user_info(u)
                                usr_print += u.name + "\n"
                            to_embed.add_field(
                                name = f"Players [{str(len(game['users']))}/{str((games_info[game['gameid']])['maxplayers'])}]",
                                value = usr_print
                            )
                            game_init = await bot.send_message(message.author,embed = to_embed)
                            messages = [game_init]
                            limit_user(message.author.id)
                            while resp is not None:
                                resp = await bot.wait_for_message(check = try_join, timeout = game["timeout"])
                                if resp is not None:
                                    print("   Active lobby recived join request: "+resp.content)
                                    to_embed = discord.Embed(
                                        title = newgame_const+" game created",
                                        description = f"Match ID: {game['match_id']}"
                                    )
                                    usr_print = ""
                                    for u in game["users"]:
                                        u = await bot.get_user_info(u)
                                        usr_print += u.name + "\n"
                                    to_embed.add_field(
                                        name = f"Players [{str(len(game['users']))}/{str(games_info[game['gameid']]['maxplayers'])}]",
                                        value = usr_print
                                    )
                                    params = (resp.content.replace("~","")).rsplit()
                                    if not resp.author.bot:
                                        resp1 = join_game(game, resp.author.id)
                                        add_msg = await bot.send_message(resp.author,embed = to_embed)
                                    else:
                                        game_id = params[1]
                                        if game_id == game["match_id"]:
                                            user_add = await bot.get_user_info(params[2])
                                            add_msg = await bot.send_message(user_add,embed = to_embed)
                                            resp1 = join_game(game, user_add.id)
                                        else:
                                            resp1 = None
                                    if resp1 is not None:
                                        game = resp1
                                        messages.append(add_msg)
                                else:
                                    if len(game["users"]) >= games_info[game["gameid"]]["minplayers"]:
                                        match_made = True
                                    else:
                                        match_made = False
                                if len(game["users"]) >= games_info[game["gameid"]]["maxplayers"]:
                                    match_made = True
                                    resp = None
                                for m in messages:
                                    to_embed = discord.Embed(
                                        title = newgame_const+" game created",
                                        description = f"Match ID: {game['match_id']}",
                                        color = 7506394
                                    )
                                    usr_print = ""
                                    for u in game["users"]:
                                        u = await bot.get_user_info(u)
                                        usr_print += u.name + "\n"
                                    to_embed.add_field(
                                        name = f"Players [{str(len(game['users']))}/{str((games_info[game['gameid']])['maxplayers'])}]",
                                        value = usr_print
                                    )
                                    await bot.edit_message(m, embed = to_embed)
                            close_match(game["match_id"])
                            print(f"match with ID: {game['match_id']} closed from matchmaking")
                            if match_made:
                                for zz in messages:
                                    to_embed = discord.Embed(
                                        title = f"{newgame_const} game created",
                                        description = f"Match ID: {game['match_id']}",
                                        color = 10070709
                                    )
                                    usr_print = ""
                                    for u in game["users"]:
                                        u = await bot.get_user_info(u)
                                        usr_print += u.name + "\n"
                                    to_embed.add_field(
                                        name = f"Players [{str(len(game['users']))}/{str((games_info[game['gameid']])['maxplayers'])}]",
                                        value = usr_print,
                                        inline = True
                                    )
                                    ctrl_msg = games_info[game["gameid"]]["ctrlmsg"]
                                    to_embed.add_field(
                                        name = "Game instructions:",
                                        value = ctrl_msg,
                                        inline = True
                                    )
                                    to_embed.add_field(
                                        name = "Rendering boards...",
                                        value = "This may take some time depending on game complexity and bot usage",
                                        inline = True
                                    )
                                    await bot.edit_message(zz,embed = to_embed)
                                user_statuses = []
                                #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Initial board rendering is declared here
                                game_safe = game
                                messages_safe = messages
                                try:
                                    if game["gameid"] == "ox":
                                        to_print = ox.firstrender()
                                    elif game["gameid"] == "cn4":
                                        to_print = cn4.firstrender()
                                    #DO NOT EDIT THIS COMMENT! THIS LINE IS REFERENCED FOR DYNAMIC FILE UPDATING!
                                    #initrenderhere
                                    for plr in game["users"]:
                                        chnl = await bot.get_user_info(plr)
                                        msgs = []
                                        for rdr in to_print:
                                            concat = ""
                                            for rdr1 in rdr:
                                                concat += rdr1
                                            msgr = await bot.send_message(chnl, concat)
                                            msgs.append(msgr.id)
                                            dmchl = msgr.channel.id
                                        if game["ctrls"][0] == 1:
                                            for emji in game["reactions"]:
                                                await bot.add_reaction(msgr,emji)
                                        userinf = {"id": plr,"board": to_print, "messages": msgs,"dmchannel": dmchl,"team": game["users"].index(plr)}
                                        user_statuses.append(userinf)
                                        game["usrstatuses"] = user_statuses
                                        game["currentplay"] = 0
                                    print(f"Game started with ID: {str(game['match_id'])}")
                                    while match_made:
                                        for zz in messages:
                                            to_embed = discord.Embed(
                                                title = newgame_const+" game created",
                                                description = "Match ID: "+game["match_id"],
                                                color = 10070709
                                            )
                                            usr_print = ""
                                            for u in game["users"]:
                                                uu = await bot.get_user_info(u)
                                                usr_print += uu.name + "\n"
                                                if game["users"].index(u) == game["currentplay"]:
                                                    plr_name = uu.name
                                            to_embed.add_field(
                                                name = f"Players [{str(len(game['users']))}/{str((games_info[game['gameid']])['maxplayers'])}]",
                                                value = usr_print,
                                                inline = True
                                            )
                                            ctrl_msg = games_info[game["gameid"]]["ctrlmsg"]
                                            to_embed.add_field(
                                                name = "Game instructions:",
                                                value = ctrl_msg,
                                                inline = True
                                            )
                                            to_embed.add_field(
                                                name = "Game active",
                                                value = f"{plr_name}'s turn",
                                                inline = True
                                            )
                                            await bot.edit_message(zz, embed = to_embed)
                                        user_wait_for = await bot.get_user_info(game["users"][game["currentplay"]])
                                        if game["ctrls"][0] == 0:
                                            if game["ctrls"][1] == 0:
                                                resp = await bot.wait_for_message(author = user_wait_for, timeout = game["timeout"])
                                            else:
                                                resp = await bot.wait_for_message(author = user_wait_for, timeout = 1)
                                        elif game["ctrls"][0] == 1:
                                            if game["ctrls"][1] == 0:
                                                resp = await bot.wait_for_reaction(user = user_wait_for, timeout = game["timeout"])
                                            else:
                                                resp = await bot.wait_for_reaction(user = user_wait_for, timeout = 1)
                                        if str(resp) == "exit":
                                            #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Handling for a user leaving the game by choice
                                            game = leave_game(game, game["users"][game["currentplay"]])
                                            if len(game["users"]) < games_info[game["gameid"]]["minplayers"]:
                                                match_made = False
                                                for jjjj in game["users"]:
                                                    unlimit_user(jjjj)
                                                for jjj in messages:
                                                    to_embed = discord.Embed(
                                                        title = newgame_const+" game created",
                                                        description = f"Match ID: {game['match_id']}",
                                                        color = 10070709
                                                    )
                                                    usr_print = ""
                                                    for u in game["users"]:
                                                        u = await bot.get_user_info(u)
                                                        usr_print += u.name + "\n"
                                                    to_embed.add_field(
                                                        name = f"Players [{str(len(game['users']))}/{str((games_info[game['gameid']])['maxplayers'])}]",
                                                        value = usr_print,
                                                        inline = True
                                                    )
                                                    to_embed.add_field(
                                                        name = "GAME OVER",
                                                        value = "Too many users disconnected.",
                                                        inline = True
                                                    )
                                                    await bot.edit_message(jjj, embed = to_embed)
                                            else:
                                                if game["currentplay"] == len(game["users"])-1:
                                                    game["currentplay"] = 0
                                                else:
                                                    game["currentplay"] += 1
                                        elif resp is not None and game["ctrls"][1] == 0:
                                            #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< On message events here
                                            if game["gameid"] == "ox":
                                                r1 = ox.makeplay(game["usrstatuses"][game["currentplay"]],resp.content)
                                            elif game["gameid"] == "cn4":
                                                r1 = cn4.makeplay(game["usrstatuses"][game["currentplay"]], resp.content)
                                            #DO NOT EDIT THIS COMMENT! THIS LINE IS REFERENCED FOR DYNAMIC FILE UPDATING!
                                            #msgeventhere
                                            if not r1:
                                                game["usrstatuses"][game["currentplay"]] = r1
                                                for usrs in game["usrstatuses"]:
                                                    for clmn in usrs["board"]:
                                                        concat = ""
                                                        for xzzx in clmn:
                                                            concat += xzzx
                                                        chnl = bot.get_channel(usrs["dmchannel"])
                                                        msgs = usrs["messages"][usrs["board"].index(clmn)]
                                                        msgobj = await bot.get_message(chnl,msgs)
                                                        if msgobj.content != concat:
                                                            await bot.edit_message(msgobj,concat)
                                                if game["gameid"] == "ox":
                                                    winchk = ox.wincond(game["usrstatuses"][game["currentplay"]])
                                                elif game["gameid"] == "cn4":
                                                    winchk = cn4.wincond(game["usrstatuses"][game["currentplay"]])
                                                #DO NOT EDIT THIS COMMENT! THIS LINE IS REFERENCED FOR DYNAMIC FILE UPDATING!
                                                #msgwincondhere
                                                if winchk:
                                                    for jjj in messages:
                                                        to_embed = discord.Embed(
                                                            title = newgame_const+" game created",
                                                            description = "Match ID: "+game["match_id"],
                                                            color = 10070709
                                                        )
                                                        usr_print = ""
                                                        for u in game["users"]:
                                                            u = await bot.get_user_info(u)
                                                            usr_print += u.name + "\n"
                                                        to_embed.add_field(
                                                            name = f"Players [{str(len(game['users']))}/{str((games_info[game['gameid']])['maxplayers'])}]",
                                                            value = usr_print,
                                                            inline = True
                                                        )
                                                        usr_get = await bot.get_user_info((game["users"])[game["currentplay"]])
                                                        to_embed.add_field(
                                                            name = "GAME OVER",
                                                            value = usr_get.name+" has won!",
                                                            inline = True
                                                        )
                                                        await bot.edit_message(jjj,embed = to_embed)
                                                    for jjjj in game["users"]:
                                                        unlimit_user(jjjj)
                                                    match_made = False
                                                if game["gameid"] == "ox":
                                                    losschk = ox.losscond(game["usrstatuses"][game["currentplay"]])
                                                elif game["gameid"] == "cn4":
                                                    losschk = cn4.losscond(game["usrstatuses"][game["currentplay"]])
                                                #DO NOT EDIT THIS COMMENT! THIS LINE IS REFERENCED FOR DYNAMIC FILE UPDATING!
                                                #msglosscondhere
                                                if losschk:
                                                    for jjj in messages:
                                                        to_embed = discord.Embed(
                                                            title = newgame_const+" game created",
                                                            description = f"Match ID: {game['match_id']}",
                                                            color = 10070709
                                                        )
                                                        usr_print = ""
                                                        for u in game["users"]:
                                                            u = await bot.get_user_info(u)
                                                            usr_print += u.name + "\n"
                                                        to_embed.add_field(
                                                            name = f"Players [{str(len(game['users']))}/{str((games_info[game['gameid']])['maxplayers'])}]",
                                                            value = usr_print,
                                                            inline = True
                                                        )
                                                        to_embed.add_field(
                                                            name = "GAME OVER",
                                                            value = "No-one won!",
                                                            inline = True
                                                        )
                                                        await bot.edit_message(jjj,embed = to_embed)
                                                    for jjjj in game["users"]:
                                                        unlimit_user(jjjj)
                                                    match_made = False
                                                if game["currentplay"] == len(game["users"])-1:
                                                    game["currentplay"] = 0
                                                else:
                                                    game["currentplay"] += 1
                                        elif resp is not None and game["ctrls"][1] == 1:
                                            #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< On reaction events here
                                            if game["gameid"] == "some emoji controlled game":
                                                r1 = ox.makeplay(game["usrstatuses"][game["currentplay"]],resp.content)
                                            #DO NOT EDIT THIS COMMENT! THIS LINE IS REFERENCED FOR DYNAMIC FILE UPDATING!
                                            #reacteventhere
                                            if not r1:
                                                ((game["usrstatuses"])[game["currentplay"]]) = r1
                                                for usrs in game["usrstatuses"]:
                                                    for clmn in usrs["board"]:
                                                        concat = ""
                                                        for xzzx in clmn:
                                                            concat += xzzx
                                                        chnl = bot.get_channel(usrs["dmchannel"])
                                                        msgs = usrs["messages"][usrs["board"].index(clmn)]
                                                        msgobj = await bot.get_message(chnl, msgs)
                                                        if msgobj.content != concat:
                                                            await bot.edit_message(msgobj, concat)
                                                if game["gameid"] == "some emoji controlled game":
                                                    winchk = ox.wincond(game["usrstatuses"][game["currentplay"]])
                                                #DO NOT EDIT THIS COMMENT! THIS LINE IS REFERENCED FOR DYNAMIC FILE UPDATING!
                                                #reactwincondhere
                                                if winchk:
                                                    for jjj in messages:
                                                        to_embed = discord.Embed(
                                                            title = newgame_const+" game created",
                                                            description = f"Match ID: {game['match_id']}",
                                                            color = 10070709
                                                        )
                                                        usr_print = ""
                                                        for u in game["users"]:
                                                            u = await bot.get_user_info(u)
                                                            usr_print += u.name + "\n"
                                                        to_embed.add_field(
                                                            name = f"Players [{str(len(game['users']))}/{str((games_info[game['gameid']])['maxplayers'])}]",
                                                            value = usr_print,
                                                            inline = True
                                                        )
                                                        usr_get = await bot.get_user_info((game["users"])[game["currentplay"]])
                                                        to_embed.add_field(
                                                            name = "GAME OVER",
                                                            value = f"{usr_get.name} has won!",
                                                            inline = True
                                                        )
                                                        await bot.edit_message(jjj,embed = to_embed)
                                                    for jjjj in game["users"]:
                                                        unlimit_user(jjjj)
                                                    match_made = False
                                                if game["gameid"] == "some emoji controlled game":
                                                    losschk = ox.losscond(game["usrstatuses"][game["currentplay"]])
                                                #DO NOT EDIT THIS COMMENT! THIS LINE IS REFERENCED FOR DYNAMIC FILE UPDATING!
                                                #reactlosscondhere
                                                if losschk:
                                                    for jjj in messages:
                                                        to_embed = discord.Embed(
                                                            title = f"{newgame_const} game created",
                                                            description = f"Match ID: {game['match_id']}",
                                                            color = 10070709
                                                        )
                                                        usr_print = ""
                                                        for u in game["users"]:
                                                            u = await bot.get_user_info(u)
                                                            usr_print += u.name + "\n"
                                                        to_embed.add_field(
                                                            name = f"Players [{str(len(game['users']))}/{str((games_info[game['gameid']])['maxplayers'])}]",
                                                            value = usr_print,
                                                            inline = True
                                                        )
                                                        to_embed.add_field(
                                                            name = "GAME OVER",
                                                            value = "No-one won!",
                                                            inline = True
                                                        )
                                                        await bot.edit_message(jjj,embed = to_embed)
                                                    for jjjj in game["users"]:
                                                        unlimit_user(jjjj)
                                                    match_made = False
                                                if game["currentplay"] == len(game["users"])-1:
                                                    game["currentplay"] = 0
                                                else:
                                                    game["currentplay"] += 1
                                        else:
                                            game = leave_game(game, (game["users"])[game["currentplay"]])
                                            if len(game["users"]) < games_info[game["gameid"]]["minplayers"]:
                                                match_made = False
                                                for jjjj in game["users"]:
                                                    unlimit_user(jjjj)
                                            else:
                                                if game["currentplay"] == len(game["users"])-1:
                                                    game["currentplay"] = 0
                                                else:
                                                    game["currentplay"] += 1
                                except Exception as e:
                                    for jjjj in game["users"]:
                                        unlimit_user(jjjj)
                                    for zz in messages_safe:
                                        to_embed = discord.Embed(
                                            title = newgame_const+" game created",
                                            description = f"Match ID: {game['match_id']}",
                                            color = 10070709
                                        )
                                        usr_print = ""
                                        for u in game["users"]:
                                            uu = await bot.get_user_info(u)
                                            usr_print += uu.name + "\n"
                                            if (game["users"]).index(u) == game["currentplay"]:
                                                plr_name = uu.name
                                        to_embed.add_field(
                                            name = f"Players [{str(len(game['users']))}/{str((games_info[game['gameid']])['maxplayers'])}]",
                                            value = usr_print,
                                            inline = True
                                        )
                                        ctrl_msg = games_info[game["gameid"]]["ctrlmsg"]
                                        to_embed.add_field(
                                            name = "Game instructions:",
                                            value = ctrl_msg,
                                            inline = True
                                        )
                                        to_embed.add_field(
                                            name = "GAME CRASHED",
                                            value = "The game encountered an internal script error and was forced to close. Please send the author this error message:\n`"+str(e)+"`",
                                            inline = True
                                        )
                                        await bot.edit_message(zz, embed = to_embed)
                            else:
                                for jjj in messages:
                                    to_embed = discord.Embed(
                                        title = f"{newgame_const} game created",
                                        description = f"Match ID: {game['match_id']}",
                                        color = 10070709
                                    )
                                    usr_print = ""
                                    for u in game["users"]:
                                        u = await bot.get_user_info(u)
                                        usr_print += u.name + "\n"
                                    to_embed.add_field(
                                        name = f"Players [{str(len(game['users']))}/{str((games_info[game['gameid']])['maxplayers'])}]",
                                        value = usr_print,
                                        inline = True
                                    )
                                    to_embed.add_field(
                                        name = "GAME OVER",
                                        value = "Lobby timed out.",
                                        inline = True
                                    )
                                    await bot.edit_message(jjj, embed = to_embed)
                                for usrs in game_safe["users"]:
                                    unlimit_user(usrs)
                        else:
                            pass
                            # <<<<<<<<<<<< Singleplayer games go here, the code would be a minor variation of the MP code that removes the current player, players list and match ID arguments
                            # I would code a simple SP game but it'd be boring compared to tic-tac-toe
                            # So you get one MP game instead
                            # Please feel free to add your own SP game though <3
                elif params[0] =="findgame" or params[0] == "fg":
                    if len(params) == 2:
                        game_id = find_game(params[1])
                        if not game_id:
                            print(f"   game search started with game ID: {game_id}")
                            active_games = open("activegames","r").read().split("||")
                            potent_games = []
                            for x in active_games:
                                if x is not None and x != "":
                                    print(x)
                                    if len(dict(ast.literal_eval(x))["gameid"].rsplit("-")) <3: #lol look it's a heart
                                        if dict(ast.literal_eval(x))["gameid"] == str(game_id):
                                            potent_games.append(dict(ast.literal_eval(x)))
                            filled = 0
                            current_game = None
                            for z in potent_games:
                                if len(z["users"]) > filled:
                                    filled = len(z["users"])
                                    current_game = z
                            if current_game is not None:
                                print(f"   attempting to join user {message.author.id} to game {str(current_game['match_id'])}")
                                d = await bot.send_message(message.author,f"selfjoin {current_game['match_id']} {message.author.id}")
                                await bot.delete_message(d)
                                limit_user(message.author.id)
                            else:
                                await bot.send_message(message.channel, f"couldn't find an active lobby for this game, you can make one with `~newgame {params[1]}`")
bot.run(discord_token)
