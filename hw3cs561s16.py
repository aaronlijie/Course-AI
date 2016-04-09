#python
import pdb
import sys
import math
import copy

#------------------------------------------------------------------------------------------
#    0 : NOTHING 
#    1: debug initial 
#    2: debug IO 
#    3:sub function for the ENUMERATION-ASK
DEBUG = 3
#------------------------------------------------------------------------------------------

class QueryNode(object):
    def __init__(self):
        self.type = None    #0: P   1: EU    2: MEU
        self.query=[]
        self.cond = []
    def initialize(self,s):
        if s[0]=="P":
            self.type = 0
            s = s[2:len(s)-1]
        elif s[0:2] =="EU":
            self.type = 1
            s = s[3:len(s)-1]
        elif s[0:3] == "MEU":
            self.type = 2
            s = s[4:len(s)-1]
        else:
            return False
        slist = s.split("|")
        if len(slist)==1 or len(slist)==2:
            querytem  = slist[0].split(",")
            for q in querytem:
                val = self.handlequery(q)
                if val==False:return False
                self.query.append(val)
            if len(slist)==2:
                condtem = slist[1].split(",")
                for q in condtem:
                    val = self.handlequery(q)
                    if val==False:return False
                    self.cond.append(val)
            return True
        else:
            return False
    def handlequery(self,q):
        node = [None,0]
        part = q.split("=")
        if len(part)==1:
            node[0]=part[0]
        elif len(part)==2:
            node[0] = part[0].strip(" ")
            val = part[1].strip(" ")
            node[1] = "+" if "+" in val else "-"
        else:
            return False
        return node
    
    #------------------------------------------------------------------------------------------
    #DEBUG PART: PRINT INFO DEBUG = 1
    def printQueryNode(self):
        #pdb.set_trace()
        dic ={0:"P",1:"EU",2:"MEU"}
        #dic2={0:"None",1:"+","-":"-"}
        print "-"*60
        print "type:",dic[self.type]
        print "query=",self.query
        print "cond=",self.cond       

        print "-"*60
    #------------------------------------------------------------------------------------------
class BayesNode(object):
    def __init__(self):
        self.node=None #the name of this bayesNode
        self.type=0   #0:normal  1: dicision
        self.prob = -1 # -1: has parent 
        self.condprob = {}
        self.parent=[]
        self.child =[]
        '''
        exmaple01.txt:
        Demoralize | NightDefense Infiltration
        0.3 + +
        0.6 + -
        0.95 - +
        0.05 - -

        {
            self.node = "Demoralize"
            self.type=0
            self.prob = -1 # -1: has parent 
            self.condprob = {
                                "++":03,
                                "+-":0.6,
                                "-+":0.95,
                                "--":0.05
                            }
            self.parent=["NightDefense","Infiltration"]
            self.child =[]

            # for node Infiltration: self.child = ["Demoralize"]

        }


        '''
    def initialize(self,slist):
        #pdb.set_trace()
        part=slist[0].split("|")
        if len(part)==1:   # there is no parent for this node.
            self.node = part[0].strip(" ")
            if len(slist)!=2:return False
            if slist[1] == "decision":
                self.type= 1
                return True
            self.prob=float(slist[-1])
            return True
        elif len(part)==2:
            self.node = part[0].strip(" ")
            #--- initialize parent list
            cond = part[1].strip(" ").split(" ")
            self.parent = cond
            #--- initialize end
            if len(slist)!=math.pow(2,len(cond))+1:
                return False

            #--- add the cond probability

            for v in slist[1:]:   
                vl = v.split(" ")
                ad = "".join(vl[1:])
                if ad in self.condprob:
                    if self.condprob[ad]!=float(vl[0]):
                        return False
                else:
                    self.condprob[ad]=float(vl[0])
            #--- add end
            return True
        else:
            return False
    #------------------------------------------------------------------------------------------
    #DEBUG PART: PRINT INFO DEBUG = 1
    def printBayesNode(self):
        print "-"*60
        print "Node:",self.node
        if self.type==1:
            print "type:","dicision"
        else:
            print "type:","normal"
        if self.prob!=-1:
            print "no pre cond"
            print self.prob
        else:
            print "parent:",self.parent
        print "child:",self.child   
        for k in self.condprob.keys():
            print k,":",self.condprob[k]
    #------------------------------------------------------------------------------------------



class BayesianNetwork(object):
    #------------------------------------------------------------------------------------------
    #INITIALIZE
    def __init__(self,infile):
        self.query = []
        self.Net={}
        self.utility = None  # utility node type is same as bayesnode type
        self.lines = self.openInfile(infile)
        self.output = []
    def initialize(self):
        if self.lines==False:
            return False
        ret = self.initQuery()
        if ret == False:return False
        ret = self.initBayesNode(ret)
        if ret == False:return False
        if ret !=len(self.lines)+1:
            ret = self.initUtility(ret)
            if ret==False:return False
        self.construct()
        if DEBUG==1:
            #pdb.set_trace()
            self.printQuery()
            self.printBayes()
            print "-"*60
            if self.utility:
            	print "utility"
                self.utility.printBayesNode()
        return True
    def initQuery(self):
        i = 0
        while self.lines[i]!="******":
            qn = QueryNode()
            ret = qn.initialize(self.lines[i])
            if ret==False:return False
            self.query.append(qn)
            i+=1
        return i+1
    def initBayesNode(self,i):
        start = i
        while True:
            while i!=len(self.lines) and self.lines[i]!="***" and self.lines[i]!="******":
                i+=1
            bn = BayesNode()
            ret = bn.initialize(self.lines[start:i])
            if ret==False:return False
            self.Net[bn.node] = bn
            if i==len(self.lines) or self.lines[i]=="******":
                return i+1
            else:
                i+=1
                start = i
        return i
    def initUtility(self,i):
        ut = BayesNode()
        ret = ut.initialize(self.lines[i:])
        if ret == False:return False
        self.utility=ut
        return True
    def construct(self):
        '''
        construct the bayes Net, for each node in the Network add the link to its child
        in the initialization of initBayesNode, each node has link to its parent

        FOR EXAMPLE:
        sample01.txt:

        NightDefense | LeakIdea:
        NightDefense (child) <----> LeakIdea (parent)
        '''
        for nod in  self.Net.keys():
            for k in self.Net[nod].parent:
                self.Net[k].child.append(self.Net[nod].node)
        return True
    #------------------------------------------------------------------------------------------

    #------------------------------------------------------------------------------------------
    # sub function for the ENUMERATION-ASK

    def NORMALIZE(self,dic):
        '''
        args:
            dic: {}
        Normalize the prob, the sum of all probability equals to 1.0
        '''
        sumall = sum(dic.values())
        for i in dic.keys():
            dic[i] = dic[i]/sumall
        return dic

    def SortOrder(self,variablelist):
        '''
        sort the variablelist in the following order:
        1. for each node x, all parents of x will appear before x
        2. if there is no parent-child relationship, node will be sorted by alphabetically
        '''
        variablelist.sort()
        appeared = set()
        ret = []
        while len(ret)!=len(variablelist):
            for s in variablelist:
                flag = True
                if s not in appeared:
                    for x in self.Net[s].parent:
                        if x not in appeared:
                            flag=False
                            break
                    if flag:
                        appeared.add(s)
                        ret.append(s)
        return ret

    def queryProb(self,X,e):
        '''
        query the probability for variable X.
        e is the info we know.(e contains the parents of X)
        Args:
            X: str
            e: {}
        For EXAMPLE:
        In example01.txt:
        Demoralize | NightDefense Infiltration
        0.3 + +
        0.6 + -
        0.95 - +
        0.05 - -      
        e = {"NightDefense":"+","Infiltration":"-","Demoralize":"+"}
        X = "Demoralize"
        queryProb(X,e) = 0.6
        '''
        if self.Net[X].prob!=-1: #X didn't have parent
            prob = self.Net[X].prob if e[X]=="+" else 1- self.Net[X].prob
            return prob
        else:
            tem =[]
            for k in self.Net[X].parent:
                tem.append(e[k])
            st = "".join(tem)
            prob = self.Net[X].condprob[st] if e[X]=="+" else 1-self.Net[X].condprob[st]
            return prob


    #------------------------------------------------------------------------------------------
    # MainFunction for bayes network: ENUMERATION-ASK and ENUMERATE-ALL
    # for more info, get reference form page 525 AIAM 3rd edition
    def ENUMERATION_ASK(self,X,e):
        RET = {}
        for x in "+-":
            tempe = copy.deepcopy(e)
            e[X] = x
            variables = self.SortOrder(self.Net.keys())
            RET[x] = (self.ENUMERATE_ALL(variables,e))
        RET = self.NORMALIZE(RET)
        return RET
    def ENUMERATE_ALL(self, variables,e):
        if len(variables)==0:return 1.0
        Y = variables[0]
        if Y in e:
            ret = self.queryProb(Y,e)*self.ENUMERATE_ALL(variables[1:],e)
        else:
            temprobs = []
            tempe = copy.deepcopy(e)
            for y in "+-":
                tempe[Y] = y
                temprobs.append(self.queryProb(Y,tempe)*self.ENUMERATE_ALL(variables[1:],tempe))
            ret = sum(temprobs)
        return ret

    #------------------------------------------------------------------------------------------

    #------------------------------------------------------------------------------------------
    # function to run the bayes
    def MainRun(self):
        for eachquery in self.query:
            if eachquery.type == 0 : #type = P().. will call ENUMERATION_ASK
                templist =[]
                q=[]
                e = {}

                for eache in eachquery.cond:
                    e[eache[0]]=eache[1]
                for i,X in enumerate(eachquery.query):
                    q.append(X[1])
                    e[X[0]]=X[1]
                    teme = copy.deepcopy(e)
                    val = self.ENUMERATION_ASK(X[0],teme)
                    templist.append(val)
                if DEBUG ==3 and len(eachquery.query)==3:
                    pdb.set_trace()

                while len(templist)!=1:
                    last = templist.pop()
                    first = templist.pop()
                    tem = {}
                    for i in first.keys():
                        for j in last.keys():
                            tem[i+j] = first[i]*last[j]
                    templist.append(tem)
                val = round(templist[0]["".join(q)],2)

                #val = round(templist[-1][eachquery.query[-1][1]],2)
                valstr = str(val).ljust(4,"0")
                self.output.append(valstr)
            elif eachquery.type == 1: # type = EU().. contain dicision node
                pass
            elif eachquery.type == 2: # type = MEU().. contain dicision node
                pass
        self.writeFile()

    #------------------------------------------------------------------------------------------


    #------------------------------------------------------------------------------------------
    # IO part
    def openInfile(self,filename):
        try:
            with open(filename,"r") as f:
                lines = f.read().splitlines()
            if DEBUG == 2:
                for i in lines:
                    print i
            return lines
        except:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print exc_type,exc_obj,exc_tb.tb_lineno
            print "no such file"
            return False 
    

    def writeFile(self):
        for i in self.output:
            print i

    #------------------------------------------------------------------------------------------


    #------------------------------------------------------------------------------------------
    #DEBUG PART: PRINT INFO DEBUG = 1

    def printQuery(self):
        for i in self.query:
            i.printQueryNode()
    def printBayes(self):
        for i in self.Net.keys():
            self.Net[i].printBayesNode()
    #------------------------------------------------------------------------------------------


if __name__=="__main__":
    print "start"
    argv = sys.argv
    bayes = BayesianNetwork(argv[2])
    res = bayes.initialize()
    if res==False:
        print "initialize false"
    if DEBUG == 2:    
        e = {"Demoralize":"-","NightDefense":"-","Infiltration":"+","LeakIdea":"-"}
        print bayes.queryProb("Demoralize",e)
        print bayes.SortOrder(bayes.Net.keys())
    bayes.MainRun()
