import math
from Schedule_FilePaths import *

import itertools #Used in adding Courses.

##################################################################################################################
#Get the number of blocks in the schedule.
#Function defined in FilePaths
nPeriods = get_nPeriods()
print(nPeriods)
symList = get_Symmetry()
print(symList)

##################################################################################################################


##################################################################################################################
#People
##################################################################################################################
AllPeople = []
Teachers = []
Students = []
msStudents = []
hsStudents = []
#Creating class to contain information on teachers and students.
class Person:
    #Student and Teachers
    def __init__(self, Name, pType):
        self.name = Name
        #Default Perameters
        self.schedule = [] #Course objects placed here.
        self.scheduleFactor = 0 #Metric of difficulty of fitting schedule
        self.period = [0]*(nPeriods+1) #Zero period should be left empty. Set the number of periods.

        AllPeople.append(self)
        if pType == 'msStudent':
            msStudents.append(self)
            Students.append(self)
        elif pType == 'hsStudent':
            hsStudents.append(self)
            Students.append(self)
        elif pType == 'T':
            Teachers.append(self)

    #Return the number of courses a student is taking.
    #Modified to use unavailable periods to increase priority.
    def setScheduleFactor(self):
        self.scheduleFactor = len(self.schedule) + 20*((sum(self.period) + 1)//nPeriods) #Adds 20 if there is less 2 free slots.
        return self.scheduleFactor


##################################################################################################################
#Courses
#All courses must be added before adding students.
##################################################################################################################
CourseList  = []    #CourseList is for Output.
PCourseList = []    #PCourseList is to optimize.
periodList  = []
#Creating class to contain information on courses.
class Course:
    #Student and Teachers
    def __init__(self, Name):
        self.name = Name
        #Default Perameters
        self.period = 0        #Zero period means course is waiting for assignment.
        self.people = []       #Person objects placed here corresponding to a roster (includes teachers and rooms).
        self.priority = 0      #Set order for PCourseList. High priority goes first.
        self.conflictCount = 0 #Number of courses in potential conflict with this one.

        CourseList.append(self)
        self.i = False #index in PCourseList
        self.previousCourse = False #Save course that comes before in PCourseList. 
        #This can be used to find which course was assigned just before this course.

    #Check if a group of students is free during nth period. 0th period is a place holder and is always free.
    def free(self, n):
        return all(p.period[n] == 0 for p in self.people)

    #Assign students as busy during a certain period.
    def AssignPeople(self,n):
        for p in self.people:
            p.period[n] += 1
            if p.period[n] > 1:
                print("ERROR {} is overbooked.".format(p.name))

    # Used in Main_Output. Use symmetry to remove redundant results.
    # Check if members of the i-th course are free during n-th period.
    # If True assign that period to the course and show students as busy.
    # If Fasle check for period n+1 to speed up process.
    def Assign(self,n):
        #Check that n is in bounds.
        if n == 0:
            #Assign should never be used this way.
            print("Assign Period should not be assigned to 0")
            return "Assign Period should not be assigned to 0"
        elif n > nPeriods:
            #print("No available periods for {0}".format(self.name))
            return False

        #Symmetrry Code
        for s in symList:
            #n should not be the last element in s.
            if n in s[:-1]:
                #Go from high to low. Make sure p is greater than n.
                for p in reversed(s[1:]):
                    if p <= n:
                        break
                    elif p not in periodList:
                        #print("Skip from {0}  to {1}".format(n, p))
                        n = p
                        break
                break

        #No Symmetry MWF
        # if n == 3:
        #     #print("Symettry Check 3")
        #     if  4 not in periodList:
        #         #print("Skip to 4")
        #         n = 4
        #3-fold Symmetry 6,7
        # if n == 6:
        #     #print("Symettry Check 6")
        #     if  7 not in periodList:
        #         #print("Skip to 7")
        #         n = 7     

        #Main part of function
        if self.free(n):
            self.period = n
            periodList.append(n)
            self.AssignPeople(n)
            #print("{0} is assigned to period {1}".format(self.name,n))
            return True

        else:
            if n < nPeriods:
                #print("{0} has conflict with period {1}. Checking period {2}".format(self.name, n, n+1))
                return self.Assign(n+1)
            elif n == nPeriods:
                #print("{0} has conflict with period {1}".format(self.name, n))
                return False
            else:
                print("Period is out of bounds")
                return "Period is out of bounds"

    #User specific assignment. Used in Human_Readable_Output.
    #If conflicts exist do nothing.
    #Otherwise assign that period to the course and show students as busy.
    def SlowAssign(self,n):
        #Check that n is in bounds.
        if n == 0:
            print("Assign Period should not be assigned to 0")

        elif n > nPeriods:
            print("Assign Period is out of bounds")

        #Main part of function
        else:
            if self.free(n):
                self.period = n
                periodList.append(n)
                self.AssignPeople(n)

            else:
                print("Error: Course was not assigned. Possible Conflict!")

    #Remove course period assignment as necessary.
    #Jump is used in continue function.
    def UnAssign(self):
        jump = 1

        #Check if course is at last period. If so also unassign last class.
        if self.period > nPeriods-1 and self.previousCourse != False: 
            jump += self.previousCourse.UnAssign()
        
        #UnAssign all people in this course.
        for p in self.people:
            p.period[self.period] = 0

        #UnAssign this course.
        self.period = 0
        periodList.pop()
        return jump

    #Prioritize Courses by how many students and how rigid those students schedules are
    def setPriority(self):
        xp = 0
        for p in self.people:
            xp += 10**p.scheduleFactor
        self.priority = 2*math.log(xp)

    def countConflicts(self):
        count = 0
        for c in CourseList:
            if any(p in c.people for p in self.people):
                count +=1
        self.conflictCount = count

def getOrder(c):
    return c.priority + c.conflictCount
def getPeriod(c):
    return c.period


##################################################################################################################
#Functions for People and Courses. This does all the prep work.
##################################################################################################################
#Add Teachers with availability
def addTeachers():
    #Get values from spreedsheet
    result = get_SheetRange(range_Teachers)
    values = result.get('values', [])
    #print(values)

    #Find and Set Column indices
    #print(values[0])
    nameCol        = values[0].index("Name")
    periodCol      = values[0].index("1")
    #print(nameCol, periodCol)
    values.pop(0)

    #Add Teachers
    for row in values:
        if row[nameCol] != '':
            #print(row[nameCol])
            newPerson = Person(row[nameCol], 'T')

            #Set Availability
            for i in range(nPeriods):
                newPerson.period[i+1]= int(row[i+periodCol])
            #print(newPerson.period)

    #Test
    # print("List of Teachers")
    # for t in Teachers:
    #     print(t.name)
        
#Add Students
def addStudents():
    #Get values from spreedsheet
    result = get_SheetRange(range_Students)
    values = result.get('values', [])
    #print(values)

    #Find and Set Column indices
    # print(values[0])
    lastNameCol    = values[0].index("Last")
    firstNameCol   = values[0].index("First")
    gradeCol       = values[0].index("Grade")
    # print(lastNameCol, firstNameCol, gradeCol)
    values.pop(0)
    
    #Add Students
    for row in values:
        if row[gradeCol] != '':
            if row[gradeCol] in ['6','7','8']:
                name = row[lastNameCol] + ', ' + row[firstNameCol]
                pType = 'msStudent'
            elif row[gradeCol] in ['9','10','11','12']:
                    name = row[lastNameCol] + ', ' + row[firstNameCol]
                    pType = 'hsStudent'
            else:
                    print("Grade Column Error {}".format(row[gradeCol]))

            newPerson = Person(name, pType)
            # print(newPerson.name)
    #Test
    # print("\nList of MS Students")
    # for m in msStudents:
    #     print(m.name)
    # print("\nList of HS Students")
    # for h in hsStudents:
    #     print(h.name)
    # print("\nList of Students")
    # for s in Students:
    #     print(s.name)

#Adds Teachers and Students
def addPeople():
    addTeachers()
    addStudents()

#Add Courses with rosters
def addCourses():
    #Get  values from spreedsheet
    result = get_SheetRange(range_Rosters)
    values = result.get('values', [])
    #Invert values so each row corresponds to a Course.
    # *values passes each row as an argument
    #Zip returns a iterator. So it is converted to a list.
    #This makes a list that has been transposed.
    zipped = list(itertools.zip_longest(*values))
    #This remove empty strings and NONE created by zip function.
    del values[:]
    for row in zipped:
        tempList = list(filter(None, row))
        values.append(tempList)
    # print("Rosters Zipped")
    # print(values)

    #Set Column indices
    nameCol        = 0
    firstPersonCol = 1

    #Add Course
    for row in values:
        if  row[nameCol] not in ["", " "]:
            newCourse = Course(row[nameCol])

            #Add People
            roster = row[firstPersonCol:]
            # print("\n")
            # print(roster)
            for name in roster:
                for p in AllPeople:
                    if name == p.name:
                        newCourse.people.append(p)
                        p.schedule.append(newCourse)
                        break
            # for p in newCourse.people:
            #     print(p.name)

            if len(newCourse.people) < 1:
                CourseList.remove(newCourse)
                # print('\nRemoved {}'.format(newCourse.name))
                # for c in CourseList:
                #     print(c.name)
        else:
            print('Error: Course name invalid - {}'.format(row[nameCol]))

#Algorithm for creating PCourseList.
#In other words prioritizing courses for assignment.
def PrioritizedCourseListCreator():
    #This needs to be run after all people and courses are added.
    for p in AllPeople:
        p.setScheduleFactor()
    for c in CourseList:
        c.setPriority()
        c.countConflicts()
    #PCourseList is empty. Adding a sorted version of CourseList
    PCourseList.extend(sorted(CourseList, key = getOrder, reverse = True))
    
    #Each course needs to know which course comes before or if it is the first.
    for i in range(len(PCourseList)):
        PCourseList[i].i = i
        if i > 0:
            PCourseList[i].previousCourse = PCourseList[i-1]


###################################################################################################################
def Creator():
    addPeople()
    addCourses()
    PrioritizedCourseListCreator()
###################################################################################################################


###################################################################################################################
#Output Functions
###################################################################################################################
def MasterSchedule(saveFile):
    master = []
    for c in CourseList:
        master.append(c.period)
    ms = open(saveFile, 'a')
    ms.write(", ".join(str(j) for j in master))
    ms.write("\n")
    ms.close()

def HumanReadableSchedule(saveFile):
    hrs = open(saveFile, 'w')
    for i in range(nPeriods+1):
        hrs.write("Period {0}\n".format(i))
        for c in CourseList:
            if c.period == i:
                hrs.write("{0}\n".format(c.name))
        hrs.write("\n")
    hrs.write("!!!!!!!!!!WIN!!!!!!!!!!\n\n")

    for s in Students:
        hrs.write("{0}\n".format(s.name))
        hrs.write("-----------------\n")
        s.schedule.sort(key = getPeriod)
        for c in s.schedule:
            hrs.write("{0} - {1}\n".format(c.period, c.name))
        hrs.write("\n")
    hrs.write("\n")

    for t in Teachers:
        hrs.write("{0}\n".format(t.name))
        hrs.write("-----------------\n")
        t.schedule.sort(key = getPeriod)
        for c in t.schedule:
            hrs.write("{0} - {1}\n".format(c.period, c.name))
        hrs.write("\n")
    hrs.write("\n")

    hrs.close()

def StudyHall(saveFile1, saveFile2, saveFile3):
    sh = open(saveFile1, 'w')
    for i in range(1,nPeriods+1):
        sh.write("Period {0} \n".format(i))
        for p in Students:
            if p.period[i] == 0:
                sh.write("{0} \n".format(p.name))
        sh.write("\n\n")
    sh.close()

    msSh = open(saveFile2, 'w')
    for i in range(1,nPeriods+1):
        msSh.write("Period {0} \n".format(i))
        for p in msStudents:
            if p.period[i] == 0:
                msSh.write("{0} \n".format(p.name))
        msSh.write("\n\n")
    msSh.close()

    hsSh = open(saveFile3, 'w')
    for i in range(1,nPeriods+1):
        hsSh.write("Period {0} \n".format(i))
        for p in hsStudents:
            if p.period[i] == 0:
                hsSh.write("{0} \n".format(p.name))
        hsSh.write("\n\n")
    hsSh.close()


###################################################################################################################
#Main Scheduling Function - Subfunctions - Main Loop
###################################################################################################################
#Returns which course was the last to be assigned a period.
def lastAttempt():
    for c in PCourseList:
        if c.period == 0:
            return c.previousCourse
    return PCourseList[len(PCourseList)-1]

def ProgressMonitor(nMon,nMonMax):
    if nMon < nMonMax:
        return nMon + 1
    else:
        print(periodList)
        return 0


###################################################################################################################
#Assign the n-th class and higher.
#The first course nStart will be assigned starting with nPeriod.
#The following courses will be assigned starting with period 1.
nMonitor = 0
nMonitorMax = 10**6 #Number loops before displaying progress.

def MasterAssign(nStart,nPeriod,outputType):
    #Get the course object and the number of courses.
    cC = PCourseList[nStart]
    nC = len(PCourseList)
    #Print updates to console
    global nMonitor
    nMonitor = ProgressMonitor(nMonitor,nMonitorMax)

    #Main part of function.
    if cC.period == 0:
        proceed = cC.Assign(nPeriod)
        if proceed == True:
            if nStart < nC-1:
                #print("Working on {0}".format(PCourseList[nStart+1].name))
                return MasterAssign(nStart+1,1,outputType)
            elif nStart == nC-1:
                if outputType == "Master":
                    #export schedule in some useable csv file
                    MasterSchedule(solutionsCSV)
                    #New Code: Potential issue if nPeriod = nPeriods
                    if nPeriod < nPeriods:
                        #Old Code
                        restartPeriod = cC.period
                        cC.UnAssign()
                        return MasterAssign(nStart,restartPeriod+1,outputType)
                    else:
                        return False
                elif outputType == "Formatted":
                    HumanReadableSchedule(solution)
                    StudyHall(studyHall)
                    print("!!!!!!!!!!WIN!!!!!!!!!!")
                    return True
                else:
                    print("Output Type not recognized.")
                    return "Output Type not recognized."
            else:
                print("Possible Error. nStart is out of bounds.")
                return "Possible Error. nStart is out of bounds."
        elif proceed == False:
            return False
        else:
            print("Assign function not behaving properly.")
            return "Assign function not behaving properly."      
    else:
        if nStart < nC-1:
            print("Error: {0} is already assigned to period {1}".format(cC.name,cC.period))
            return MasterAssign(nStart+1,1,outputType)
        else:
            print("Is this working? Why are all courses assigned and program is not done?") #This should never happen.
            return "Is this working? Why are all courses assigned and program is not done?"


###################################################################################################################
#modified to include bigger jumps
#The program will not reassign any courses before halt. 
#Ex. if halt = 5, then periods 0-4 are set in stone on their first pass.
#Only usefull if you know a solution. Default is halt = 0.
def Continue(outputType, halt):
    #Need a copy of the PeriodList before running UnAssign  
    previousPeriodList = periodList[:] # Copies all the elements in the array

    last = lastAttempt()
    if last == False: #Prevent from reassigning courses lower than this.
        print("Schedule is finished.")
        g = open(solutionsCSV, 'a')
        g.write("Schedule is finished.")
        g.close()
        return True

    jumpCounter = last.UnAssign()-1
    #print(jumpCounter)
    k = last.i-jumpCounter
    #print(k)

    return MasterAssign(k, previousPeriodList[k]+1,outputType)


###################################################################################################################

#Run this once at the end of this module.
#This will import all the information from the google sheet file.
Creator()
##################################################################################
# Main Check: Code only execute when you run the module as a program.
# It will not execute when you import your module.
if __name__ == '__main__':
    print('\nPCourseList\n')
    for c in PCourseList:
        if c.previousCourse == False:
            print(repr(c.period).rjust(1), ('%.2f' %(c.conflictCount+c.priority)).rjust(7), repr(c.conflictCount).rjust(3), ('%.2f' %(c.priority)).rjust(6), '', c.name.ljust(70), repr(c.i).rjust(2))
        else:
            print(repr(c.period).rjust(1), ('%.2f' %(c.conflictCount+c.priority)).rjust(7), repr(c.conflictCount).rjust(3), ('%.2f' %(c.priority)).rjust(6), '', c.name.ljust(70), repr(c.i).rjust(2), '', c.previousCourse.name)
