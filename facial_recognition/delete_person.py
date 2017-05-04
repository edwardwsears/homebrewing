from optparse import OptionParser
import face_api
import sys

#parse cmdline flags
parser = OptionParser()
parser.add_option("-u","--use",action="store",type="string",dest="user",help="User Name")
(options,args) = parser.parse_args()

if not options.user:
    parser.error('Username (-u) not given')

list_persons_json = face_api.list_persons()

found = False
for person in list_persons_json:
    if (person['name'] == options.user:
        print "Deleting: "+person['name']
        face_api.delete_person(person['personId'])
        found = True

if (found == False):
    print "Unable to find user: "+options.user
