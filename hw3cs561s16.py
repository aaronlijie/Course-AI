#python
import pdb
import sys
import math

DEBUG = 1  #0 : NOTHING 1: debug initial 2: debug IO


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
            node[1] = 1 if "+" in val else -1
        else:
            return False
        return node
    def printQueryNode(self):
        #pdb.set_trace()
        dic ={0:"P",1:"EU",2:"MEU"}
        dic2={0:"None",1:"+",-1:"-"}
        print "-"*60
        print "type:",dic[self.type]
        print "query=",self.query
        print "cond=",self.cond       

        print "-"*60
class BayesNode(object):
    def __init__(self):
        self.node=None
        self.type=0   #0:normal  1: dicision
        self.table={}
        self.cond = []
    def initialize(self,slist):
        #pdb.set_trace()
        part=slist[0].split("|")
        if len(part)==1:
            self.node = part[0].strip(" ")
            if len(slist)!=2:return False
            if slist[1] == "decision":
                self.type= 1
                return True
            self.table["+"]=float(slist[-1])
            return True
        elif len(part)==2:
            self.node = part[0].strip(" ")
            cond = part[1].strip(" ").split(" ")
            self.cond = cond
            if len(slist)!=math.pow(2,len(cond))+1:
                return False
            for v in slist[1:]:
                vl = v.split(" ")
                ad = "".join(vl[1:])
                if ad in self.table:
                    if self.table[ad]!=float(vl[0]):
                        return False
                else:
                    self.table[ad]=float(vl[0])
            return True
        else:
            return False
    def printBayesNode(self):
        print "-"*60
        print "Node:",self.node
        if self.type==1:
            print "type:","dicision"
        else:
            print "type:","normal"
        if self.cond==None:
            print "no pre cond"
        else:
            print self.cond
        for k in self.table.keys():
            print k,":",self.table[k]

class BayesianNetwork(object):
    def __init__(self,infile):
        self.query = []
        self.bayesNode=[]
        self.utility = None  # utility node type is same as bayesnode type
        self.lines = self.openInfile(infile)

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
        if DEBUG==1:
            #pdb.set_trace()
            #self.printQuery()
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
            self.bayesNode.append(bn)
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

    def printQuery(self):
        for i in self.query:
            i.printQueryNode()
    def printBayes(self):
        for i in self.bayesNode:
            i.printBayesNode()

if __name__=="__main__":
    print "start"
    argv = sys.argv
    bayes = BayesianNetwork(argv[2])
    res = bayes.initialize()
    if res==False:
        print "initialize false"