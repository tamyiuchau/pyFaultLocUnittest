from unittest import TestCase,TestResult,TestProgram,TextTestRunner,TextTestResult
from collections import namedtuple
import sys
import inspect
import os
import os.path
from importlib.util import find_spec
from functools import reduce
from itertools import groupby
from collections import Counter

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
    def summary(self):
        #assert self.stopped
        r = super().summary()
        result = ()
        if "failed" in r:
            #print("?")
            for i in r["failed"]:
                #with open(i.file,"r") as f:
                #    s = f.read()
                j = r["failed"][i]
                total = j
                if "success" in r and i in r["success"]:
                    total+=r["success"][i]
                result[i]=[j/total]
        #print(r)
        return result
class TextFaultLocalizationResult(TextTestResult,FaultLocalizationResult):
    pass
class TextTarantulaResult(TextTestResult,Tarantula):
    def summary(self):
        r = super().summary()
        print(r)
        return r
    pass
class FaultTestProgram(TestProgram):
    pass
TextTestRunner.resultclass = TextTarantulaResult
__unittest = True
if __name__ == "__main__":
    FaultTestProgram(module=None)
