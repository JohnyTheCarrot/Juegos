def firstrender():
    return([[":black_circle:",":black_circle:",":black_circle:",":black_circle:",":black_circle:",":black_circle:",":black_circle:"],[":black_circle:",":black_circle:",":black_circle:",":black_circle:",":black_circle:",":black_circle:",":black_circle:"],[":black_circle:",":black_circle:",":black_circle:",":black_circle:",":black_circle:",":black_circle:",":black_circle:"],[":black_circle:",":black_circle:",":black_circle:",":black_circle:",":black_circle:",":black_circle:",":black_circle:"],[":black_circle:",":black_circle:",":black_circle:",":black_circle:",":black_circle:",":black_circle:",":black_circle:"],[":black_circle:",":black_circle:",":black_circle:",":black_circle:",":black_circle:",":black_circle:",":black_circle:"]])
def makeplay(user,msg):
    #Carries out a "play" based on user input, returning false simply insinuates an invaild or no play was made. If the user says "exit" they leave the game
    if msg.lower() == "exit":
        return "exit"
    else:
        board = user["board"]
        translate = {"1":1,"2":2,"3":3,"4":4,"5":5,"6":6,"7":7}
        boardedit = None
        try:
            boardedit = (translate[msg.lower()])-1
        except:
            return False
        if boardedit != None:
            rownum = 0
            hle = False
            for row in board:
                if row[boardedit] == ":black_circle:":
                    hle = True
                    rtrn = rownum
                rownum += 1
            if hle == True:
                if user["team"] == 0:
                    (board[rtrn])[boardedit] = ":red_circle:"
                else:
                    (board[rtrn])[boardedit] = ":large_blue_circle:"
                user["board"] = board
                return user
            else:
                return False
        else:
            return False
def wincond(user):
    #Systematically checks for any 3 of the same emote in a row where one can't be the blank emote, stopping a blank board from being a win
    win = False
    board = user["board"]
    rowindx = 0
    for row in board:
        indx = 0
        for chip in row:
            if chip != ":black_circle:":
                try:
                    if chip == row[indx+1]:
                        if chip == row[indx+2]:
                            if chip == row[indx+3]:
                                win = True
                except:
                    pass
                try:
                    if chip == (board[rowindx + 1])[indx]:
                        if chip == (board[rowindx + 2])[indx]:
                            if chip == (board[rowindx + 3])[indx]:
                                win = True
                except:
                    pass
                try:
                    if chip == (board[rowindx + 1])[indx+1]:
                        if chip == (board[rowindx + 2])[indx+1]:
                            if chip == (board[rowindx + 3])[indx+1]:
                                win = True
                except:
                    pass
                try:
                    if chip == (board[rowindx + 1])[indx-1]:
                        if chip == (board[rowindx + 2])[indx-1]:
                            if chip == (board[rowindx + 3])[indx-1]:
                                win = True
                except:
                    pass
            indx += 1
        rowindx += 1
    return win
def losscond(user):
    # Simple function to check if the board is full, thus meaning there are no possible moves and no-one wins
    board = user["board"]
    loss = True
    for z in board:
        if ":black_circle:" in z:
            loss = False
            break
    return loss