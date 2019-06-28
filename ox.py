def firstrender():
    #Initial render that essentially declares the board size and the status of the board before any moves a carried out
    return([[":black_large_square:",":black_large_square:",":black_large_square:"],[":black_large_square:",":black_large_square:",":black_large_square:"],[":black_large_square:",":black_large_square:",":black_large_square:"]])
def makeplay(user,msg):
    #Carries out a "play" based on user input, returning false simply insinuates an invaild or no play was made. If the user says "exit" they leave the game
    if msg.lower() == "exit":
        return "exit"
    else:
        board = user["board"]
        translate = {"tl":[0,0],"tm":[0,1],"tr":[0,2],"ml":[1,0],"mm":[1,1],"mr":[1,2],"bl":[2,0],"bm":[2,1],"br":[2,2]}
        boardedit = None
        try:
            boardedit = translate[msg.lower()]
        except:
            return False
        if boardedit != None:
            clmn = board[boardedit[0]]
            blck = clmn[boardedit[1]]
            if blck == ":black_large_square:":
                if user["team"] == 0:
                    blck = ":regional_indicator_x:"
                else:
                    blck = ":o2:"
                (board[boardedit[0]])[boardedit[1]] = blck
                user["board"] = board
                return user
            else:
                return False
        else:
            return False
def wincond(user):
    #Systematically checks for any 3 of the same emote in a row where one can't be the blank emote, stopping a blank board from being a win
    win = False
    rowchk = [[],[],[]]
    diagchk = [[],[]]
    board = user["board"]
    for clmnchk in board:
        rowchk[0].append(clmnchk[0])
        rowchk[1].append(clmnchk[1])
        rowchk[2].append(clmnchk[2])
        if board.index(clmnchk) == 0:
            diagchk[0].append(clmnchk[0])
            diagchk[1].append(clmnchk[2])
        elif board.index(clmnchk) == 1:
            diagchk[0].append(clmnchk[1])
            diagchk[1].append(clmnchk[1])
        elif board.index(clmnchk) == 2:
            diagchk[0].append(clmnchk[2])
            diagchk[1].append(clmnchk[0])
    for clmnchk in board:
        if ((clmnchk[0] == clmnchk[1]) and (clmnchk[1] == clmnchk[2]))and(clmnchk[0] != ":black_large_square:"):
            win = True
    for v in rowchk:
        if ((v[0] == v[1]) and (v[1] == v[2]))and(v[0] != ":black_large_square:"):
            win = True
    for vv in diagchk:
        if ((vv[0] == vv[1]) and (vv[1] == vv[2]))and(vv[0] != ":black_large_square:"):
            win = True
    if win == True:
        print("Win condition met")
        return True
    else:
        return False
def losscond(user):
    # Simple function to check if the board is full, thus meaning there are no possible moves and no-one wins
    board = user["board"]
    loss = True
    for z in board:
        if ":black_large_square:" in z:
            loss = False
    return loss