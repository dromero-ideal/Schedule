import os

#Local Files for Output
##################################################################################
outFolder = os.getcwd() + '\\Output\\'
#Create output folder if it doesn't exist.
if not os.path.exists(outFolder):
    os.makedirs(outFolder)

#Output files
solutionsCSV = outFolder + 'Solutions.csv'

solution     = outFolder + 'Solution.txt'
studyHall    = outFolder + 'StudyHall.txt'
MSstudyHall  = outFolder + 'MS StudyHall.txt'
HSstudyHall  = outFolder + 'HS StudyHall.txt'

basic        = outFolder + 'Basic Info.txt'

ErrorLog     = outFolder + 'Error Log.txt'


#Local Files for Data
##################################################################################
dataFolder = os.getcwd() + '\\Data\\'
#Create data folder if it doesn't exist.
if not os.path.exists(dataFolder):
    os.makedirs(dataFolder)

#ID for Google Sheets file
sheetsIDtxt = dataFolder + 'sheetsID.txt'
#Credentials
credential_path = os.path.join(dataFolder,'ScheduleMaker.json')

#Useful Ranges in Spread Sheet
##################################################################################
#Whole sheets
range_Teachers = 'Teacher Assignments' #Names and availability.
range_Students = 'Next Semester'       #Names only.
range_Rosters  = 'Rosters'             #Uses all information.

range_nPeriods = range_Teachers + '!1:1'


#Google Sheets API - Find Sheet and store data.
##################################################################################
from httplib2          import Http
from apiclient         import discovery
from oauth2client      import client
from oauth2client      import tools
from oauth2client.file import Storage

# If modifying these scopes, delete your previously saved credentials at ~/.credentials/ScheduleMaker.json
SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    #Storage is an object used to store credentials.
    #It can retrieve and update credentials from its associated file.
    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        #Attempts to open an authorization server page in the user's web browser.
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        credentials = tools.run_flow(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def updateSpreadSheetID():
    """Ask for target spreadsheet ID and stores the values.
    
    Creates a Sheets API service object.
    """
    sheetsID = input('Enter the target spreadsheet ID. The ID is the value\n'
                     'between "/d/" and "/edit" in the URL of your spreadsheet.\n'
                     '---> ')
    s = open(sheetsIDtxt, 'w')
    s.write(sheetsID)
    s.close()
    return sheetsID

def get_sheetID():
    try:
        s = open(sheetsIDtxt, 'r')
        sheetsID = s.read()
        s.close()
        return sheetsID
    except:
        return updateSpreadSheetID()

def get_SheetRange(rangeName):
    """Checks credentials and target spreadsheet ID.

    Creates a Sheets API service object.

    Any Errors should result in requesting new credentials or spreadsheet ID.
    """
    credentials = get_credentials()
    http = credentials.authorize(Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?version=v4')
    service = discovery.build('sheets', 'v4', http=http, discoveryServiceUrl=discoveryUrl)
    sheetsID = get_sheetID()

    request = service.spreadsheets().values().get(spreadsheetId=sheetsID, range=rangeName)
    response = request.execute()
    return response

def testSheet():
    """Checks credentials and target spreadsheet ID.

    Creates a Sheets API service object.

    Any Errors should result in requesting new credentials or spreadsheet ID.
    """
    credentials = get_credentials()
    http = credentials.authorize(Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?version=v4')
    service = discovery.build('sheets', 'v4', http=http, discoveryServiceUrl=discoveryUrl)
    sheetsID = get_sheetID()
    testRange = range_Teachers

    result = get_SheetRange(testRange)

    #This code is just for testing.
    values = result.get('values', [])
    if not values:
        print('No data found.')
    else:
        #Each row read is returned as a list of strings.
        for row in values:
            if  row != []:
                print(', '.join(row))

def get_nPeriods():
    result = get_SheetRange(range_nPeriods)
    values = result.get('values', [])
    #print(values)

    temp_nPeriods = 0
    for col in values[0]:
        #print(col)
        if col.isdigit():
            temp_nPeriods = int(col)

    return temp_nPeriods

#There is a potential bug in this current code.
#Need to only grab consecutive periods.
#Otherwise assign will skip over available periods.
#Potential fix added to to setup test.
def get_Symmetry():
    result = get_SheetRange(range_Teachers)
    values = result.get('values', [])
    #Invert values so each row corresponds to a Period.
    # *values passes each row as an argument
    #Zip returns a iterator. So it is converted to a list.
    #This makes a list that has been transposed.
    values = list(zip(*values))
    values = [item for item in values if item[0].isdigit()]
    #print(values)

    #Search through data and find symmetry of schedule.
    #Each loop should eliminate the first period (row) and any matches.
    symList = []
    while len(values) > 1:
        first = values.pop(0)
        tempList = [int(first[0])]
        newValues = []
        for row in values:
            #See if consecutive periods match in terms of teacher availability.
            #If so keep track of matches.
            #If non-match is found stop. Pick up at non-match. 
            if( first[1:] == row[1:] ):
                tempList.append(int(row[0]))
            else:
                #Old Code: newValues.append(row)
                #This code should fix the bug.
                i = values.index(row)
                newValues = values[i:]
                break
        if len(tempList) > 1:
            symList.append(tempList)
        values = newValues
    return symList

##################################################################################
# Main Check: Code only execute when you run the module as a program.
# It will not execute when you import your module.
if __name__ == '__main__':
    testSheet()
