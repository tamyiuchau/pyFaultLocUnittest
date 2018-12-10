#What is it
It is a drop-in implementation of two fault localization technique,"tarantula" and "crosstab", on top of python standard unittest.
#How to install
```
pip install .
```
#How to use
```
python -m faultLoc -r tarantula
```

#Hot to generate report
```
cd test
python -m faultLoc -r crosstab #generated
```
Open the newly generated errorReport.html file and the result of debugger is shown.

#How to sort the result
Press on the title of each column to change the sorting method (Line / File / Result (chi2, phi, sigma)).
