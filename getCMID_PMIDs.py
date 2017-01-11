# getCMID_PMIDs.py
# Author: Peter MacHarrie
# Input: file containing list of Chemical Ids (aka cmid, CID)
# Ouput: pairs of comma seperated cmid, pubMedIds
#
# Process
#  Batch 100 cmids into a single http request to obtain json document
#  Traverse json document and print out cmid,pmid pairs
 
import httplib
import time
import json


# Call the pubchem interface and request json for the pmids referenced in cid page

def getcidPubId (x):

    conn = httplib.HTTPSConnection("pubchem.ncbi.nlm.nih.gov")

    request_txt = "/rest/pug/compound/cid/" + x + "/xrefs/PubMedId/JSONP"
    #print "rq=", request_txt

    conn.request("GET", request_txt)
    r1 = conn.getresponse()

    #print r1.status, r1.reason

#
#	Check to see if valid response
#
    data1 = ""
    if r1.status == 404:
			# Some cids throw an exception, return in data1, handle downstream, need to improve
        data1="404"
    else:
			# otherwise, have a valid json object
        data1 = r1.read()

    #print "data=", data1

    return data1


# Traverse the json object and print cmid,pmid pairs

def printPubData(x):

#    print "x3", x['InformationList']['Information']
#    print "x3 type=", type(x['InformationList']['Information'])

    for i,val in enumerate(x['InformationList']['Information']):
#        print "i=", i, "v=", val

	# Extract the CID

        cid=val['CID']

			# Check to see if any PubMedID exist for the CID, if so print, else print "NULL" for pubMedId
			
        if 'PubMedID' in val:
            for y in val['PubMedID']:
              print str(cid) + "," + str(y)
        else:

					# If no PubMedID for the CID print cid,NULL

            print str(cid) + "," + "NULL"
            
# Main

# open the file containing the list of cmids

f = open('pccompound_result.txt')

# Loop through the file

ctr=1
cidList=""
pubData=""

for line in f:
	# Remove line feed
    line = line.rstrip()

    if ctr == 100:
		# Have a batch of 100 cmids, get json object
        cidList += line
        pubData=getcidPubId(cidList)
	
		# Remove extraneous data
        pubData=pubData.replace("callback(", "");
        pubData=pubData.replace(");", "");

		# Print data if got valid response from server

        if pubData <> "404":
            d=json.loads(pubData)
            printPubData(d)

        cidList=""
        ctr=1

    else:
		# Keep building a batch
        cidList += line + ","

    ctr += 1


# Process any remaining cids
# Remove trailing comma if present

pubData=getcidPubId(cidList.rstrip(","))

pubData=pubData.replace("callback(", "");
pubData=pubData.replace(");", "");
d=json.loads(pubData)
printPubData(d)

# Done
