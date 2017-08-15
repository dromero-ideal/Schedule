import sys
sys.path.append(sys.path[0]+'\\modules')
from Schedule_FilePaths import *
from Schedule_Classes import *

f = open(basic, 'w')

for c in CourseList:
	f.write("{0}\n".format(c.name))
f.write("\n")

for c in CourseList:
	f.write("{0}\n".format(c.name))
	for p in c.people:
		f.write("{0}\n".format(p.name))
	f.write("\n")

for s in Students:
	f.write("{0}\n".format(s.name))
	for q in s.schedule:
		f.write("{0}\n".format(q.name))
	f.write("\n")
for t in Teachers:
	f.write("{0}\n".format(t.name))
	for q in t.schedule:
		f.write("{0}\n".format(q.name))
	f.write("\n")

f.close()
