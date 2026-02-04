#Use this script to capture TQP statistics from the prepared logs in the input directory (PreparedLogs)
#The statistics process includes determining the following
#    1. A list of calls in each of the TQP categories
#    2. Number of TX logs, Non-TX logs, DX Logs
#    3. Number of TX-TX QSOs, TX-NTX QSOs, TX-DX QSOs
#    4. Number of QSOs on each band
#    5. Number of QSOs on each mode
#    6. Number of counties active and number of QSOs from each

#------------------------------------------------------------------------------------------------
# Category Coding for power, mode, location, and number of operators
#
#     powercode QRP = 0
#               LOW = 1
#               HIGH = 2
#     modecode  CWO = 0
#               PHO = 1
#               DGO = 2
#               MIX = 3   
#     location  DX = 0
#               NTX = 1  (non-TX US/VE)
#               TX(Fixed) = 2
#               TX(Mobile) = 3
#     numOps    Single = 0
#               Multi = 1 
#-----------------------------------------------------------------------------------------------
QRPCODE = 0
LOWCODE = 1
HIGHCODE = 2
CWOCODE = 0
PHOCODE = 1
DGOCODE = 2
MIXCODE = 3
DXCODE = 0
NTXCODE = 1
TXFCODE = 2
TXMCODE = 3
SOPCODE = 0
MOPCODE = 1

# import a list of Texas county abbreviations (used to detect that station is/isnot a TX station)
#-----------------------------------------------------------------------------------------------
TXabbsFile = 'C:\\Users\\18326\\TexasQsoParty\\Data\\TXCTY_Abbrevs.txt'
#-----------------------------------------------------------------------------------------------
#
TXabbList = []
with open(TXabbsFile, 'r') as f:
    TXabbrevsList = f.readlines()
for abb in TXabbrevsList:
    TXabbList.append(abb.rstrip())

#-----------------------------------------------------------------------------------------------
# TXCounty = Define a class for holding county abbreviation and number of QSOs sent from the county 
#-----------------------------------------------------------------------------------------------
class TXCounty:
    def __init__(self, name, sentQsos, rcvdQsos):
        self.name = name.rstrip()
        self.sentQsos = sentQsos
        self.rcvdQsos = rcvdQsos

    def display(self):
        print(f"Name, {self.name}, SentQsos, {self.sentQsos}, RcvdQsos, {self.rcvdQsos}")


TXCountiesList = []
for abb in TXabbrevsList:
    TXCountiesList.append(TXCounty(abb, 0, 0))

def updateCountySentQsos(aTXCountiesList, abb):
    for item in aTXCountiesList:
        if(item.name == abb):
            item.sentQsos += 1
            break

def updateCountyRcvdQsos(aTXCountiesList, abb):
    for item in aTXCountiesList:
        if(item.name == abb):
            item.rcvdQsos += 1
            break

# import a list of Non-Texas (US/VE) QTH abbreviations (used to detect that station is non-TX US/VE)
#-----------------------------------------------------------------------------------------------
NonTXabbsFile = 'C:\\Users\\18326\\TexasQsoParty\\Data\\WVE_Abbrevs.txt'
#-----------------------------------------------------------------------------------------------

NonTXabbList = []
with open(NonTXabbsFile, 'r') as f:
    NonTXabbrevsList = f.readlines()
for abb in NonTXabbrevsList:
    NonTXabbList.append(abb.rstrip())
 
#-----------------------------------------------------------------------------------------------
# Set the directory that contains the prepared logs
#-----------------------------------------------------------------------------------------------
PreparedLogs = 'C:\\Users\\18326\\TexasQsoParty\\TQP-2025\\LogProcessing\\PreparedLogs'
#the files in PreparedLogs are named CallSign-Prep.LOG and are the only files in that directory
#
#-------------------------------Define the set of ambiguous QTHs--------------------------------
SetOfAmbigDxQth = {"ON","PA", "CT", "TN", "LA","HI", "OK", "CO", "OH"}
#-----------------------------------------------------------------------------------------------
#-------------------------------Define the set of Canadian prefixes-----------------------------
CanadianPrefixes = {"CF", "CG", "CH", "CI", "CJ", "CK", "CY", "CZ", "VA", "VB", "VC", "VD", "VE", 
"VF", "VG", "VO", "VX", "VY", "XJ", "XK", "XL", "XM", "XN", "XO"}
#-----------------------------------------------------------------------------------------------
#-------------------------------Define the set of US prefixes-----------------------------------
USPrefixes = {"K", "N", "W", "AA", "AB", "AC", "AD", "AE", "AF", "AG", "AH", "AI", "AJ", "AK", "AL"}
#-----------------------------------------------------------------------------------------------
#---------------------------------Import some functions from the Python library-----------------
# Import the os module, for the os.walk function and the datetime module
import shutil
import os
from pathlib import Path
from datetime import datetime, timezone

#-----------------------------------------------------------------------------------------------
#---------------------------------Define the date time format-----------------------------------
# Define the format of the input time string
format_string = "%Y-%m-%d %H%M"
date_format = "%Y-%m-%d"

#-----------------------------------------------------------------------------------------------
#-----------------------Define the start and end times of the TQP sessions for this year--------
starttimeday1_string = "2025-09-20 1400"
endtimeday1_string = "2025-09-21 0200"
starttimeday2_string = "2025-09-21 1400"
endtimeday2_string = "2025-09-21 2000"

#-----------------------------------------------------------------------------------------------
unix_timestamp_int_starttimeday1 = 0
unix_timestamp_int_endtimeday1 = 0
unix_timestamp_int_starttimeday2 = 0
unix_timestamp_int_endtimeday2 = 0

#define some functions for checking validity of QSO entries
# -------------------------------------------------------------------------------
# -----------------get the start time of first session as an integer-------------
# -------------------------------------------------------------------------------
# Parse the time string into a datetime object
dt_object_starttimeday1 = datetime.strptime(starttimeday1_string, format_string)

# Get the Unix timestamp (float)
unix_timestamp_float_starttimeday1 = dt_object_starttimeday1.timestamp()

# Convert to integer
unix_timestamp_int_starttimeday1 = int(unix_timestamp_float_starttimeday1)

# -------------------------------------------------------------------------------
# -----------------get the end time of first session as an integer-------------
# -------------------------------------------------------------------------------
# Parse the time string into a datetime object
dt_object_endtimeday1 = datetime.strptime(endtimeday1_string, format_string)

# Get the Unix timestamp (float)
unix_timestamp_float_endtimeday1 = dt_object_endtimeday1.timestamp()

# Convert to integer
unix_timestamp_int_endtimeday1 = int(unix_timestamp_float_endtimeday1)

# -------------------------------------------------------------------------------
# -----------------get the start time of second session as an integer------------
# -------------------------------------------------------------------------------
# Parse the time string into a datetime object
dt_object_starttimeday2 = datetime.strptime(starttimeday2_string, format_string)

# Get the Unix timestamp (float)
unix_timestamp_float_starttimeday2 = dt_object_starttimeday2.timestamp()

# Convert to integer
unix_timestamp_int_starttimeday2 = int(unix_timestamp_float_starttimeday2)

# -------------------------------------------------------------------------------
# -----------------get the end time of second session as an integer--------------
# -------------------------------------------------------------------------------
# Parse the time string into a datetime object
dt_object_endtimeday2 = datetime.strptime(endtimeday2_string, format_string)

# Get the Unix timestamp (float)
unix_timestamp_float_endtimeday2 = dt_object_endtimeday2.timestamp()

# Convert to integer
unix_timestamp_int_endtimeday2 = int(unix_timestamp_float_endtimeday2)

#--------------------------------------------------------------------------------------------------------------
# Setup a list of start times of the hours of TQP for use in the BIC determination
#--------------------------------------------------------------------------------------------------------------
unix_timestamp_int_TQPHours_starttimes = []
unix_timestamp_int_TQPHours_starttimes.append(unix_timestamp_int_starttimeday1)             #start of hour 0 9am
unix_timestamp_int_TQPHours_starttimes.append(unix_timestamp_int_starttimeday1 + 3600)      #start of hour 1 10am
unix_timestamp_int_TQPHours_starttimes.append(unix_timestamp_int_starttimeday1 + 3600*2)    #start of hour 2 11am
unix_timestamp_int_TQPHours_starttimes.append(unix_timestamp_int_starttimeday1 + 3600*3)    #start of hour 3 noon
unix_timestamp_int_TQPHours_starttimes.append(unix_timestamp_int_starttimeday1 + 3600*4)    #start of hour 4 1pm
unix_timestamp_int_TQPHours_starttimes.append(unix_timestamp_int_starttimeday1 + 3600*5)    #start of hour 5 2pm
unix_timestamp_int_TQPHours_starttimes.append(unix_timestamp_int_starttimeday1 + 3600*6)    #start of hour 6 3pm
unix_timestamp_int_TQPHours_starttimes.append(unix_timestamp_int_starttimeday1 + 3600*7)    #start of hour 7 4pm
unix_timestamp_int_TQPHours_starttimes.append(unix_timestamp_int_starttimeday1 + 3600*8)    #start of hour 8 5pm
unix_timestamp_int_TQPHours_starttimes.append(unix_timestamp_int_starttimeday1 + 3600*9)    #start of hour 9 6pm 
unix_timestamp_int_TQPHours_starttimes.append(unix_timestamp_int_starttimeday1 + 3600*10)   #start of hour 10 7pm
unix_timestamp_int_TQPHours_starttimes.append(unix_timestamp_int_starttimeday1 + 3600*11)   #start of hour 11 

unix_timestamp_int_TQPHours_starttimes.append(unix_timestamp_int_starttimeday2)             #start of hour 12 9am
unix_timestamp_int_TQPHours_starttimes.append(unix_timestamp_int_starttimeday2 + 3600)      #start of hour 13 10am
unix_timestamp_int_TQPHours_starttimes.append(unix_timestamp_int_starttimeday2 + 3600*2)    #start of hour 14 11am
unix_timestamp_int_TQPHours_starttimes.append(unix_timestamp_int_starttimeday2 + 3600*3)    #start of hour 15 noon 
unix_timestamp_int_TQPHours_starttimes.append(unix_timestamp_int_starttimeday2 + 3600*4)    #start of hour 16 1pm
unix_timestamp_int_TQPHours_starttimes.append(unix_timestamp_int_starttimeday2 + 3600*5)    #start of hour 17 2pm 
 

for item in unix_timestamp_int_TQPHours_starttimes:
    # Convert to a datetime object in UTC
    dt_object_utc = datetime.fromtimestamp(item)
    #dt_object_utc = datetime.fromtimestamp(item, tz=timezone.utc)

    # Format the UTC datetime object
    formatted_time_utc = dt_object_utc.strftime("%Y-%m-%d %H%M")

    print(f"Formatted start of hour (UTC): {formatted_time_utc}")

# -------------------------------------------------------------------------------
# ---------function for getting time of QSO as a unix integer -------------------
# -------------------------------------------------------------------------------
def TimeOfQsoAsUnixTimeStamp(aQsoLine):
    substrings = aQsoLine.split()
    date_string = substrings[3] + " " + substrings[4]
    format_pattern = "%Y-%m-%d %H%M"

    dt_object = datetime.strptime(date_string, format_pattern)
    unix_timestamp = dt_object.timestamp()
    return(unix_timestamp)

# -------------------------------------------------------------------------------
# ---------function for getting index of QSO hour as an integer -----------------
# -------------------------------------------------------------------------------
def IndexOfQsoHourAsInteger(aQsoLine):
    substrings = aQsoLine.split()
    date_string = substrings[3] + " " + substrings[4]
    format_pattern = "%Y-%m-%d %H%M"

    dt_object = datetime.strptime(date_string, format_pattern)
    unix_timestamp = dt_object.timestamp()
    rtnIndex = -1
    if(unix_timestamp >= unix_timestamp_int_TQPHours_starttimes[0] and unix_timestamp < unix_timestamp_int_TQPHours_starttimes[1]):
        rtnIndex = 0 
    elif(unix_timestamp >= unix_timestamp_int_TQPHours_starttimes[1] and unix_timestamp < unix_timestamp_int_TQPHours_starttimes[2]):
        rtnIndex = 1 
    elif(unix_timestamp >= unix_timestamp_int_TQPHours_starttimes[2] and unix_timestamp < unix_timestamp_int_TQPHours_starttimes[3]):
        rtnIndex = 2 
    elif(unix_timestamp >= unix_timestamp_int_TQPHours_starttimes[3] and unix_timestamp < unix_timestamp_int_TQPHours_starttimes[4]):
        rtnIndex = 3
    elif(unix_timestamp >= unix_timestamp_int_TQPHours_starttimes[4] and unix_timestamp < unix_timestamp_int_TQPHours_starttimes[5]):
        rtnIndex = 4
    elif(unix_timestamp >= unix_timestamp_int_TQPHours_starttimes[5] and unix_timestamp < unix_timestamp_int_TQPHours_starttimes[6]):
        rtnIndex = 5
    elif(unix_timestamp >= unix_timestamp_int_TQPHours_starttimes[6] and unix_timestamp < unix_timestamp_int_TQPHours_starttimes[7]):
        rtnIndex = 6
    elif(unix_timestamp >= unix_timestamp_int_TQPHours_starttimes[7] and unix_timestamp < unix_timestamp_int_TQPHours_starttimes[8]):
        rtnIndex = 7
    elif(unix_timestamp >= unix_timestamp_int_TQPHours_starttimes[8] and unix_timestamp < unix_timestamp_int_TQPHours_starttimes[9]):
        rtnIndex = 8
    elif(unix_timestamp >= unix_timestamp_int_TQPHours_starttimes[9] and unix_timestamp < unix_timestamp_int_TQPHours_starttimes[10]):
        rtnIndex = 9
    elif(unix_timestamp >= unix_timestamp_int_TQPHours_starttimes[10] and unix_timestamp < unix_timestamp_int_TQPHours_starttimes[11]):
        rtnIndex = 10
    elif(unix_timestamp >= unix_timestamp_int_TQPHours_starttimes[11] and unix_timestamp < unix_timestamp_int_TQPHours_starttimes[12]):
        rtnIndex = 11
    elif(unix_timestamp >= unix_timestamp_int_TQPHours_starttimes[12] and unix_timestamp < unix_timestamp_int_TQPHours_starttimes[13]):
        rtnIndex = 12
    elif(unix_timestamp >= unix_timestamp_int_TQPHours_starttimes[13] and unix_timestamp < unix_timestamp_int_TQPHours_starttimes[14]):
        rtnIndex = 13
    elif(unix_timestamp >= unix_timestamp_int_TQPHours_starttimes[14] and unix_timestamp < unix_timestamp_int_TQPHours_starttimes[15]):
        rtnIndex = 14
    elif(unix_timestamp >= unix_timestamp_int_TQPHours_starttimes[15] and unix_timestamp < unix_timestamp_int_TQPHours_starttimes[16]):
        rtnIndex = 15
    elif(unix_timestamp >= unix_timestamp_int_TQPHours_starttimes[16] and unix_timestamp < unix_timestamp_int_TQPHours_starttimes[17]):
        rtnIndex = 16

    return(rtnIndex)


# -------------------------------------------------------------------------------
# -----------------function for checking call signs------------------------------
# -------------------------------------------------------------------------------
def IsValidCall(aCall):
    character_to_find = "/"
    hasASlash = character_to_find in aCall 
    onlyAlphaNum = aCall.isalnum() or hasASlash 
    atLeastLen3 = len(aCall) >= 3
    atLeastOneNum = any(char.isdigit() for char in aCall)
    return(onlyAlphaNum and atLeastLen3 and atLeastOneNum)

# -------------------------------------------------------------------------------
# -----------------function for checking Qth ------------------------------------
# -------------------------------------------------------------------------------
def IsValidQth(aQth):
    notTexas = aQth != "TX" 
    lenLessThanFive = len(aQth) <= 4
    return(lenLessThanFive and notTexas) 

# -------------------------------------------------------------------------------
# -----------------functions for checking frequency------------------------------
# -----------------input must be an integer--------------------------------------
def IsA160KHz(aFreqKHz):
    return(1800 <= aFreqKHz and aFreqKHz <= 2000)

def IsA80KHz(aFreqKHz):
    return(3500 <= aFreqKHz and aFreqKHz <= 4000)

def IsA40KHz(aFreqKHz):
    return(7000 <= aFreqKHz and aFreqKHz <= 7300)

def IsA20KHz(aFreqKHz):
    return(14000 <= aFreqKHz and aFreqKHz <= 14350)

def IsA15KHz(aFreqKHz):
    return(21000 <= aFreqKHz and aFreqKHz <= 21450)

def IsA10KHz(aFreqKHz):
    return(28000 <= aFreqKHz and aFreqKHz <= 29700)

def IsA6KHz(aFreqKHz):
    return(50000 <= aFreqKHz and aFreqKHz <= 54000)

def IsA2KHz(aFreqKHz):
    return(144000 <= aFreqKHz and aFreqKHz <= 148000)

def IsA2KHz(aFreqKHz):
    return(144000 <= aFreqKHz and aFreqKHz <= 148000)

def IsA125KHz(aFreqKHz):
    return(222000 <= aFreqKHz and aFreqKHz <= 225000)

def IsValidTQPKHz(aKHz):
    isLowHF = IsA160KHz(aKHz) or IsA80KHz(aKHz) or IsA40KHz(aKHz) 
    isHighHF = IsA20KHz(aKHz) or IsA15KHz(aKHz) or IsA10KHz(aKHz)
    isVUF = IsA6KHz(aKHz) or IsA2KHz(aKHz) or IsA125KHz(aKHz)
    return(isLowHF or isHighHF or isVUF)

#---------------------------------------------------------------------------------
#                          Function for converting KHZ to a band
#---------------------------------------------------------------------------------
def convertKHzToBand(aFreqKHz):
    if(aFreqKHz == 160):
        return(160)
    if(aFreqKHz == 80):
        return(80)
    if(aFreqKHz == 40):
        return(40)
    if(aFreqKHz == 20):
        return(20)
    if(aFreqKHz == 15):
        return(15)
    if(aFreqKHz == 10):
        return(10)
    if(aFreqKHz == 6):
        return(6)
    if(aFreqKHz == 2):
        return(2)
    if(aFreqKHz == 1.25):
        return(1.25)

    if(1800 <= aFreqKHz and aFreqKHz <= 2000):
        return(160)
    if(3500 <= aFreqKHz and aFreqKHz <= 4000):
        return(80)    
    if(7000 <= aFreqKHz and aFreqKHz <= 7300):
        return(40)
    if(14000 <= aFreqKHz and aFreqKHz <= 14350):
        return(20)
    if(21000 <= aFreqKHz and aFreqKHz <= 21450):
        return(15)
    if(28000 <= aFreqKHz and aFreqKHz <= 29700):
        return(10)
    if(50000 <= aFreqKHz and aFreqKHz <= 54000):
        return(6)
    if(144000 <= aFreqKHz and aFreqKHz <= 148000):
        return(2)
    if(222000 <= aFreqKHz and aFreqKHz <= 225000):
        return(1.25)
        
# -------------------------------------------------------------------------------
# -----------------function for checking mode------------------------------------
# -------------------------------------------------------------------------------
def IsValidTQPMode(aMode):
    isCW = aMode == "CW"
    isPH = aMode == "PH"
    isDG = aMode == "DG"
    isRY = aMode == "RY"
    isFM = aMode == "FM"
    return(isCW or isPH or isDG or isRY or isFM)

# -------------------------------------------------------------------------------
# -----------------function for checking date time-------------------------------
# -------------------------------------------------------------------------------
def IsValidTQPDateTime(aLogDate, aLogTime, aStartDT1, aEndDT1, aStartDT2, aEndDT2):
    aLogDtAsString = aLogDate + " " + aLogTime

    # Parse the time string into a datetime object
    dt_object_logtime = datetime.strptime(aLogDtAsString, format_string)

    # Get the Unix timestamp (float)
    unix_timestamp_float_logtime = dt_object_logtime.timestamp()

    # Convert to integer
    unix_timestamp_int_logtime = int(unix_timestamp_float_logtime)

    # check log time in session 1
    isInSession1 = aStartDT1 <= unix_timestamp_int_logtime <= aEndDT1
 
    # check log time in session 2
    isInSession2 = aStartDT2 <= unix_timestamp_int_logtime <= aEndDT2

    return (isInSession1 or isInSession2)

# -------------------------------------------------------------------------------
# -----------------function for checking the format of a date--------------------
# -------------------------------------------------------------------------------
def check_date_format(date_string, date_format):
    try:
        datetime.strptime(date_string, date_format)
        return True  # Date string matches the format
    except ValueError:
        return False # Date string does not match the format or is an invalid date

# -------------------------------------------------------------------------------
# -----------------function for checking the format of a time--------------------
# -------------------------------------------------------------------------------
def check_time_format(time_string):
    lenOk = len(time_string) == 4
    alldigs = time_string.isdigit()
    return(lenOk and alldigs)
    
# -------------------------------------------------------------------------------
# -----------------function for checking a QSO log line--------------------------
# -------------------------------------------------------------------------------
def IsAValidQsoLine(aline):
    substrings = aline.split()
    errCode = 0
    if(substrings[0] != "QSO:"):
        return(errCode)
    if(len(substrings) != 11):
    	return(-1)
    errCode = 8;
    freqOk = IsValidTQPKHz(int(substrings[1]))
    modeOk = IsValidTQPMode(substrings[2])
    dateFormatOk = check_date_format(substrings[3], date_format)
    timeFormatOk = check_time_format(substrings[4])
    if(dateFormatOk and timeFormatOk):
        dateTimeOk = IsValidTQPDateTime(substrings[3], substrings[4], unix_timestamp_int_starttimeday1, unix_timestamp_int_endtimeday1, unix_timestamp_int_starttimeday2, unix_timestamp_int_endtimeday2)
    else:
        dateTimeOk = False
    sentCallOk = IsValidCall(substrings[5])
    sentQthOk = IsValidQth(substrings[7])
    rcvdCallOk = IsValidCall(substrings[8])
    rcvdQthOk = IsValidQth(substrings[10])
    if not freqOk:
        errCode = 1
    if not modeOk:
        errCode = 2
    if not dateTimeOk:
        errCode = 3
    if not sentCallOk:
        errCode = 4
    if not sentQthOk:
        errCode = 5
    if not rcvdCallOk:
        errCode = 6
    if not rcvdQthOk:
        errCode = 7
    return(errCode)

#-----------------------------------------------------------------------------------------
#------------Function for getting the full path file names in a directory-----------------
#-----------------------------------------------------------------------------------------
def get_all_files(directory_path):
    """
    Traverses a directory and its subdirectories to get a list of all file paths.

    Args:
        directory_path (str): The path to the starting directory.

    Returns:
        list: A list of absolute paths to all files found.
    """
    file_list = []
    for root, _, files in os.walk(directory_path):
        for file in files:
            file_list.append(os.path.join(root, file))
    return file_list


#-----------------------------------------------------------------------------------------
#------------Function for getting lines from a full path file name -----------------------
#-----------------------------------------------------------------------------------------
def get_lines_from_file(filepath):
    """
    Reads a text file and returns a list where each element is a line from the file.

    Args:
        filepath (str): The path to the text file.

    Returns:
        list: A list of strings, where each string represents a line from the file.
              Each line will include the newline character ('\n') if present in the file.
    """
    try:
        with open(filepath, 'r') as file:
            lines = file.readlines()
        return lines
    except FileNotFoundError:
        print(f"Error: The file '{filepath}' was not found.")
        return []
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

#-----------------------------------------------------------------------------------------
#------------Function for moving a source file to a destination directory ----------------
#-----------------------------------------------------------------------------------------
def MoveFileToNewDestination(destination_directory, source_file):
    try:
        # Ensure the destination directory exists (optional, shutil.move can create it)
        os.makedirs(destination_directory, exist_ok=True)

        # Construct the full destination path, including the desired new file name
        # If you want to keep the same file name, use os.path.basename(source_file)
        destination_file = os.path.join(destination_directory, os.path.basename(source_file))

        # Move the file
        shutil.move(source_file, destination_file)
        print(f"File '{source_file}' successfully moved to '{destination_file}'")

    except FileNotFoundError:
        print(f"Error: Source file '{source_file}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

#--------------------------------------------------------------------------------
#            Function for testing a prefix for being Canadian
#--------------------------------------------------------------------------------
def PrefixIsCanadian(apfx):
    return(apfx in CanadianPrefixes)

#--------------------------------------------------------------------------------
#            Function for testing a prefix for being USA
#--------------------------------------------------------------------------------
def PrefixIsUS(apfx):
    if(len(apfx) <= 0):
        return(False)
    if(apfx[0] == "K" or apfx[0] == "N" or apfx[0] == "W"):
        return(True)
    return(apfx in USPrefixes)


#--------------------------------------------------------------------------------
#            Function for getting the prefix from a callsign
#--------------------------------------------------------------------------------
def getPrefixFromCallSign(aCall):
    """
    Returns the substring of an alphanumeric string up to the first number.

    Args:
        aCall (str): The input alphanumeric string.

    Returns:
        str: The substring before the first number, or the entire string if no number is found.
    """
    for i, char in enumerate(aCall):
        if char.isdigit():
            return aCall[:i]
    return aCall  # Return the entire string if no number is found

#--------------------------------------------------------------------------------
#            Function for returning true if the call is a DX callsign
#--------------------------------------------------------------------------------
def IsDXCall(acall):
    pfx = getPrefixFromCallSign(acall)
    isUSACall = PrefixIsUS(pfx)
    isVECall = PrefixIsCanadian(pfx)
    return(not isUSACall and not isVECall)

#--------------------------------------------------------------------------------
#   Function for checking whether a sent or rcvd QTH needs to have "DX" appended 
#         returns     0 if no change is required, 
#         returns     1 if Sent QTH needs changing (DX appended to SentQTH)
#         returns     2 if Rcvd QTH needs changing (DX appended to RcvdQTH)
#--------------------------------------------------------------------------------
def IsALogQsoLineToChange(aline):
    substrings = aline.split()
    changeCode = 0
    if(substrings[0] != "QSO:"):
        return(changeCode)
    if(len(substrings) == 11 or len(substrings)==12):
        SCallIsDX = IsDXCall(substrings[5])
        RCallIsDX = IsDXCall(substrings[8])
        SQth = substrings[7]
        RQth = substrings[10]
        SentQthIsAmbig = SQth in SetOfAmbigDxQth
        RcvdQthIsAmbig = RQth in SetOfAmbigDxQth
        if(SCallIsDX and SentQthIsAmbig):
            return(1) 
        if(RCallIsDX and RcvdQthIsAmbig):
            return(2) 
        else:
            return(0)    
    else:
        return(-1)

def ReformatQsoLine(qsoLine, logList, chgCode):
    qso = qsoLine.split()
    if(len(qso) < 11):
        return(qsoLine + "    [ERROR: Missing qso elements]")
    bandstr = str(convertKHzToBand(int(qso[1])))
    newSentCall = qso[5].split("/")[0]
    newRcvdCall = qso[8].split("/")[0]
    newRcvdQthList = qso[10].split("/")
    
    for item in newRcvdQthList: 
        if(chgCode == 0):
            logList.append(qso[0] + " " + bandstr + " " + qso[2] + " " + qso[3] + " " + qso[4] + " " + newSentCall + " " + qso[6] + " " + qso[7] + " " + newRcvdCall + " " + qso[9] + " " + item)
        elif(chgCode == 1):
            logList.append(qso[0] + " " + bandstr + " " + qso[2] + " " + qso[3] + " " + qso[4] + " " + newSentCall + " " + qso[6] + " " + qso[7] + "DX " + newRcvdCall + " " + qso[9] + " " + item)
        else:
            logList.append(qso[0] + " " + bandstr + " " + qso[2] + " " + qso[3] + " " + qso[4] + " " + newSentCall + " " + qso[6] + " " + qso[7] + " " + newRcvdCall + " " + qso[9] + " " + item +"DX")
 
def IsTXCounty(astr):
    return(astr in TXabbList)

def IsNonTXUSVE(astr):
    return(astr in NonTXabbList)

def IsATX_TX_Qso(qsoLine):
    qso=qsoLine.split()
    return(IsTXCounty(qso[7]) and IsTXCounty(qso[10]))

def IsATX_NTX_Qso(qsoLine):
    qso=qsoLine.split()
    fromTX = IsTXCounty(qso[7]) and IsNonTXUSVE(qso[10])
    toTX =  IsTXCounty(qso[10]) and IsNonTXUSVE(qso[7]) 
    return(fromTX or toTX)

def IsATX_DX_Qso(qsoLine):
    qso=qsoLine.split()
    fromTX = IsTXCounty(qso[7]) and IsDXCall(qso[8])
    toTX =  IsDXCall(qso[5]) and IsTXCounty(qso[10]) 
    return(fromTX or toTX)

def UpdateLocationCode(qsoLine, sentQth, aheaderLocation, ahasFix):
    qso = qsoLine.split()
    if(len(qso) < 11):
        return(aheaderLocation)
    if(IsDXCall(qso[5])):
        return(0)
    if(IsNonTXUSVE(qso[7])):
        return(1)
    if(IsTXCounty(qso[7])):
        sentQth.append(qso[7])
        unique_elements = list(set(sentQth))
        if(len(unique_elements) > 1 and not ahasFix):  #use fixed value in header as override
            return(3)        
        else:
            return(2)

def UpdateSentCounties(qsoLine, aTxCtyList):
    qso = qsoLine.split()
    if(IsTXCounty(qso[7])):
        updateCountySentQsos(aTxCtyList, qso[7].rstrip())

def UpdateRcvdCounties(qsoLine, aTxCtyList):
    qso = qsoLine.split()
    if(IsTXCounty(qso[10])):
        updateCountyRcvdQsos(aTxCtyList, qso[10].rstrip())

def GetNumberOfActiveSentCounties(aTxCtyList):
    count = 0
    for item in aTxCtyList:
        if(item.sentQsos > 0):
            count += 1
    return(count)

def GetNumberOfActiveRcvdCounties(aTxCtyList):
    count = 0
    for item in aTxCtyList:
        if(item.rcvdQsos > 0):
            count += 1
    return(count)

def IsACWQso(qsoLine):
    qso = qsoLine.split()
    if(len(qso) < 11):
        return(qsoLine + "    [ERROR: Missing qso elements]")
    return(qso[2] == "CW")    
    
def IsAPHQso(qsoLine):
    qso = qsoLine.split()
    if(len(qso) < 11):
        return(qsoLine + "    [ERROR: Missing qso elements]")
    return(qso[2] == "PH" or qso[2] == "FM" or qso[2] == "USB" or qso[2] == "LSB")

def IsADGQso(qsoLine):
    qso = qsoLine.split()
    if(len(qso) < 11):
        return(qsoLine + "    [ERROR: Missing qso elements]")
    return(qso[2] == "DG" or qso[2] == "RY")

def IsA160Qso(qsoLine):
    qso = qsoLine.split()
    if(len(qso) < 11):
        return(qsoLine + "    [ERROR: Missing qso elements]")
    return(qso[1] == "160")
    
def IsA80Qso(qsoLine):
    qso = qsoLine.split()
    if(len(qso) < 11):
        return(qsoLine + "    [ERROR: Missing qso elements]")
    return(qso[1] == "80")
    
def IsA40Qso(qsoLine):
    qso = qsoLine.split()
    if(len(qso) < 11):
        return(qsoLine + "    [ERROR: Missing qso elements]")
    return(qso[1] == "40")
    
def IsA20Qso(qsoLine):
    qso = qsoLine.split()
    if(len(qso) < 11):
        return(qsoLine + "    [ERROR: Missing qso elements]")
    return(qso[1] == "20")

def IsA15Qso(qsoLine):
    qso = qsoLine.split()
    if(len(qso) < 11):
        return(qsoLine + "    [ERROR: Missing qso elements]")
    return(qso[1] == "15")

def IsA10Qso(qsoLine):
    qso = qsoLine.split()
    if(len(qso) < 11):
        return(qsoLine + "    [ERROR: Missing qso elements]")
    return(qso[1] == "10")

def IsA6Qso(qsoLine):
    qso = qsoLine.split()
    if(len(qso) < 11):
        return(qsoLine + "    [ERROR: Missing qso elements]")
    return(qso[1] == "6")

def IsA2Qso(qsoLine):
    qso = qsoLine.split()
    if(len(qso) < 11):
        return(qsoLine + "    [ERROR: Missing qso elements]")
    return(qso[1] == "2")

def ConvertModeCountToName(aCWcount, aPHcount, aDGcount):
    if(aCWcount > 0 and aPHcount == 0 and aDGcount == 0):
        return("TQP-MODE: CWO")
    elif(aCWcount == 0 and aPHcount > 0 and aDGcount == 0):
        return("TQP-MODE: PHO")
    elif(aCWcount == 0 and aPHcount == 0 and aDGcount > 0):
        return("TQP-MODE: DGO")
    else:
        return("TQP-MODE: MIX")

def ConvertModeCountToCode(aCWcount, aPHcount, aDGcount):
    if(aCWcount > 0 and aPHcount == 0 and aDGcount == 0):
        return(0)
    elif(aCWcount == 0 and aPHcount > 0 and aDGcount == 0):
        return(1)
    elif(aCWcount == 0 and aPHcount == 0 and aDGcount > 0):
        return(2)
    else:
        return(3)

def ConvertCatCodesToTQPCatName(powercode, modecode, locationcode, numOpscode):
    if(locationcode == NTXCODE and modecode == CWOCODE):
        return("NTX SO CWO")
    if(locationcode == NTXCODE and modecode == PHOCODE):
        return("NTX SO PHO")
    if(locationcode == NTXCODE and modecode == MIXCODE):
        return("NTX SO")
    if(locationcode == NTXCODE and powercode == QRPCODE):
        return("NTX SO QRP")
    if(locationcode == DXCODE):
        return("DX SO")
    if(locationcode == TXFCODE and modecode == CWOCODE and numOpscode == SOPCODE and powercode == LOWCODE):
        return("TX CWO SO LP")
    if(locationcode == TXFCODE and modecode == CWOCODE and numOpscode == SOPCODE and powercode == HIGHCODE):
        return("TX CWO SO HP")
    if(locationcode == TXFCODE and modecode == PHOCODE and numOpscode == SOPCODE and powercode == LOWCODE):
        return("TX PHO SO LP")
    if(locationcode == TXFCODE and modecode == PHOCODE and numOpscode == SOPCODE and powercode == HIGHCODE):
        return("TX PHO SO HP")
    if(locationcode == TXFCODE and modecode == DGOCODE and numOpscode == SOPCODE and powercode == LOWCODE):
        return("TX DGO SO LP")
    if(locationcode == TXFCODE and modecode == DGOCODE and numOpscode == SOPCODE and powercode == HIGHCODE):
        return("TX DGO SO HP")
    if(locationcode == TXFCODE and modecode == MIXCODE and numOpscode == SOPCODE and powercode == LOWCODE):
        return("TX SO MIX LP")
    if(locationcode == TXFCODE and modecode == MIXCODE and numOpscode == SOPCODE and powercode == HIGHCODE):
        return("TX SO MIX HP")
    if(locationcode == TXFCODE and numOpscode == SOPCODE and powercode == QRPCODE):
        return("TX SO QRP")
    if(locationcode == TXMCODE and modecode == CWOCODE and numOpscode == SOPCODE):
        return("TXM SO CWO")
    if(locationcode == TXMCODE and modecode == PHOCODE and numOpscode == SOPCODE):
        return("TXM SO PHO")
    if(locationcode == TXMCODE and modecode == MIXCODE and numOpscode == SOPCODE):
        return("TXM SO")
    if(locationcode == TXMCODE and numOpscode == MOPCODE):
        return("TXM MO")
    if(locationcode == TXFCODE and numOpscode == MOPCODE and powercode == LOWCODE):
        return("TX MO LP")
    if(locationcode == TXFCODE and numOpscode == MOPCODE and powercode == HIGHCODE):
        return("TX MO HP")
    else:
        return("TQP-CATEGORY: UNKNOWN")

def DetectWardCounty(qsoLine):
    qso = qsoLine.split()
    call = qso[5]
    scty = qso[7]
    if scty == "WARD":
        print("WARD STATION=" + call)             
   
#-----------------------------------------------------------------------------------------
#The actual processing begins here using the above functions. 
#Each log in the PreparedLogs directory is read in and processed
#-----------------------------------------------------------------------------------------
target_directory = PreparedLogs 
all_files = get_all_files(target_directory)
print("TQP-CATEGORY,CallSign")

TotalLogs = 0
TotalDXLogs = 0
TotalNTXLogs = 0
TotalTXLogs = 0
UnCatLogs = 0

NumLogsCat_DX_SO = 0
NumLogsCat_NTX_SO = 0 
NumLogsCat_NTX_SO_CWO = 0 
NumLogsCat_NTX_SO_PHO = 0 
NumLogsCat_NTX_SO_QRP = 0
NumLogsCat_TX_CWO_SO_HP = 0 
NumLogsCat_TX_CWO_SO_LP = 0 
NumLogsCat_TX_DGO_SO_LP = 0 
NumLogsCat_TX_MO_HP = 0 
NumLogsCat_TX_MO_LP = 0 
NumLogsCat_TX_PHO_SO_HP = 0 
NumLogsCat_TX_PHO_SO_LP = 0 
NumLogsCat_TX_SO_MIX_HP = 0 
NumLogsCat_TX_SO_MIX_LP = 0 
NumLogsCat_TX_SO_QRP = 0 
NumLogsCat_TXM_SO = 0 
NumLogsCat_TXM_SO_CWO = 0 
NumLogsCat_TXM_SO_PHO = 0 
NumLogsCat_TXM_MO = 0 

TotalQsos = 0
TotalCWQsos = 0
TotalPHQsos = 0
TotalDGQsos = 0
Total160Qsos = 0
Total80Qsos = 0
Total40Qsos = 0
Total20Qsos = 0
Total15Qsos = 0
Total10Qsos = 0
Total6Qsos = 0
Total2Qsos = 0

TotalTX_TX_Qsos = 0
TotalTX_DX_Qsos = 0
TotalTX_NTX_Qsos = 0

SentCounties = []
RcvdCounties = []

HourlyQsos = []
HourlyQsos = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

BicMissedNoHr = []
BicMissedOneHr = []
BicMissedTwoHr = []
HourlyQsosThisStation = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

CallHoursWithQso = []

for f in all_files:
    file_path = f

    # Create a Path object
    path_obj = Path(file_path)

    # Get the stem (filename without extension)
    fname = path_obj.stem
    newLogName = PreparedLogs + "\\" + fname + "-Prep.log"

    catResults = []
    catResults.clear()

    with open(f, 'r', encoding='utf-8') as file:
        CallSign = ""
        TQPCat = ""
        HourlyQsosThisStation = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

        for line in file:
            # Process each line here
            # For example, strip whitespace and newline characters
            processed_line = line.strip().upper()
            items = processed_line.split()
            if(len(items) <= 0): 
                continue
            if(items[0] == "CALLSIGN:"):
                CallSign = items[1]
            if(items[0] == "TQP-CATEGORY:"):
                for i in range(1, len(items)):
                    TQPCat = TQPCat + items[i] + " "
                catitems = TQPCat.split()
                if(catitems[0] == "DX"):
                    TotalDXLogs += 1    
                elif(catitems[0] == "NTX"):
                    TotalNTXLogs += 1
                elif(catitems[0] == "TX" or catitems[0] == "TXM"):
                    TotalTXLogs += 1
                else:
                    UnCatLogs += 1 
            if(items[0] == "QSO:"):
                TotalQsos += 1
                if(IsACWQso(processed_line)):
                    TotalCWQsos += 1
                if(IsAPHQso(processed_line)):
                    TotalPHQsos += 1
                if(IsADGQso(processed_line)):
                    TotalDGQsos += 1
                if(IsA160Qso(processed_line)):
                    Total160Qsos += 1
                if(IsA80Qso(processed_line)):
                    Total80Qsos += 1
                if(IsA40Qso(processed_line)):
                    Total40Qsos += 1
                if(IsA20Qso(processed_line)):
                    Total20Qsos += 1
                if(IsA15Qso(processed_line)):
                    Total15Qsos += 1
                if(IsA10Qso(processed_line)):
                    Total10Qsos += 1
                if(IsA6Qso(processed_line)):
                    Total6Qsos += 1
                if(IsA2Qso(processed_line)):
                    Total2Qsos += 1
                if(IsATX_TX_Qso(processed_line)):
                    TotalTX_TX_Qsos += 1
                if(IsATX_NTX_Qso(processed_line)):
                    TotalTX_NTX_Qsos += 1
                if(IsATX_DX_Qso(processed_line)):
                    TotalTX_DX_Qsos += 1
                UpdateSentCounties(processed_line, TXCountiesList)
                UpdateRcvdCounties(processed_line, TXCountiesList)
                DetectWardCounty(processed_line) 
                hrIndex = IndexOfQsoHourAsInteger(processed_line)
                HourlyQsos[hrIndex] = HourlyQsos[hrIndex] + 1
                HourlyQsosThisStation[hrIndex] = HourlyQsosThisStation[hrIndex] + 1                    

        
        catResults.append(TQPCat.rstrip() + "," + CallSign)
        TotalLogs += 1
        HoursWithQsosThisStation = 0
        for item in HourlyQsosThisStation:
            if(item > 0):
                HoursWithQsosThisStation = HoursWithQsosThisStation + 1
        if(HoursWithQsosThisStation == 18):
            qsoStr = CallSign + ","
            totQso = 0
            for item in HourlyQsosThisStation:
                qsoStr = qsoStr + str(item) + ","
                totQso = totQso + item
            BicMissedNoHr.append(qsoStr + str(totQso))
        elif(HoursWithQsosThisStation == 17):
            qsoStr = CallSign + ","
            totQso = 0
            for item in HourlyQsosThisStation:
                qsoStr = qsoStr + str(item) + ","
                totQso = totQso + item 
            BicMissedOneHr.append(qsoStr + str(totQso))
        elif(HoursWithQsosThisStation == 16):
            qsoStr = CallSign + ","
            totQso = 0
            for item in HourlyQsosThisStation:
                qsoStr = qsoStr + str(item) + ","
                totQso = totQso + item 
            BicMissedTwoHr.append(qsoStr + str(totQso))
     
        file.close()
        
    for item in catResults:
        print(item)
        catitems = item.split(',')
        if(catitems[0] == "DX SO"):
            NumLogsCat_DX_SO += 1            
        elif(catitems[0] == "NTX SO"):
            NumLogsCat_NTX_SO += 1            
        elif(catitems[0] == "NTX SO CWO"):
            NumLogsCat_NTX_SO_CWO += 1            
        elif(catitems[0] == "NTX SO PHO"):
            NumLogsCat_NTX_SO_PHO += 1            
        elif(catitems[0] == "NTX SO QRP"):
            NumLogsCat_NTX_SO_QRP += 1            
        elif(catitems[0] == "TX CWO SO HP"):
            NumLogsCat_TX_CWO_SO_HP += 1            
        elif(catitems[0] == "TX CWO SO LP"):
            NumLogsCat_TX_CWO_SO_LP += 1            
        elif(catitems[0] == "TX DGO SO LP"):
            NumLogsCat_TX_DGO_SO_LP += 1            
        elif(catitems[0] == "TX MO HP"):
            NumLogsCat_TX_MO_HP += 1            
        elif(catitems[0] == "TX MO LP"):
            NumLogsCat_TX_MO_LP += 1            
        elif(catitems[0] == "TX PHO SO HP"):
            NumLogsCat_TX_PHO_SO_HP += 1            
        elif(catitems[0] == "TX PHO SO LP"):
            NumLogsCat_TX_PHO_SO_LP += 1            
        elif(catitems[0] == "TX SO MIX HP"):
            NumLogsCat_TX_SO_MIX_HP += 1            
        elif(catitems[0] == "TX SO MIX LP"):
            NumLogsCat_TX_SO_MIX_LP += 1            
        elif(catitems[0] == "TX SO QRP"):
            NumLogsCat_TX_SO_QRP += 1            
        elif(catitems[0] == "TXM SO"):
            NumLogsCat_TXM_SO += 1            
        elif(catitems[0] == "TXM SO CWO"):
            NumLogsCat_TXM_SO_CWO += 1            
        elif(catitems[0] == "TXM SO PHO"):
            NumLogsCat_TXM_SO_PHO += 1            
        elif(catitems[0] == "TXM MO"):
            NumLogsCat_TXM_MO += 1            

print(" ")
print("Logs received (Total/DX/NTX/TX)")
print("Total number of logs, " + str(TotalLogs))
print("Total number of DX logs, " + str(TotalDXLogs))
print("Total number of NTX(US/VE) logs, " + str(TotalNTXLogs))
print("Total number of TX logs, " + str(TotalTXLogs))
print("Total number of Unclassified logs, " + str(UnCatLogs))

print(" ")
print("Number of logs submitted in each TQP Category")
print("Total logs in category DX SO," + str(NumLogsCat_DX_SO))
print("Total logs in category NTX SO," + str(NumLogsCat_NTX_SO))
print("Total logs in category NTX SO CWO," + str(NumLogsCat_NTX_SO_CWO))
print("Total logs in category NTX SO PHO," + str(NumLogsCat_NTX_SO_PHO))
print("Total logs in category NTX SO QRP," + str(NumLogsCat_NTX_SO_QRP))
print("Total logs in category TX CWO SO HP," + str(NumLogsCat_TX_CWO_SO_HP))
print("Total logs in category TX CWO SO LP," + str(NumLogsCat_TX_CWO_SO_LP))
print("Total logs in category TX DGO SO LP," + str(NumLogsCat_TX_DGO_SO_LP))
print("Total logs in category TX MO HP," + str(NumLogsCat_TX_MO_HP))
print("Total logs in category TX MO LP," + str(NumLogsCat_TX_MO_LP))
print("Total logs in category TX PHO SO HP," + str(NumLogsCat_TX_PHO_SO_HP))
print("Total logs in category TX PHO SO LP," + str(NumLogsCat_TX_PHO_SO_LP))
print("Total logs in category TX SO MIX HP," + str(NumLogsCat_TX_SO_MIX_HP))
print("Total logs in category TX SO MIX LP," + str(NumLogsCat_TX_SO_MIX_LP))
print("Total logs in category TX SO QRP," + str(NumLogsCat_TX_SO_QRP))
print("Total logs in category TXM SO," + str(NumLogsCat_TXM_SO))
print("Total logs in category TXM SO CWO," + str(NumLogsCat_TXM_SO_CWO))
print("Total logs in category TXM SO PHO," + str(NumLogsCat_TXM_SO_PHO))
print("Total logs in category TXM MO," + str(NumLogsCat_TXM_MO))

print(" ")
print("QSOs by Mode")
print("Total number of Qsos, " + str(TotalQsos))
print("Total number of CW Qsos, " + str(TotalCWQsos))
print("Total number of PH Qsos, " + str(TotalPHQsos))
print("Total number of DG Qsos, " + str(TotalDGQsos))

print(" ")
print("QSOs by Band")
print("Total number of 160m Qsos, " + str(Total160Qsos))
print("Total number of 80m Qsos, " + str(Total80Qsos))
print("Total number of 40m Qsos, " + str(Total40Qsos))
print("Total number of 20m Qsos, " + str(Total20Qsos))
print("Total number of 15m Qsos, " + str(Total15Qsos))
print("Total number of 10m Qsos, " + str(Total10Qsos))
print("Total number of 6m Qsos, " + str(Total6Qsos))
print("Total number of 2m Qsos, " + str(Total2Qsos))

print(" ")
print("Total QSOs by Destination")
print("Total number of TX-to-TX Qsos, " + str(TotalTX_TX_Qsos))
print("Total number of TX-to-DX Qsos, " + str(TotalTX_DX_Qsos))
print("Total number of TX-to-US/VE Qsos, " + str(TotalTX_NTX_Qsos))

print(" ")
print(" ")
numSentCty = GetNumberOfActiveSentCounties(TXCountiesList)
print("Number of Counties with at least one sent QSO," + str(numSentCty))
numRcvdCty = GetNumberOfActiveRcvdCounties(TXCountiesList)
print("Number of Counties with at least one received QSO," + str(numRcvdCty))


for item in TXCountiesList:
    TXCounty.display(item)

print(" ")
print("Total QSOs by Hour")
index = 0
CheckTotal = 0
for item in HourlyQsos:
    print("Qsos in hour of index, " + str(index) + ",  " + str(item))
    CheckTotal = CheckTotal + item
    index = index + 1
print("Total QSOs = " + str(CheckTotal))

print(" ")
print("Butt in Chair results")
for item in BicMissedNoHr:
    print("BicMissedNoHr," + item)
print(" ")
for item in BicMissedOneHr:
    print("BicMissedOneHr," + item)
print(" ")
for item in BicMissedTwoHr:
    print("BicMissedTwoHr," + item)
   




