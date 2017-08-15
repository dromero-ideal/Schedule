import sys
sys.path.append(sys.path[0]+'\\modules')
from Schedule_FilePaths import *
from Schedule_Classes import *


#Make this take user input.
bar = [8, 4, 9, 3, 5, 6, 8, 9, 1, 3, 7, 5, 9, 2, 1, 4, 5, 6, 10, 7, 9, 6, 2, 10, 3, 4, 9, 7, 8, 4, 3, 1, 8, 8, 7, 6, 7, 6, 8, 7, 8, 6, 1, 2, 2, 3, 5, 1, 2, 5, 8, 10, 9, 9]


for i in range(len(bar)):
	CourseList[i].SlowAssign(bar[i])

HumanReadableSchedule(solution)
StudyHall(studyHall,MSstudyHall,HSstudyHall)
