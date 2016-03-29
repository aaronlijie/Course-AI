#python
#-*- coding: UTF-8 -*-
#version 0.1
import sys
import pdb
import re
DEBUG = 7 
# 1: readfile, 
# 2: generate part 
# 3: fol_or, fol_and  
# 4: main print info
# 5:FOL_ASK EXCEPT


NEG = 0

class BaseEle(object):
    def __init__(self,name,ty,val): #type: 0 const, 1 val,2:predicate
        self.name = name
        self.type = ty
        #self.val = val
        self.subvar = []
        self.Not = 0
        self.subname = ""
        if name[0]=="~":
            self.Not = 1
            self.subname = name[1:]
    def isexpress(self):
        return self.type ==2
    def isvariable(self):
        return self.type ==1
    def isconst(self):
        return self.type ==0
    def __repr__(self):
        return self.name
    def __eq__(self,other):
        return other is self or (isinstance(other,BaseEle) and self.name == other.name and self.subvar==other.subvar )
    #def __hash__(self):
    #    return hash(self.name) #^ hash(tuple(self.subvar))
    def printBa(self,stt=""):
        st = stt
        a = ["const","val","predicate"]
        b = ["No","Yes"]
        #v = "None" if self.val=="" else self.val
        s = "None" if self.subname=="" else self.subname
        st = st+a[self.type]+"   :"+self.name
        if self.type == 2:
            st = st+" subname: "+ s 
        #if self.type == 2 else st+",    val: "+v+" "
        print st
        for val in self.subvar:
            val.printBa("  "+stt)

class KnowledgeBase(object):
    def __init__(self,infile):
        self.lines = self.openInfile(infile)
        self.Goal = []
        self.KBsent = {}
        self.KBimpl = {}  # not in use now
        self.var = {}     # not in use now
        self.prev=""
        self.output = []
        self.Truedic={}
        self.standarizecount = 0


    def isvariable(self,v):
        return isinstance(v,BaseEle) and v.isvariable()
    def ispredicate(self,v):
        return isinstance(v,BaseEle) and v.isexpress()

#######################################################################################################################
#################
#################      Initialize and generate part
#################
#######################################################################################################################
    def initialize(self):
        if not self.lines:return False
        res = self.genGoal()
        if res == False:return False
        res = self.genKB()
        if res == False: return False
        return True

    def genSenstence(self,pat):
        lis = []
        start,i=0,0
        while i<len(pat):
            if pat[i]=="(" or pat[i]==")":
                lis.append(pat[start:i])
                start = i+1
                i+=1
            elif pat[i]=="," and pat[i+1]==" ":
                lis.append(pat[start:i])
                start = i+2
                i=i+2
            else:
                i+=1
        base = BaseEle(lis[0],2,"")
        for val in lis[1:]:
            if len(val) == 1 and val.islower():
                if val not in self.var:   # generate variable list
                    self.var[val] = None
                base.subvar.append(BaseEle(val,1,"_"))
            elif val[0].islower()==False:
                base.subvar.append(BaseEle(val,0,val))
            else:
                print "error"
                return False
        return base
    def genGoal(self):
        if not self.lines:return
        firstline = self.lines[0].split(" && ")
        for pat in firstline:
            base = self.genSenstence(pat)
            if base==False:
                return False
            else:
                self.Goal.append(base)
        return True
    def genKB(self):
        for i in xrange(2,2+int(self.lines[1])):
            line = re.split(" => ",self.lines[i])
            if len(line)>1: # => exist
                rhs = self.genSenstence(line[-1])
                if rhs==False:return False
                if rhs.name not in self.KBsent: #####
                    self.KBsent[rhs.name]=[]  ######
                #self.KBsent[rhs.name].append(rhs)
                #if rhs.name not in self.KBimpl:
                #    self.KBimpl[rhs.name] = []
                subline = re.split(" && ",line[0])
                if DEBUG ==2 :pdb.set_trace()
                litem = [rhs]
                for pat in subline:
                    lhs = self.genSenstence(pat)
                    if lhs == False:return False
                    litem.append(lhs)
                if DEBUG ==2 :pdb.set_trace()
                self.KBsent[rhs.name].append(litem) #####
            else:
                subline = re.split(" && ",line[0])
                for pat in subline:
                    lhs = self.genSenstence(pat)
                    if lhs == False:return False
                    if lhs.name not in self.KBsent: ###
                        self.KBsent[lhs.name]=[]  ######
                    self.KBsent[lhs.name].append([lhs]) ######
        return True


#######################################################################################################################
#################
#################      Unify function
#################
#######################################################################################################################
    def Unify(self,predx,predy,table):
        if table == None:   
            return None
        #elif predx.name==predy.name:return table
        elif predx == predy:
            return table
        elif self.isvariable(predx):
            return self.Unify_var(predx,predy,table)
        elif self.isvariable(predy):    
            return self.Unify_var(predy,predx,table)
        elif isinstance(predx,BaseEle) and isinstance(predy,BaseEle):
            return self.Unify(predx.subvar,predy.subvar,self.Unify(predx.name,predy.name,table))
        #elif isinstance(predx,str) or isinstance(predy,str) or not predx or not predy:
        #    if predx == predy:return table
        #    return None
        elif isinstance(predx,list) and isinstance(predy,list):
            return self.Unify(predx[1:],predy[1:],self.Unify(predx[0],predy[0],table))
        else:
            return None
    def Unify_var(self,var,x,table):
        if var.name in table:
            return self.Unify(table[var.name],x,table)
        elif x.name in table:
            return self.Unify(var,table[x.name],table)
        elif self.Occur_check(var,x):
            return None
        else:
            tab2 = table.copy()
            tab2[var.name] = x
            return tab2
    def Occur_check(self,var,x):  # waiting for update
        #pdb.set_trace()
        if var == x:
            if DEBUG ==10 : print "Occur_check 1"
            return True
        elif isinstance(x,BaseEle):
            if DEBUG ==10 : print "Occur_check 2"
            return var.name == x.name or self.Occur_check(var,x.subvar)
        elif not isinstance(x,str) and isinstance(x,list):
            if DEBUG ==10 : print "Occur_check 3"
            for p in x:
                if DEBUG ==10 : print "Occur_check 4"
                res = self.Occur_check(var,p)
                if res:return True
        return False

#######################################################################################################################
#################
#################      PRINT PART
#################
#######################################################################################################################
    def subgen(self,pred,tab):
        predname=pred.name+"("
        allconst = True   #True:allconst, False:has variable
        prim = []
        for st in pred.subvar:
            if st.isconst():
                prim.append(st.name)
            else:
                va = "_"
                x = st
                if tab!=None:
                    while x.name in tab:
                        x = tab[x.name]
                        if x.isconst():
                            va = x.name
                            break
                if va=="_": allconst=False
                prim.append(va)   
        f = ", ".join(prim)
        predname += f+")"
        return predname
    def printAskOrAn(self,pred,tab,bit,TF):
        if pred==None:return
        head = "Ask: "        # 0: ASK, 1:True,2:False
        if bit == 1:
            if TF == True:
                head = "True: "
            else:
                head = "False: " 
        predname = self.subgen(pred,tab)
        if len(self.output)>0 and head+predname == self.output[-1][0]:
            return
        #if len(self.output)>0 and head == "False: " and predname == self.output[-1][1]:
            #self.output.pop()
        #    return
        self.output.append([head+predname,pred.name])
        return
    def addTrue(self,pred,tab):
        predname = self.subgen(pred,tab)
        self.Truedic[predname]=True

    def removeTrue(self,pred,tab):
        predname = self.subgen(pred,tab)
        if predname in self.Truedic:
            for i in xrange(2):
                if self.output and self.output[-1][1]==pred.name:
                    self.output.pop()

#######################################################################################################################
#################
#################      BACKWARD CHAINING 
#################
#######################################################################################################################
        
    def FOL_BC_ASK(self,goal):
        unif = {}
        self.printAskOrAn(goal,unif,0,True)
        a = self.FOL_BC_OR(goal,unif)
        while True:
            try:
                f=a.next()
                if f!=None:
                    return True
            except:
                if DEBUG == 5:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    print exc_type,exc_obj,exc_tb.tb_lineno
                    print "FC_BC_ASK error"
                return False

    def FOL_BC_OR(self,goal,table):
        if DEBUG ==3:
           pdb.set_trace()
        
        if goal.name in self.KBsent:
            sentlist = self.KBsent[goal.name]
            for case in sentlist:
                op=0
                lhs,rhs = self.standarizeVal(case[1:],case[0])
                #pdb.set_trace()
                unif = self.Unify(rhs,goal,table)
                self.printAskOrAn(goal,table,0,True)
                for res in self.FOL_BC_AND(lhs,unif):
                    re = True if res!=None else False
                    if re==True:
                        op = 1
                        self.addTrue(goal,table)
                        self.printAskOrAn(goal,res,1,re)
                        yield res
            if op == 0:
                self.printAskOrAn(goal,res,1,False)
                self.removeTrue(goal,table)
                #pdb.set_trace()
                yield None

    def FOL_BC_AND(self,goal,table):
        if DEBUG ==3:
           pdb.set_trace()
        if table == None:yield None
        elif len(goal)==0:yield table
        else:
            first,res = goal[0],goal[1:]
            f = self.Subst(table,first)
            #self.printAskOrAn(first,table,0,True)#
            #pdb.set_trace()
            for val in self.FOL_BC_OR(f,table):

                #pdb.set_trace()    
                for mm in self.FOL_BC_AND(res,val):
                    #print mm
                    yield mm


#######################################################################################################################
#################
#################      STANDARIZE VARIABLE and Subst function FOR BC
#################
#######################################################################################################################
    def standarizeVal(self,lhs,rhs):
        if not isinstance(lhs,list) or not isinstance(rhs,BaseEle):
            return lhs,rhs
        dic ={}
        def standarizeHelp(v,dic):
            if v.name not in dic:
                self.standarizecount+=1
                dic[v.name] = "v_"+str(self.standarizecount)
            return dic[v.name]
        for val in rhs.subvar:
            if self.isvariable(val):
                val.name = standarizeHelp(val,dic)
        for prat in lhs:
            for val in prat.subvar:
                if self.isvariable(val):
                    val.name = standarizeHelp(val,dic)
        return lhs,rhs

    def Subst(self,v1,v2):
        if isinstance(v2,list):
            return [self.Subst(v1,x) for x in v2]
        #elif isinstance(x,tuple):
        #    return
        elif not isinstance(v2,BaseEle):
            return v2
        elif self.isvariable(v2):
             return v1.get(v2.name,v2)

        else:
            b = BaseEle(v2.name,v2.type,"")
            b.subvar = [self.Subst(v1,t) for t in v2.subvar]
            return b

#######################################################################################################################
#################
#################      Diagnonsis Part
#################
#######################################################################################################################

    def test(self):
        
        f = self.KBimpl["Tells"]
        pdb.set_trace()
        res = self.Unify(self.KBimpl["Traitor"][0][3],self.KBimpl["Tells"][0][0],{})
        pdb.set_trace()
    def printKB(self):
        print "GOAL:".center(80,"-")
        print "-".center(80,"-")
        for val in self.Goal:
            val.printBa()
        print "Variable:".center(80,"-")
        print "-".center(80,"-")
        for val in self.var.keys():
            print val," : ",self.var[val]
        print "Predicate:".center(80,"-")
        print "-".center(80,"-")
        for val in self.KBsent.keys():
            print val
            for v in self.KBsent[val]:
                print "next".center(40,"*")
                for s in v:
                    s.printBa("   -->")
        print "Implication:".center(80,"-")
        print "-".center(80,"-")
        for val in self.KBimpl.keys():
            print val
            for v in self.KBimpl[val]:
                for s in v:
                    s.printBa("   -->")

#######################################################################################################################
#################
#################      READ AND WRITE FILE
#################
#######################################################################################################################

    def openInfile(self,filename):
        try:
            with open(filename,"r") as f:
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
    def openWriteFile(self,outputname,Final):
        try:
            fjob = open(outputname,"w")
            for i in self.output:
                fjob.write(i[0]+"\n")
            last = "False" if Final==False else "True"
            fjob.write(last)
            fjob.close()
        except:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print exc_type,exc_obj,exc_tb.tb_lineno
            print "write file failure"
            return False         

#######################################################################################################################
#######################################################################################################################

if __name__=="__main__":
    argv = sys.argv
    KB = KnowledgeBase(argv[2])
    res = KB.initialize()
    if DEBUG ==7:
        KB.printKB()
    #pdb.set_trace()
    if res == False:
        print "initialize failure"
        sys.exit(0)
    res = True
    for val in KB.Goal:
        cd    = KB.FOL_BC_ASK(val)
        res = res & cd
        if res ==False:break
    if DEBUG == 6:
        for i in KB.output:
            print i[0]
        print res
    KB.openWriteFile("output.txt",res)
    