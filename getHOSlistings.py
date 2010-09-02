#!/usr/bin/python

import urllib2
from BeautifulSoup import BeautifulSoup
import time
import re
import sys
import os


email_file = open("hos_email.txt", "w")
programNum = 0
foundPID = False

for line in sys.stdin:
    email_file.write(line)
    #print line
    findProgram = re.search(r'^Subject: \[Hearts of Space Playlist\] PGM (\d{3}).*', line)
    if findProgram is not None:
        foundPID = True
        email_file.write("""
****FOUND PROGRAM ID %s IN SUBJECT LINE****

""" % findProgram.group(1))
        programNum = int(findProgram.group(1))

if not foundPID:
    email_file.close()
    sys.exit()
    
#email_file.close()

#print sys.stdin.read()

#today = time.strptime("19 Jul 2010", "%d %b %Y")
today = time.localtime()
page = urllib2.urlopen("http://www.hos.com/php/printProgram2.php?program=%04d" % programNum)
email_file.write("%s %s %s" % (page.url, page.code, page.msg))
page = re.sub(r'&nbsp;', ' ', page.read())
soup = BeautifulSoup(page)
#print soup.prettify()
songlist = []

targetdatesec = time.mktime(today) - (60 * 60 * 24 * (today.tm_wday - 6))
targetdate = time.localtime(targetdatesec)

#print time.asctime(targetdate)

#print "<tracks>"
#for song in soup('table', width="100%"):
for interestingThing in soup.findAll("p"):
    if interestingThing.i is not None:
        #print interestingThing.__str__
	items = re.split(r'<br />', str(interestingThing))
	artist = items[0].strip()
	artist = artist[3:]
	artist = artist.title()
	artist = re.sub('&(?!([a-zA-Z0-9]+|#[0-9]+|#x[0-9a-fA-F]+);)', '&amp;', artist)
	#print artist.title()

	title, trackduration = items[1].split(r'</i>')
	title = title[4:]
	title = title.strip()
	title = re.sub('&(?!([a-zA-Z0-9]+|#[0-9]+|#x[0-9a-fA-F]+);)', '&amp;', title)

	#print title.strip()
	#print trackduration.strip()
	trackMO = re.search(r'< (\d+):(\d+)->(\d+):(\d+)>', trackduration)
	#print "Starts at 21:%s:%s, Ends at 21:%s:%s" % trackMO.groups()
	starttime = time.strptime("%s 21:%s:%s" % (time.strftime("%m/%d/%Y", targetdate),
				     trackMO.group(1), trackMO.group(2)),
				    "%m/%d/%Y %H:%M:%S")
	endtime =  time.strptime("%s 21:%s:%s" % (time.strftime("%m/%d/%Y", targetdate),
				     trackMO.group(3), trackMO.group(4)),
				    "%m/%d/%Y %H:%M:%S")
	#print time.asctime(starttime)
	#print time.asctime(endtime)
	length = time.mktime(endtime) - time.mktime(starttime)
	#print length

	#print items[2]
	albumMO = re.search(r'.*<a href.*>(.*)</a>.*', items[2])
	if albumMO is not None:
	    album, = albumMO.groups()
	else:
	    album = items[2].split(';')
	    album = album[0]
	    album = album[3:]
	    album = album.strip()

	album = album.title()
	album = re.sub('&(?!([a-zA-Z0-9]+|#[0-9]+|#x[0-9a-fA-F]+);)', '&amp;', album)
	#print album

	songlist.append([starttime, title, artist, album, length])

track = songlist[0][0]
trackfilename = "/var/netplaylists/hos/hos_%s-%s-%s_%s.xml" % (track.tm_mon, track.tm_mday, 
    track.tm_year, track.tm_hour)
#os.mknod(trackfilename, 0666)
f = open(trackfilename, 'w')
f.write("<tracks>\n")
#print "<tracks>"
for songfields in songlist:
    trackstring = "<track>\n"
    trackstring = trackstring + "<track_start_time>" + time.strftime("%B %d, %Y %H:%M:%S", songfields[0]) + "</track_start_time>\n"
    trackstring = trackstring + "<track_title>" + songfields[1] + "</track_title>\n"
    trackstring = trackstring + "<artist>" + songfields[2] + "</artist>\n"
    trackstring = trackstring + "<album>" + songfields[3] + "</album>\n"
    trackstring = trackstring + "<track_length>" + "%d" % (songfields[4] * 1000) + "</track_length>\n"
    trackstring = trackstring + "</track>\n"
    #print trackstring
    f.write( trackstring )
f.write("</tracks>\n")
#print "</tracks>"
f.close()
os.chmod(trackfilename, 0666)
#os.chown(trackfilename, 33 , 33)

