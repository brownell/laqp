#Use this script to prepare each validated log in the input directory (ValidatedLogs)
#Validated logs that have completed the preparation process are saved to the PreparedLogs directory (PreparedLogs)
#The script does not create these directories so one of the first steps is to manually create the PreparedLogs directory
#The preparation process involves the following
#    1. Determine the TQP category and add a tag to the log as TQP-CATEGORY: <category determined from Cabrillo tags in log>
#    2. On each QSO line convert the frequency in KHz to a Band numerical indicator (160, 80, 40, etc)
#    3. On each QSO line remove any / characters from rcvd or sent callsigns where characters are /M and /CntyAbbrev
#    4. On each QSO line convert any ambiguous DX QTH indicators (OH, PA, TN, ON, etc to OHDX, PADX, TNDX, ONDX, etc)
#    5. On each QSO line where multiple counties are logged as RcvdQTH convert line to multiple single RcvdQTH lines

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

# import a list of Non-Texas (US/VE) QTH abbreviations (used to detect that station is non-TX US/VE
#-----------------------------------------------------------------------------------------------
NonTXabbsFile = 'C:\\Users\\18326\\TexasQsoParty\\Data\\WVE_Abbrevs.txt'
#-----------------------------------------------------------------------------------------------

NonTXabbList = []
with open(NonTXabbsFile, 'r') as f:
    NonTXabbrevsList = f.readlines()
for abb in NonTXabbrevsList:
    NonTXabbList.append(abb.rstrip())
 


# Set the source directory containing the validated logs to be prepared
#-----------------------------------------------------------------------------------------------
ValidatedLogs = 'C:\\Users\\18326\\TexasQsoParty\\TQP-2025\\LogProcessing\\ValidatedLogs'
#the files in ValidatedLogs are named CallSign.LOG and are the only files in that directory
#-----------------------------------------------------------------------------------------------
# Set the destination directory that will contain the prepared logs
#-----------------------------------------------------------------------------------------------
PreparedLogs = 'C:\\Users\\18326\\TexasQsoParty\\TQP-2025\\LogProcessing\\PreparedLogs'
#the files in PreparedLogs are named CallSign.LOG and are the only files in that directory
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
from datetime import datetime
from pathlib import Path
#-----------------------------------------------------------------------------------------------
#---------------------------------Define the date time format-----------------------------------
# Define the format of the input time string
format_string = "%Y-%m-%d %H%M"
date_format = "%Y-%m-%d"

#-----------------------------------------------------------------------------------------------
#-----------------------Define the start and end times of the TQP sessions for this year--------
starttimeday1_string = "2024-09-21 1400"
endtimeday1_string = "2024-09-22 0200"
starttimeday2_string = "2024-09-22 1400"
endtimeday2_string = "2024-09-22 2000"
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
        dateTimeOk = IsValidTQPDateTime(substrings[3], substrings[4], unix_timestamp_int_starttimeday1, unix_timestamp_int_endtimeday1,                            unix_timestamp_int_starttimeday2, unix_timestamp_int_endtimeday2)
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

def IsACWQso(qsoLine):
    qso = qsoLine.split()
    if(len(qso) < 11):
        return(qsoLine + "    [ERROR: Missing qso elements]")
    return(qso[2] == "CW")    
    
def IsAPHQso(qsoLine):
    qso = qsoLine.split()
    if(len(qso) < 11):
        return(qsoLine + "    [ERROR: Missing qso elements]")
    return(qso[2] == "PH" or qso[2] == "FM")

def IsADGQso(qsoLine):
    qso = qsoLine.split()
    if(len(qso) < 11):
        return(qsoLine + "    [ERROR: Missing qso elements]")
    return(qso[2] == "DG" or qso[2] == "RY")
    

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
    if(locationcode == NTXCODE and modecode == MIXCODE and not powercode == QRPCODE):
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
            
   
#-----------------------------------------------------------------------------------------
#The actual processing begins here using the above functions. 
#Each log in the ValidatedLogs directory is read in and processed
#Then the log is copied to the PreparedLogs directory
#-----------------------------------------------------------------------------------------

target_directory = ValidatedLogs 
all_files = get_all_files(target_directory)

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
        lines = []
        qsoLines = 0
        changeQsoLines = 0
        hasQsoLinesToChange = False
        locationcode = 0       #0 => DX, 1=>NTX, 2=>TX(Fixed), 3=>TX(Mobile)
        headerlocation = 0     #assume DX
        powercode = 1          #assume LOW as default
        modecode = 3           #assume mixed as default
        numOpsCode = 0         #assume single op as default
        hasFixed = False
        sentQth = []
        sentQth.clear()
        CWQCount = 0
        PHQCount = 0
        DGQCount = 0
        valResults = []
        CallSign = ""
        for line in file:
            # Process each line here
            # For example, strip whitespace and newline characters
            processed_line = line.strip().upper()
            items = processed_line.split()
            if(len(items) <= 0): 
                continue
            if(items[0] != "QSO:"):
                valResults.append(processed_line)
                if(items[0] == "CALLSIGN:"):
                    CallSign = items[1]
                if(items[0] == "CATEGORY-POWER:"):
                    if(items[1] == "QRP"):
                        powercode = 0
                    elif(items[1] == "LOW"):
                        powercode = 1
                    else:
                        powercode = 2
                if(items[0] == "CATEGORY-OPERATOR:"):
                    if(items[1] == "SINGLE-OP"):
                        numOpscode = 0
                    elif(items[1] == "MULTI-OP"):
                        numOpscode = 1
                    else:
                        numOpscode = 0
                if(items[0] == "CATEGORY-STATION:"):
                    if(len(items) < 2):
                        headerlocation = 2 
                    else:
                        if(items[1] == "FIXED"):
                            headerlocation = 2
                            hasFixed = True
                        elif(items[1] == "MOBILE"):
                            headerlocation = 3
                        else:
                            headerlocation = 0


            else:
                qsoLines = qsoLines + 1
                changeCode = IsALogQsoLineToChange(processed_line)
                locationcode = UpdateLocationCode(processed_line, sentQth, headerlocation, hasFixed)
                if(IsACWQso(processed_line)):
                    CWQCount = CWQCount + 1 
                if(IsAPHQso(processed_line)):
                    PHQCount = PHQCount + 1
                if(IsADGQso(processed_line)):
                    DGQCount = DGQCount + 1

                reformLine = ReformatQsoLine(processed_line, valResults, changeCode)
                #valResults.append(reformLine)
        modecode = ConvertModeCountToCode(CWQCount, PHQCount, DGQCount)        
        tqpCat = ConvertCatCodesToTQPCatName(powercode, modecode, locationcode, numOpscode)
        valResults.insert(1, "TQP-CATEGORY: " + tqpCat)
        dataStr = CallSign + "," + str(powercode) + "," + str(modecode) + "," + str(locationcode) + "," + str(numOpscode)
        catResults.append("TQP-CATEGORY, " + tqpCat + "," + dataStr)
        with open(newLogName, 'w', encoding='utf8') as file:
            for item in valResults:
                file.write(f"{item}\n")
 
        file.close()
        
    for item in catResults:
        print(item)

