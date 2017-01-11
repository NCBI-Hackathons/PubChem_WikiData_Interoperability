# mapPubChem2Wiki.py
# Author: Peter MacHarrie (Peter.MacHarrie@noaa.gov)
# Date:   Jan. 10, 2017
# Inputs
#		PubChem attribute to wikidata attribute map  (file: ./pc-wikidata-property-mapping.txt)
#		PubChem cmid List (stdin)
#	Outputs
#   Wikidata formatted tsv output (stdout)
#
#	

import httplib
import time
import json
import sys

#
# PubTerm to Wiki Id Map
#
# Example:
# pub2Wiki_dict['pKa']=P117
#
# To be filled in by file below

pub2Wiki_dict = {}



#
# Request PubChemDoc Section for CID and Term
#

def getPubChemDoc (x, y):

# Input x - CID
#				y - term
# Output - data1 (json in text, or "404" if invalid URL)


    conn = httplib.HTTPSConnection("pubchem.ncbi.nlm.nih.gov")

#
# ExampleURL: /rest/pug_view/data/compound/1140/JSON/?response_type=display&heading=Boiling%20Point
#                                           x                                             y

    request_txt = "/rest/pug_view/data/compound/" + x + "/JSON/?response_type=display&heading="+y
#    print "rt=", request_txt

    conn.request("GET", request_txt)
    r1 = conn.getresponse()

    data1 = ""
    if r1.status == 404:
                        # Some cids throw an exception, return in data, improve handling later
        data1="404"
    else:
                        # otherwise, have a valid json object return
        data1 = r1.read()

#    print "data=", data1

    return data1

#
# print the information content of the term 
#

def printTerm(d, term):
#
#	Input d - json structure:
#       term - the term being extracted
# Output 
#       print term in wikidata format
#
#	Recurse the json object

	for key, item in d.items():

#		print "key=", key, "type=", type(item), "item=", item

		if type(item) is dict:
			# Keep Traversing if item is a dicitionary
			printTerm(item, term)

		else: 

			if type(item) is list:

				if key == 'Information': # This is what we've been looking for
					# Found the information section for the term 

					# Print out the needed data, proof of concept, some term have more attributes that StringValue or NumValue, need to complete
					for i, val in enumerate(item):
						#print "i=", i, "val=", val

						outString="LAST\t" + pub2Wiki_dict[term] + "\t"
						if 'StringValue' in val:
							outString += '"' + val['StringValue'] + '"'
						if 'NumValue' in val:
							outString += '"' + str(val['NumValue']) + '"'
						print outString
	
				for i, val in enumerate(item):

					# For this json, Dictionary are wrapped inside list so if the list contains a dictionary
					# Keep Traversing
					# Otherwise done.
#					print "i=", i, "val=", val, "type=", type(val)

					if type(val) is dict:
						# Remember, dictionaries wrapped in list so keep going
						printTerm(val, term)
#			else:
#					print "key=", key, "item=", item

#
# Main
#




#
# Get mapping data, populate pub2Wiki_dict
#

f = open('pc-wikidata-property-mapping.txt')

for line in f:
	# stripe of the linefeed
	line = line.rstrip()
	[pub,wiki] = line.split('\t')
	pub=pub.replace(' ', '%20')
#	print pub, wiki
	pub2Wiki_dict[pub]=wiki

f.close()

#
# Process cids
#

#cid_list = [702, 2244, 5793, 122172997]

for cid in sys.stdin:

	cid=cid.rstrip()

#
# print the wikidata header info for each cid
#
	print "CREATE"
	print "LAST\tP31\t\"Q11173\""
	print 'LAST\tP662\t"' + str(cid) + '"'

#
# for each term passed in get the json, parse and print
#
	for key, value in sorted(pub2Wiki_dict.iteritems()):

	# get json	
		pubData=getPubChemDoc(str(cid), key)
		#print pubData
		#print "**********", key, "**********"
		if pubData <> "404":
			# get json successful
			# parse
			d=json.loads(pubData)
			# print
			printTerm(d, key)

# Done
