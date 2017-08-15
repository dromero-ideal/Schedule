import sys
sys.path.append(sys.path[0]+'\\modules')
from Schedule_FilePaths import *
from Schedule_Classes import *

#Set file type
fileType = 'Master'      #CSV output with all posibilities.
#fileType = 'Formatted'  #Schedule & StudyHall of first solution found.


#Output files
g = open(solutionsCSV, 'w')
g.write(",".join(str(cl.name) for cl in CourseList))
g.write("\n")
g.close()

#Carraway T/R
for t in Teachers:
    if t.name == 'Carraway':
        print(t.period)
        t.period = [0, 1,1,1,1,1, 0,0,0,0,1]
        break
for t in Teachers:
    if t.name == 'Carraway':
        print(t.period)
        break

foo = MasterAssign(0,1,fileType)
while foo == False:
	foo = Continue(fileType,0)
if foo != True:
	print("Error unexpected value for foo.")
	eL = open(ErrorLog, 'w')
	eL.write("Error unexpected value for foo.\n")
	eL.write(foo)
	eL.close()


#Carraway M/W/F
for t in Teachers:
    if t.name == 'Carraway':
        t.period = [0, 0,0,0,0,0, 1,1,1,1,1]
        break
for t in Teachers:
    if t.name == 'Carraway':
        print(t.period)
        break

foo = MasterAssign(0,1,fileType)
while foo == False:
    foo = Continue(fileType,0)
if foo != True:
    print("Error unexpected value for foo.")
    eL = open(ErrorLog, 'w')
    eL.write("Error unexpected value for foo.\n")
    eL.write(foo)
    eL.close()
