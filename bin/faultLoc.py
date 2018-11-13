from unittest import TestCase,TestResult,TestProgram,TextTestRunner,TextTestResult
from collections import namedtuple
import sys
import inspect
import os
import os.path
from importlib.util import find_spec
from functools import reduce,lru_cache
from itertools import groupby
from collections import Counter
import json

Line = namedtuple("Line","file line")
#TestResult = namedtuple("TestResult","lines status")
class FaultLocalizationResult(TestResult):
    tracing = False
    stopped = False
    def __init__(self,stream=None, descriptions=None, verbosity=None):
        super().__init__(stream, descriptions, verbosity)#*args,**kwargs)
        self.result = {}
        self.currentLines = []
        self.data_stack = []
        self.shouldTrace=True
        self.cur_file_dict, self.cur_file_name, self.last_line = None,None,0
        if not self.tracing:
            sys.settrace(self._tracer)

    def startTest(self,test):
        super().startTest(test)
        #assert sys.gettracer() == None
        #print(self.currentLines)
        #assert len(self.currentLines) == 0
        self.result[test]={}
        self.result[test]["lines"] = []
        self.result[test]["status"] = "skipped"
        self.result[test]["errors"] =[]
        self.currentTest=test
        self.currentLines=[]
        self.shouldTrace=False
        self.stopped=False
        if not self.tracing:
            sys.settrace(self._tracer)
            
    def stopTest(self,test):
        super().stopTest(test)
        self.stopped = True
        self.shouldTrace=False
        if (sys.gettrace() == self._tracer):
            sys.settrace(None)

    #result handling        
    
    def addEvent(self,test,status="skiped"):
        self.result[test]["status"] = status
        self.result[test]["lines"]+=self.currentLines
        self.currentLines=[]
    def addError(self,test,err):
        super().addError(test,err)
        self.result[test]["errors"].append(err)
        self.addEvent(test,"failed")
    def addFailure(self,test,err):
        super().addFailure(test,err)
        self.result[test]["errors"].append(err)
        self.addEvent(test,"failed")  
    def addSuccess(self,test):
        super().addSuccess(test)
        self.addEvent(test,"success")
    def addSkip(self,test,reason = ""):
        super().addSkip(test,reason)
        self.result[test]["errors"].append(reason)
    def addExpectedFailure(self,test,err):
        super().addExpectedFailure(test,err)
        self.addEvent(test,"success")
        self.result[test]["errors"].append(err)
    def addUnexcpectedSuccess(self,test):
        super().addUnexcpectedSuccess(test)
        self.addEvent(test,"failed")

    #fin    
    def wasSuccessful(self):
        self.summary()
        return super().wasSuccessful()
    def summary(self):
        #print(self.result)
        r = {}
        #print(self.result.items())
        for k,g in groupby(list(self.result.items()),lambda x:x[1]["status"]):
            g = map(lambda x:x[1]["lines"],g)
            #print(g)
            r[k]=Counter(reduce(lambda x,y:x+y,g))
        return r
        
    def _tracer(self, frame, event, arg_unused):
        """The tracing function, which invokes self.onLine"""
        if (self.stopped and sys.gettrace() == self._tracer):
            #check stopped and delete tracer
            #print("wtf",frame.f_lineno,event)
            sys.settrace(None)
            return
        #print(event)
        if event == 'call':
            self.data_stack.append((self.cur_file_name, self.last_line))
            try:
                import os.path
                filename = os.path.abspath(inspect.getfile(frame))
                #moduleName = inspect.getmodulename(filename)
                #print(filename)
                #print(filename,os.path.commonprefix([filename,os.getcwd()]))
                if os.path.commonprefix([os.getcwd(),filename])!=os.getcwd():
                    self.shouldTrace = False
                else:
                    #print(filename)
                    self.shouldTrace = True
                    #return self._tracer
            except TypeError:
                filename = "__builtin__"
                self.shouldTrace = False
            self.cur_file_name = filename
        elif event == "line":
            if self.shouldTrace:
                line = Line(self.cur_file_name,frame.f_lineno)
                #print(line)
                self.currentLines.append(line)
                self.last_line = line
        elif event == "return":
            self.cur_file_name, self.last_line = self.data_stack.pop()
        elif event == "exception":
            #print(frame)
            if self.shouldTrace:
                self.shouldTrace = False
        return self._tracer
            
class FaultLocalizationTestCase(TestCase):
    def run(self,result=None):
        if result!=None:
            result = FaultLocalizationResult()
        super().run(result)
class Tarantula(FaultLocalizationResult):
    def summary(self):
        #assert self.stopped
        r = super().summary()
        result = {}
        if "failed" in r:
            #print("?")
            for i in r["failed"]:
                #with open(i.file,"r") as f:
                #    s = f.read()
                j = r["failed"][i]
                total = j
                if "success" in r and i in r["success"]:
                    total+=r["success"][i]
                result[i]=j/total
        #print(r)
        return result
class Crosstab(FaultLocalizationResult):
    @property
    @lru_cache()
    def grouped_lines(self):
        r = {}
        for k,g in groupby(list(self.result.items()),lambda x:x[1]["status"]):
            g = map(lambda x:set(x[1]["lines"]),g)
            r[k] = list(g)
        return r
    #defined function notation
    #use @lru_cache for caching result
    @property
    @lru_cache()
    def N(self):
        N = self.testsRun - len(self.skipped)
        return N
    @property
    @lru_cache()
    def Nf(self):
        Nf = len(self.failures)+len(self.errors) #total number of failed test cases
        return Nf
    @property
    @lru_cache()
    def Ns(self):
        Ns = self.N-self.Nf
        return Ns
    @lru_cache()
    def Ncf(self,line):
        return len(tuple(filter(lambda x:line in x,self.grouped_lines["failed"])))
    @lru_cache()
    def Ncs(self,line):
        return len(tuple(filter(lambda x:line in x,self.grouped_lines["success"])))
    @lru_cache()
    def Nc(self,line):
        return self.Ncf(line)+self.Ncs(line)
    @lru_cache()
    def Nuf(self,line):
        return len(tuple(filter(lambda x:not line in x,self.grouped_lines["failed"])))
    @lru_cache()
    def Nus(self,line):
        return len(tuple(filter(lambda x:not line in x,self.grouped_lines["success"])))
    @lru_cache()
    def Nu(self,line):
        return self.Nuf(line)+self.Nus(line)
    @lru_cache()
    def chi2(self,line):
        try:
            Ecf = self.Nc(line)*self.Nf/self.N
            Ecs = self.Nc(line)*self.Ns/self.N
            Euf = self.Nu(line)*self.Nf/self.N
            Eus = self.Nu(line)*self.Ns/self.N
            chi2 =  (self.Ncf(line)-Ecf)**2/Ecf + \
                    (self.Ncs(line)-Ecs)**2/Ecs + \
                    (self.Nuf(line)-Euf)**2/Euf + \
                    (self.Nus(line)-Eus)**2/Eus
            return chi2
        except ZeroDivisionError:
            return 0.0
    @lru_cache()
    def M(self,line):
        return self.chi2(line)/self.N #sqrt((row-1)*(col-1)) = 1
    @lru_cache()
    def phi(self,line):
        try:
            return self.Ncf(line)/self.Nf*self.Ns/self.Ncs(line)
        except ZeroDivisionError:
            return 0.0
    @lru_cache()
    def zeta(self,w):
        if self.phi(w)>0: return self.M(w)
        elif self.phi(w)<0: return -self.M(w)
        else: return 0.0
        
        
        
    def summary(self):
        #assert self.stopped
        super().summary()
        result = {}
        lines = set(reduce(lambda x,y:x+y,map(lambda x:x["lines"],self.result.values())))
        for w in lines:
            result[w]=(self.chi2(w),self.M(w),self.zeta(w),)
            print(w,result[w])
        
        #print(r)
        return result
class TextFaultLocalizationResult(TextTestResult,FaultLocalizationResult):
    pass
class TextTarantulaResult(TextTestResult,Tarantula):
    def summary(self):
        r = super().summary()
        #print(r)
        print(json.dumps(list(map(lambda x: [x[0].file,x[0].line,x[1]],r.items()))))
        return r
    pass
class CrosstabResult(TextTestResult,Crosstab):
    def summary(self):
        r = super().summary()
        #print(r)
        print(json.dumps(list(map(lambda x: [x[0].file,x[0].line,x[1]],r.items()))))
        return r
    pass
class FaultTestProgram(TestProgram):
    pass
TextTestRunner.resultclass = CrosstabResult
__unittest = True
if __name__ == "__main__":
    FaultTestProgram(module=None)
