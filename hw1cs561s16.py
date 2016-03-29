#python
#-*- coding: UTF-8 -*-
import sys
import pdb
import copy
import time

DEBUG =0   # 1: debug readFile  2: PRINT BOARD INFO
class IOclass(object):
    def __init__(self):
        pass
    def readFile(self,inputname):
        '''
        this function will read all the infomation into the class BoardClass
        return : class BoardClass
        '''
        try:
            #if DEBUG == True:
            #    pdb.set_trace()
            #if ".txt" not in inputname:
            #    inputname+=".txt"
            with open(inputname,"r") as f:
                lines = f.read().splitlines()
            if DEBUG == 1:
                for i in lines:
                    print i
            return lines
        except:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print exc_type,exc_obj,exc_tb.tb_lineno
            print "no such file"
            return False
    def writeFile(self,outputname,lis):
        try:
            #if ".txt" not in outputname:
            #    outputname+=".txt" 
            fjob = open(outputname,"w")
            le = len(lis)
            for i in lis[:le-1]:
                fjob.write("".join(i)+"\n")
            fjob.write("".join(lis[-1]))
            fjob.close()
        except:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print exc_type,exc_obj,exc_tb.tb_lineno
            print "write failed"
            return False
class PlayerClass(object):
    def __init__(self,player,algo,cutoffdepth):
        self.player = player
        self.algo = int(algo)
        self.cutoffdepth =int(cutoffdepth)
        self.score = 0
        self.node = set()
    def printPlayer(self):
        print "Name: ", self.player," alog: ",self.algo," cut off depth:",self.cutoffdepth,
        print "score: ", self.score
        print "next node:", self.node
class BoardClass(object):
    def __init__(self,tp,boardscore,freenode,playerlist):
        self.type =int(tp)
        self.playerlist = playerlist
        self.boardscore = boardscore
        self.freenode = freenode
        self.col = "ABCDE"
        self.row = "12345"
    def printBCInfo(self):
        print "game type: ",self.type
        print "player 1---",
        self.playerlist[0].printPlayer()
        print "player 2---",
        if self.playerlist[1]:
            self.playerlist[1].printPlayer() 
        else:
            print None
        def subboard(typ,bd):
            print "boardtype:",typ
            for i in bd:
                print "     ",i
        subboard("points in board",self.boardscore)
        print "free node:",self.freenode
        #subboard("occpuation in board", self.freenode)
class GameControl(object):
    def __init__(self):
        self.IO = IOclass()
        self.BC = None
        self.trace_state = []
        self.lasttrace =None
    def initialize(self,argv):
        #argv = sys.argv
        if len(argv)!=3 or argv[1]!="-i":
            print "parameter is not correct"
            return False
        inputname = argv[2]
        lines = self.IO.readFile(inputname)
        if not lines:return False
        return self.construct(lines)
    def construct(self,lines):
        def subcon(m,n,k,playerlist):
            bdsc,bdocp=[],set()
            for i in xrange(m,n):
                bdsc.append([int(j) for j in lines[i].split(" ")])
            for m in xrange(n,k):
                i = m-n
                for j in xrange(5):
                    val = lines[m][j]
                    if val!="*":
                        val = 0 if val == playerlist[0].player else 1
                        playerlist[val].score+=bdsc[i][j]
                        playerlist[val].node.add((i,j)) 
                    else:
                        bdocp.add((i,j))   
            return bdsc,bdocp         
        try:    
            playerlist=[None,None]
            bdsc,bdocp = None,None
            if lines[0]!="4":
                playerlist[0] = PlayerClass(lines[1],lines[0],lines[2])
                pl = "O" if lines[1] =="X" else "X"
                playerlist[1] = PlayerClass(pl,lines[0],lines[2])
                bdsc,bdocp = subcon(3,8,13,playerlist)
            else:
                playerlist[0] = PlayerClass(lines[1],lines[2],lines[3])
                playerlist[1] = PlayerClass(lines[4],lines[5],lines[6])
                bdsc,bdocp = subcon(7,12,17,playerlist)
            self.BC = BoardClass(lines[0],bdsc,bdocp,playerlist)
            return True
        except:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print exc_type,exc_obj,exc_tb.tb_lineno
            return False
    def isAdjacentTo(self,pltype,i,j):
        if i-1>=0 and (i-1,j) in self.BC.playerlist[pltype].node:
            return True
        if i+1<5 and (i+1,j) in self.BC.playerlist[pltype].node:
            return True
        if j-1>=0 and (i,j-1) in self.BC.playerlist[pltype].node:
            return True
        if j+1<5 and (i,j+1) in self.BC.playerlist[pltype].node:
            return True
        return False
    def updatescore(self,nd,tem,whotogo): #nd[totalscore,i,j]
        self.BC.freenode.remove((nd[1],nd[2]))
        self.BC.playerlist[whotogo].node.add((nd[1],nd[2]))
        self.BC.playerlist[whotogo].score+=nd[0]
        if tem:
            for val in tem:
                self.BC.playerlist[whotogo].node.add(val)
                self.BC.playerlist[whotogo^1].node.remove(val)
                self.BC.playerlist[whotogo^1].score-=self.BC.boardscore[val[0]][val[1]]
    def reversescore(self,nd,tem,whotogo):
        self.BC.freenode.add((nd[1],nd[2]))
        self.BC.playerlist[whotogo].node.remove((nd[1],nd[2]))
        self.BC.playerlist[whotogo].score-=nd[0]
        if tem:
            for val in tem:
                self.BC.playerlist[whotogo^1].node.add(val)
                self.BC.playerlist[whotogo].node.remove(val)
                self.BC.playerlist[whotogo^1].score+=self.BC.boardscore[val[0]][val[1]]

    def Play(self,playerId):
        if not self.BC.freenode:return
        if self.BC.type == 1:
            self.MinMaxWithPrune(playerId,playerId,0,"",False,"next_state.txt",None,None)
        if self.BC.type == 2:
            self.MinMaxWithPrune(playerId,playerId,0,"traverse_log.txt",False,"next_state.txt",None,None)
        if self.BC.type == 3:
            self.MinMaxWithPrune(playerId,playerId,0,"traverse_log.txt",True,"next_state.txt",float("-inf"),float("inf"))
        if self.BC.type == 4: # fight
            while self.BC.freenode:
                prune = True if self.BC.playerlist[playerId].algo == 3 else False
                self.MinMaxWithPrune(playerId,playerId,0,"trace_state.txt",prune,"next_state.txt",float("-inf"),float("inf"))
                playerId = playerId^1
            self.IO.writeFile("trace_state.txt",self.trace_state)
    def getRaidPoint(self,i,j,pltype):
        ToConque = 1^pltype
        lis =[]
        totalscore = self.BC.boardscore[i][j]
        if i-1>=0 and (i-1,j) in self.BC.playerlist[ToConque].node:
            lis.append((i-1,j))
            totalscore+=self.BC.boardscore[i-1][j]
        if i+1<5 and (i+1,j) in self.BC.playerlist[ToConque].node:
            lis.append((i+1,j))
            totalscore+=self.BC.boardscore[i+1][j]
        if j-1>=0 and (i,j-1) in self.BC.playerlist[ToConque].node:
            lis.append((i,j-1))
            totalscore+=self.BC.boardscore[i][j-1]
        if j+1<5 and (i,j+1) in self.BC.playerlist[ToConque].node:
            lis.append((i,j+1))
            totalscore+=self.BC.boardscore[i][j+1]
        return [totalscore,i,j],lis
    def generateOutput(self):
        lis = [[None for i in xrange(5)] for j in xrange(5)]
        for val in self.BC.freenode:
            lis[val[0]][val[1]]="*"
        for val in self.BC.playerlist:
            for v2 in val.node:
                lis[v2[0]][v2[1]] = val.player
        return lis
    def Write(self,outname):
        lis = self.generateOutput()
        self.IO.writeFile(outname,lis)
    
    def WriteTravse(self,fc,cont,alpha,beta):
            st= ",".join([str(_) for _ in cont[:2]])+","
            if cont[2]==float("-inf"):
                st+="-Infinity"
            elif cont[2]==float("inf"):
                st+="Infinity"
            else:
                st+=str(cont[2])
            if cont[0] == self.lasttrace:
                return
            self.lasttrace = cont[0]
            fc.write("\n"+st)
            if alpha!=None and beta!=None:
                o1 = "-Infinity" if alpha == float("-inf") else alpha
                o2 = "Infinity" if beta == float("inf") else beta
                fc.write(","+str(o1)+","+str(o2))
    def Max_ValWithPrune(self,player,whotogo,depth,fc,prune,nextfile,alpha,beta,parent):
        if DEBUG == 100:pdb.set_trace()
        #sonalpha,sonbeta = alpha,beta
        if depth == self.BC.playerlist[player].cutoffdepth or not self.BC.freenode:
            v1 = self.BC.playerlist[player].score
            v2 = self.BC.playerlist[player^1].score
            v=v1-v2 
            #parent[2]=v
            #if fc: self.WriteTravse(fc,parent,alpha,beta)
            return v,(None,None)
        v = float("-inf")
        parent[2] = v
        pos =(None,None)
        #if fc:self.WriteTravse(fc,parent,alpha,beta)
        for m in xrange(5):
            for n in xrange(5):
                if (m,n) in self.BC.freenode:
                    nd,tem = [self.BC.boardscore[m][n],m,n],None
                    if self.isAdjacentTo(whotogo,m,n):
                        nd,tem = self.getRaidPoint(m,n,whotogo)
                    self.updatescore(nd,tem,whotogo)
                    newpar = [self.BC.col[n]+self.BC.row[m],depth+1,v]
                    if DEBUG == 100:pdb.set_trace()
                    if fc:self.WriteTravse(fc,parent,alpha,beta)
                    res ,p= self.Min_ValWithPrune(player,whotogo^1,depth+1,fc,prune,nextfile,alpha,beta,newpar)
                    newpar[2] = res
                    if fc: self.WriteTravse(fc,newpar,alpha,beta)
                    
                    self.reversescore(nd,tem,whotogo)
                    if DEBUG == 100:pdb.set_trace()
                    if v<res:
                        v = res
                        pos = (m,n)
                        parent[2] = v
                    if prune:
                        if v >= beta:
                            if fc: self.WriteTravse(fc,parent,alpha,beta) 
                            return v,pos
                        alpha = max(v,alpha)
        if fc: self.WriteTravse(fc,parent,alpha,beta) #
                    #if fc: self.WriteTravse(fc,newpar,alpha,beta)
        
        return v,pos
    def Min_ValWithPrune(self,player,whotogo,depth,fc,prune,nextfile,alpha,beta,parent):
        if DEBUG == 100:pdb.set_trace()
        #sonalpha,sonbeta = alpha,beta
        if depth == self.BC.playerlist[player].cutoffdepth or not self.BC.freenode:
            v1 = self.BC.playerlist[player].score
            v2 = self.BC.playerlist[player^1].score
            v=v1-v2 
            #parent[2]=v
            #if fc: self.WriteTravse(fc,parent,alpha,beta)
            return v,(None,None)
        v = float("inf")
        pos =(None,None)
        parent[2] = v
        #if fc:self.WriteTravse(fc,parent,alpha,beta)
        for m in xrange(5):
            for n in xrange(5):
                if (m,n) in self.BC.freenode:
                    nd,tem = [self.BC.boardscore[m][n],m,n],None
                    if self.isAdjacentTo(whotogo,m,n):
                        nd,tem = self.getRaidPoint(m,n,whotogo)
                    self.updatescore(nd,tem,whotogo)
                    if fc:self.WriteTravse(fc,parent,alpha,beta)
                    newpar = [self.BC.col[n]+self.BC.row[m],depth+1,v]
                    if DEBUG == 100:pdb.set_trace()
                    res ,p= self.Max_ValWithPrune(player,whotogo^1,depth+1,fc,prune,nextfile,alpha,beta,newpar)
                    self.reversescore(nd,tem,whotogo)
                    newpar[2] = res
                    if fc: self.WriteTravse(fc,newpar,alpha,beta)
                    
                    if DEBUG == 100:pdb.set_trace()
                    if v>res:
                        v = res
                        pos = (m,n)
                        parent[2] = v
                    if prune:
                        if v<=alpha:
                            if fc: self.WriteTravse(fc,parent,alpha,beta)
                            return v,pos
                        beta = min(beta,v)
        if fc: self.WriteTravse(fc,parent,alpha,beta)#
                    #if fc: self.WriteTravse(fc,newpar,alpha,beta)
        return v,pos
    def MinMaxWithPrune(self,player,whotogo,depth,filename,prune,nextfile,alpha,beta):
        fc = None
        try:
            if filename:
                fc = open(filename,"w")
                fc.write("Node,Depth,Value")
                if prune:fc.write(",Alpha,Beta")
        except:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print exc_type,exc_obj,exc_tb.tb_lineno
            print "write failed"
            return False   
        root = ["root",0,None]  
        v,pos = self.Max_ValWithPrune(player,whotogo,depth,fc,prune,nextfile,alpha,beta,root)
        #if fc:
        #    self.WriteTravse(fc,["root",0,v],alpha,beta)
        #print pos
        if fc:
            fc.close()
            self.lasttrace = None
        if pos ==(None,None):
            return False
        
        m,n = pos
        nd,tem = [self.BC.boardscore[m][n],m,n],None
        if self.isAdjacentTo(player,m,n):
            nd,tem = self.getRaidPoint(m,n,player)
        self.updatescore(nd,tem,player)
        if self.BC.type<4:
            self.Write(nextfile)
            return True
        else:
            lis = self.generateOutput()
            for val in lis:
                self.trace_state.append(val)
            return True  

def compfile(name1,name2,num):
    f1 = open(name1, "r")
    f2 = open(name2, "r")

    fileOne = f1.readlines()
    fileTwo = f2.readlines()
    #pdb.set_trace()
    f1.close()
    f2.close()
    if len(fileOne)!=len(fileTwo):
        print num
        return
    for i in xrange(len(fileOne)):
        if fileOne[i][-1]=="\n":
            fileOne[i] = fileOne[i][:len(fileOne[i])-1]+"\r\n"
        else:
            fileOne[i] = fileOne[i]+"\r\n"   
        if fileOne[i]!=fileTwo[i]:
            print num
            return


if __name__ == "__main__":
    #argv = sys.argv
    argv = ["python","-i","None"]
    for i in xrange(61,91):
        name = "input_"+str(i)+".txt"
        argv[2] = name
        GC = GameControl()
        BC =GC.initialize(argv) # BC =boardclass
        if not BC:
            sys.exit()
        GC.Play(0)
        nx = "testcases/next_state_"+str(i)+".txt"
        compfile("next_state.txt",nx,i)
        nx = "testcases/traverse_log_"+str(i)+".txt"
        compfile("traverse_log.txt",nx,i)

    #GC.BC.printBCInfo()