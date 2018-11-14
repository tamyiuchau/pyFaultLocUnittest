#What is it
It is a drop-in implementation of two fault localization technique,"tarantula" and "Crosstab", on top of python standard unittest.

#How to use
```
cd test
python ../bin/faultLoc.python
```

#Hot to generate report
```
cd test
python ../bin/faultLoc.python -s crosstab > result.json
python ../bin/reportGen.py result.json
```
Open the newly generated errorReport.html file and the result of debugger is shown.

#How to sort the result
Press on the title of each column to change the sorting method (Line / File / Hue (chi2, phi, sigma)).