import os,sys
dir_path = os.getcwd()
import json
templateA ='''
<html>
<head>
<script>
var importResult =
'''
templateB = '''
;
</script>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/tocas-ui/2.3.3/tocas.css">
<script
			  src="https://code.jquery.com/jquery-3.3.1.min.js"
			  integrity="sha256-FgpCb/KJQlLNfOu91ta32o/NMZxltwRo8QtmkMRdAu8="
			  crossorigin="anonymous"></script>
		
<title>Debug Log</title>
<style>
.selectable{
	cursor: pointer !important;
}

.selectable:hover{
	color:blue !important;
}
</style>
</head>
<body>
<div class="ts container">
<br>
<div class="ts header">
    pyFaultlocUnittest XG21 
    <div class="sub header"><i class="file code outline icon"></i>Development Build</div>
</div>
<div class="ts divider"></div>
<p>Error Report (Click item to sort)</p>
<table class="ts table">
    <thead>
        <tr>
            <th class="selectable" onClick="toggleSortMode(0);">#Line</th>
            <th class="selectable" onClick="toggleSortMode(2);">File</th>
            <th class="selectable" onClick="toggleSortMode(4);">Hue (chi2, phi, sigma)</th>
        </tr>
    </thead>
    <tbody id="tableContent">
    </tbody>
    <tfoot>
        <tr>
            <th colspan="3">Total Error Count: <div id="errorCount" style="display:inline;"></div></th>
        </tr>
    </tfoot>
</table>
<details class="ts accordion">
    <summary>
        <i class="dropdown icon"></i> Raw Output from Debugger
    </summary>
    <div class="content">
        <p id="rawlog"></p>
    </div>
</details>
<div class="ts divider"></div>
Developed for Software Engineering Course Project<br>
Project written by Group 21
</div>
<script>
if (typeof importResult === 'undefined'){
	alert("Error. Please generate this document with the given debugger.");
}else{
	var errorlog = importResult;
	initTable();
	var sortMode = 0;
	$("#rawlog").html(JSON.stringify(errorlog));
}
function toggleSortMode(target){
	if (target == 0){
		if (sortMode == 0){
			sortMode = 1;
		}else{
			sortMode = 0;
		}
	}else if (target == 2){
		if (sortMode == 2){
			sortMode = 3;
		}else{
			sortMode = 2;
		}
	}else if (target == 4){
			sortMode = 4;
	}
	initTable(sortMode);
	//console.log(sortMode);
}

function initTable(sortmode = 0){
	var b = $.extend(true, [], errorlog);
	//b is a copy of errorlog we can work on sorting and changing things inside it
	switch (sortmode){
		case 0:
			b.sort((a,b) => a[1] > b[1]);
			drawTable(b);
			break;
		case 1:
			b.sort((a,b) => a[1] < b[1]);
			drawTable(b);
			break;
		case 2:
			b.sort((a,b) => a[0].toUpperCase().localeCompare(b[0].toUpperCase()));
			drawTable(b);
			break;
		case 3:
			b.sort((a,b) => a[0].toUpperCase().localeCompare(b[0].toUpperCase()));
			b.reverse();
			drawTable(b);
			break;
		case 4:
			b.sort((a,b) => a[2][0] > a[2][0]);
			drawTable(b);
			break;
		
		
	}
}

function drawTable(arr){
	$("#tableContent").html("");
	var template = '<tr>\
            <td>%linenumber%</td>\
            <td><pre>%filepath%</pre></td>\
            <td>%hue%</td>\
        </tr>';
	for (var i = 0; i < arr.length; i++){
		var box = template;
		box = box.replace("%linenumber%",arr[i][0]);
		box = box.replace("%filepath%",arr[i][1]);
		box = box.replace("%hue%",arr[i][2]);
		$("#tableContent").append(box);
	}
	$("#errorCount").html(arr.length);
}
</script>
</body>
</html>'''
class httpTemplate:
    def __init__(self):
        self.files = dict()
        
    def loadFile(self,fileName):
        lines = []
        self.files[fileName] = lines
        with open(fileName,"r") as f:
            for i,l in enumerate(f):
                lines.append([i,l,(0,0,0)])
    def appendResult(self,file,line,suspicious):
        if not file in self.files:
            self.loadFile(file)
        #print(line,len(self.files[file])
        self.files[file][int(line)-1][2] = suspicious
    def digest(self):
        for i in self.files:
            filepath = os.path.join("testResult",os.path.relpath(i)+".html")
            content = json.dumps(self.files[i])
            os.makedirs(os.path.dirname(filepath),exist_ok=True)
            with open(filepath,"w") as f:
                f.write(templateA + content + templateB)
if __name__ == "__main__":
    if (len(sys.argv) > 1):
        json = ( sys.argv[1])
        infile = open(dir_path + "\\" + json,"r")
        content = infile.read()
        ef = open(dir_path + "\\errorReport.html","w");
        ef.write(templateA + content + templateB)
        ef.close()
    else:
        print("Not enough variable. Usage: genReport.py error.json")
