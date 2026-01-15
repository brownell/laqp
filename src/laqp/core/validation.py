#Use this script to validate each log in the input directory (LogsToValidate)
#If a log passes the validation process it is moved to the ValidatedLogs directory (ValidatedLogs)
#If a log does not pass the validation process it is moved to the ProblemLogs directory (ProblemLogs)
#In either case a results file is written to the ValidationResults directory (ValidationResults)
#The script does not create these directories so one of the first steps is to manually create the directories

#-----------------------------------------------------------------------------------------------
#Be sure to set the start and end times of the two sessions as UTC strings in the format YYYY-MM-DD hhmm
#starttimeday1_string, endtimeday1_string, starttimeday2_string, endtimeday2_string
#Examples for 2025 TQP are
#starttimeday1_string = "2025-09-20 1400"
#endtimeday1_string = "2025-09-21 0200"
#starttimeday2_string = "2025-09-21 1400"
#endtimeday2_string = "2025-09-21 2000"
#-----------------------------------------------------------------------------------------------

# Set the directory containing the logs to be validated
#-----------------------------------------------------------------------------------------------
LogsToValidate = 'C:\\Users\\18326\\TexasQsoParty\\TQP-2025\\LogProcessing\\LogsToValidate'
#the files in LogsToValidate are assumed to be named CallSign.LOG and are the only files in 
#that directory
#-----------------------------------------------------------------------------------------------
#
# Set the directory containing the validated logs
#-----------------------------------------------------------------------------------------------
ValidatedLogs = 'C:\\Users\\18326\\TexasQsoParty\\TQP-2025\\LogProcessing\\ValidatedLogs'
#the files in ValidatedLogs are named CallSign.LOG and are the only files in that directory
#-----------------------------------------------------------------------------------------------
#
# Set the directory containing the non-validated logs, the ProblemLogs
#-----------------------------------------------------------------------------------------------
ProblemLogs = 'C:\\Users\\18326\\TexasQsoParty\\TQP-2025\\LogProcessing\\ProblemLogs'
#the files in ProblemLogs are named CallSign.LOG and are the only files in that directory
#-----------------------------------------------------------------------------------------------
#
# Set the directory containing the error reports associated with the ProblemLogs
#-----------------------------------------------------------------------------------------------
ProblemReports = 'C:\\Users\\18326\\TexasQsoParty\\TQP-2025\\LogProcessing\\ProblemReports'
#the files in ProblemReports are named CallSign-Errors.txt and are the only files in that directory
#-----------------------------------------------------------------------------------------------
#
# Set the directory containing the validation results
#-----------------------------------------------------------------------------------------------
ValidationResults = 'C:\\Users\\18326\\TexasQsoParty\\TQP-2025\\LogProcessing\\ValidationResults'
#the files in ValidationResults are named CallSign-ValRes.txt and are the only files in that directory
#-----------------------------------------------------------------------------------------------
#

import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# Import the os module, for the os.walk function and the datetime module
import shutil
import os
from datetime import datetime
from pathlib import Path

# Define the format of the input time string
format_string = "%Y-%m-%d %H%M"
date_format = "%Y-%m-%d"
# Define the start and end times for each session
starttimeday1_string = "2025-09-20 1400"
endtimeday1_string = "2025-09-21 0200"
starttimeday2_string = "2025-09-21 1400"
endtimeday2_string = "2025-09-21 2000"

unix_timestamp_int_starttimeday1 = 0
unix_timestamp_int_endtimeday1 = 0
unix_timestamp_int_starttimeday2 = 0

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

#-------------------------------Define the set of Canadian prefixes-----------------------------
CanadianPrefixes = {"CF", "CG", "CH", "CI", "CJ", "CK", "CY", "CZ", "VA", "VB", "VC", "VD", "VE", 
"VF", "VG", "VO", "VX", "VY", "XJ", "XK", "XL", "XM", "XN", "XO"}
#-----------------------------------------------------------------------------------------------
#-------------------------------Define the set of US prefixes-----------------------------------
USPrefixes = {"K", "N", "W", "AA", "AB", "AC", "AD", "AE", "AF", "AG", "AH", "AI", "AJ", "AK", "AL"}
#-----------------------------------------------------------------------------------------------

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

 


unix_timestamp_int_endtimeday2 = 0

#define some functions for checking validity of QSO entries

def IsTXCounty(astr):
    return(astr in TXabbList)

def IsNonTXUSVE(astr):
    return(astr in NonTXabbList)

def UpdateLocationCode(qsoLine, sentQth, headerlocation) -> int:
    qso = qsoLine.split()
    if(len(qso) < 11):
        return(int(headerlocation))
    if(IsDXCall(qso[5])):
        return(int(0))
    if(IsNonTXUSVE(qso[7])):
        return(int(1))
    if(IsTXCounty(qso[7])):
        sentQth.append(qso[7])
        unique_elements = list(set(sentQth))
        if(len(unique_elements) > 1):
            return(int(3))        
        else:
            return(int(2))
    else:
        return(0)


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
    isAllDigits = aQth.isdigit()
    return(lenLessThanFive and notTexas and not isAllDigits) 

def HasSlashInRcvdQth(aQth):
    character_to_find = "/"
    hasASlash = character_to_find in aQth
    return(hasASlash) 


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

def IsA70CMKHz(aFreqKHz):
    return(420000 <= aFreqKHz and aFreqKHz <= 450000)

def IsValidTQPKHz(aKHz):
    isLowHF = IsA160KHz(aKHz) or IsA80KHz(aKHz) or IsA40KHz(aKHz) 
    isHighHF = IsA20KHz(aKHz) or IsA15KHz(aKHz) or IsA10KHz(aKHz)
    isVUF = IsA6KHz(aKHz) or IsA2KHz(aKHz) or IsA125KHz(aKHz) or IsA70CMKHz(aKHz)
    return(isLowHF or isHighHF or isVUF)

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
    if(len(substrings) == 11 or len(substrings) == 12):
        errCode = 9
    else:
    	return(-1)
    errCode = 9;
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
    rcvdQthHasSlash = HasSlashInRcvdQth(substrings[10])
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
    if rcvdQthHasSlash:
        errCode = 8
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
        #print(f"File '{source_file}' \nsuccessfully moved to '{destination_file}'") 

    except FileNotFoundError:
        print(f"Error: Source file '{source_file}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

def AddCabrilloNoteToList(aList):
    
    aList.append(".")
    aList.append(".")
    aList.append(".")
    aList.append("-----------------------------------------------------------")             
    aList.append("Note on QSO lines")
    aList.append("-----------------------------------------------------------")             
    aList.append("Every QSO line must contain the following elements separated by spaces and in the order shown.")
    aList.append("The number of spaces is not critical as long as there is at least one between the elements.")
    aList.append(" ")
    aList.append("QSO: Freq Mode Date Time SentCall SentRST SentQTH RcvdCall RcvdRST RcvdQTH")
    aList.append(" ")
    aList.append("where")
    aList.append("Freq is the frequency in KiloHertz")
    aList.append("Mode is a two-letter representation of the mode (CW, PH, DG, RY)")
    aList.append("Date is the date of the QSO in the format YYYY-MM-DD (e.g. 2025-09-21)")
    aList.append("Time is the time of the QSO in UTC in the format HHMM")
    aList.append("SentCall is your call used in the QSO party")
    aList.append("SentRST is the signal report you sent (ignored in log processing but must be present)")
    aList.append("SentQTH is the QTH indicator you sent (standard abbreviation for county/state/province/country)")
    aList.append("RcvdCall is the call of the other station")
    aList.append("RcvdRST is the signal report you received (ignored in log processing but must be present)")
    aList.append("RcvdQTH is the QTH indicator you received (standard abbreviation for county/state/province/country)")

def AddBadFreqNoteToList(aList):
    
    aList.append(".")
    aList.append(".")
    aList.append(".")
    aList.append("-----------------------------------------------------------")             
    aList.append("Note on QSO lines with Bad Frequency")
    aList.append("-----------------------------------------------------------")             
    aList.append("Most common cause of this error is logging 2m contact frequency as 144 rather than 144000.")
 
def AddBadDateTimeNoteToList(aList):
    
    aList.append(".")
    aList.append(".")
    aList.append(".")
    aList.append("-----------------------------------------------------------")             
    aList.append("Note on QSO lines with Bad Date Time")
    aList.append("-----------------------------------------------------------")             
    aList.append("Most common cause of this error is logging QSOs outside the time periods of the QSO Party.")
 

#-----------------------------------------------------------------------------------------
#The actual processing begins here. Each log in the LogsToValidate directory is read in and processed
#Then the log is moved to either the ValidatedLogs directory or the ProblemLogs directory
#-----------------------------------------------------------------------------------------

target_directory = LogsToValidate 
all_files = get_all_files(target_directory)

for f in all_files:
    file_path = f

    # Create a Path object
    path_obj = Path(file_path)

    # Get the stem (filename without extension)
    fname = path_obj.stem
    reportName = ProblemReports + "\\" + fname + "-Errors.txt"

    with open(f, 'r', encoding='utf-8') as file:
        lines = []
        qsoLines = 0        
        locationcode = int(0)       #0 => DX, 1=>NTX, 2=>TX(Fixed), 3=>TX(Mobile)
        headerlocation = 0
        badQsoLines = 0
        hasValidPowerCat = False
        hasValidOperatorCat = False
        hasValidOperatorList = False
        hasValidStationCat = False
        isAMultiOp = False
        hasInvalidQsoLines = False
        valResults = []
        stnResults = []
        stnResults.clear()
        sentQth = []
        sentQth.clear()
        for line in file:
            # Process each line here
            # For example, strip whitespace and newline characters
            processed_line = line.strip().upper()
            items = processed_line.split()
            if(len(items) <= 0): 
                continue
            if(items[0] == "CATEGORY-POWER:"):
                if(len(items) == 1):
                    hasValidPowerCat = False
                elif(items[1] == "QRP" or items[1] == "LOW" or items[1] == "HIGH"):
                    hasValidPowerCat = True
            elif(items[0] == "CATEGORY-OPERATOR:"):
                if(len(items) == 1):
                    hasValidOperatorCat = False
                elif(items[1] == "SINGLE-OP" or items[1] == "MULTI-OP" or items[1] == "CHECKLOG"):
                    hasValidOperatorCat = True
                    if(items[1] == "MULTI-OP"):
                        isAMultiOp = True
            elif(items[0] == "EMAIL:"):
                valResults.append(line)
                stnResults.append(line)
            elif(items[0] == "OPERATORS:"):
                if(len(items) > 2):
                    hasValidOperatorList = True
            elif(items[0] == "CATEGORY-STATION:"):
                if(len(items) == 1):
                    hasValidStationCat = False
                elif(items[1] == "FIXED"):
                    hasValidStationCat = True
                    headerlocation = 2 
                elif(items[1] == "MOBILE"):
                    hasValidStationCat = True
                    headerlocation = 3
                elif(items[1] == "PORTABLE"):
                    hasValidStationCat = True
                    headerlocation = 2
                elif(items[1] == "ROVER"):
                    hasValidStationCat = True
                    headerlocation = 3
            elif(items[0] == "QSO:"):
                qsoLines = qsoLines + 1
                locationcode = UpdateLocationCode(processed_line, sentQth, headerlocation)
                errCode = IsAValidQsoLine(processed_line)
                if(errCode > 0 and errCode < 9 or errCode == -1):
                     badQsoLines = badQsoLines + 1
                     if(errCode == -1):
                         errMsg = ' [Error:missing or excess data in QSO line]'
                     if(errCode == 1):
                         errMsg = ' [Error:bad frequency]'
                     if(errCode == 2):
                         errMsg = ' [Error:bad mode]'
                     if(errCode == 3):
                         errMsg = ' [Error:bad date-time]'
                     if(errCode == 4):
                         errMsg = ' [Error:bad sent call]'
                     if(errCode == 5):
                         errMsg = ' [Error:bad sent Qth]'
                     if(errCode == 6):
                         errMsg = ' [Error:bad rcvd call]'
                     if(errCode == 7):
                         errMsg = ' [Error:bad rcvd Qth]'
                     if(errCode == 8):
                         errMsg = ' [Error:bad rcvd Qth. County line QSOs will fix in preparation stage]'
                     valResults.append(processed_line + " " + errMsg)
                     stnResults.append(processed_line + " " + errMsg)
            else:
                continue

        #PowerCat, OperatorCat, StationCat are only important for Texas stations so override calc values with True for non-Texas logs
        if(locationcode < 2):     
            hasValidPowerCat = True
            hasValidOperatorCat = True
            hasValidStationCat = True 
        file.close()
        if(hasValidPowerCat):
            valResults.append(fname + ": CATEGORY-POWER is valid")
            stnResults.append(fname + ": CATEGORY-POWER is valid")
        else:
            valResults.append(fname + ": CATEGORY-POWER is invalid or missing. Should be one of QRP LOW HIGH")             
            stnResults.append(fname + ": CATEGORY-POWER is invalid or missing. Should be one of QRP LOW HIGH")             
        if(hasValidOperatorCat):
            valResults.append(fname + ": CATEGORY-OPERATOR is valid")
            stnResults.append(fname + ": CATEGORY-OPERATOR is valid")
        else:
            valResults.append(fname + ": CATEGORY-OPERATOR is invalid or missing. Should be one of S‌INGLE-OP or MULTI-OP or CHECKLOG")             
            stnResults.append(fname + ": CATEGORY-OPERATOR is invalid or missing. Should be one of S‌INGLE-OP or MULTI-OP or CHECKLOG")             
        if(hasValidStationCat):
            valResults.append(fname + ": CATEGORY-STATION is valid")
            stnResults.append(fname + ": CATEGORY-STATION is valid")
        else:
            valResults.append(fname + ": CATEGORY-STATION is invalid or missing. Should be one of FIXED  or MOBILE or PORTABLE or ROVER")
            stnResults.append(fname + ": CATEGORY-STATION is invalid or missing. Should be one of FIXED  or MOBILE or PORTABLE or ROVER")
        valResults.append(fname + ": Log contains " + str(qsoLines) + " qsoLines")             
        valResults.append(fname + ": Log contains " + str(badQsoLines) + " invalid qsoLines")
        stnResults.append(fname + ": Log contains " + str(qsoLines) + " qsoLines")             
        stnResults.append(fname + ": Log contains " + str(badQsoLines) + " invalid qsoLines")
        hasInvalidQsoLines = badQsoLines > 0
        if(isAMultiOp):
            if(not hasValidOperatorList):
                valResults.append(fname + ": MULTI-OP OPERATOR LIST is missing or invalid")
                stnResults.append(fname + ": MULTI-OP OPERATOR LIST is missing or invalid")
            isAValidLog = hasValidPowerCat and hasValidOperatorCat and hasValidOperatorList and hasValidStationCat and not hasInvalidQsoLines
        else:
            isAValidLog = hasValidPowerCat and hasValidOperatorCat and hasValidStationCat and not hasInvalidQsoLines              

        if(isAValidLog):
            valResults.append(fname + ": log is VALID")
            valResults.append("Log moved to Destination dir=" + ValidatedLogs)
            valResults.append("Log source file=" + file_path)
            MoveFileToNewDestination(ValidatedLogs, file_path)            
        else:
            valResults.append(fname + ": log is INVALID due to the above errors")
            valResults.append(fname + ": log is INVALID due to the above errors")
            valResults.append("Log moved to Destination dir=" + ProblemLogs)
            valResults.append("Log source file=" + file_path)
            valResults.append("ProblemReport is at: " + reportName)
            MoveFileToNewDestination(ProblemLogs, file_path)            
            stnfile_path = reportName
            if(hasInvalidQsoLines):
                AddCabrilloNoteToList(stnResults)
                AddBadFreqNoteToList(stnResults)
                AddBadDateTimeNoteToList(stnResults)
            with open(stnfile_path, 'w', encoding='utf8') as file:
                for item in stnResults:
                    file.write(f"{item}\n")

        valResults.append("-----------------------------------------------------------")             
        if(not isAValidLog):
            for item in valResults:
                print(item) 


