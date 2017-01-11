# getPMIDs_only.py
# Author: Peter MacHarrie (Peter.MacHarrie@noaa.gov)
# Input: file containing list of pubchem Ids (cmid)
# Output: For each pubChem document of the cmids, list of referenced pubMedIds
#
# Process:
#   pubchem TXT output url hardcoded
#   Want to go easy on the pubchem server so batch requests into groups of 100 cmids
#   print the list pubMedIds returned
#
# run the output of this program through " sort -un " to get the unique list of pubMedIds

import httplib
import time
import json

# Request PubMedId in text format for a list of comma separated cmids

def getcidPubId (x):

    conn = httplib.HTTPSConnection("pubchem.ncbi.nlm.nih.gov")
    request_txt = "/rest/pug/compound/cid/" + x + "/xrefs/PubMedId/TXT"
#    print "rq=", request_txt
    conn.request("GET", request_txt)
    r1 = conn.getresponse()
    #print r1.status, r1.reason
    data1 = r1.read()
#    print "data=", data1
    return data1


# Get the list cmids

f = open('pccompound_result.txt')

# Loop through the file

ctr=1
cidList=""
pubData=""

for line in f:

		# stripe of the linefeed
    line = line.rstrip()

    if ctr == 100:
			# Have a batch of 100
        cidList += line
        pubData=getcidPubId(cidList)
        print pubData
        cidList=""
        #time.sleep(4)
        ctr=1
    else:
			# Build a batch
        cidList += line + ","
    ctr += 1

# Do the remaining part of the list

pubData=getcidPubId(cidList.rstrip(","))
pubData=getcidPubId(cidList)
print pubData


# Done
