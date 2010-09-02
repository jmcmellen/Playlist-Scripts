#!/usr/bin/python
import urllib2
from BeautifulSoup import BeautifulSoup
import time
import subprocess, sys

p = subprocess.Popen("rm c24*", shell=True)
p.wait()

#sys.exit(0)

today = time.localtime()
#year, month, day = today.timetuple()
page = urllib2.urlopen("http://classical24.publicradio.org/listings/listings.php?display=true&source=C24&month=%s&day=%s&year=%s" % (today.tm_mon, today.tm_mday, today.tm_year))
print page.geturl()
soup = BeautifulSoup(page)
songlist = []
lasthour_was = 0
laststarttime_was = None

#print "<tracks>"
for song in soup('table', width="100%"):
    #starttime = datetime.strptime("{0}/{1}/{2} {3} -0500".format(today.month, today.day, today.year, 
    #	song.tr.td.string.strip()), 
    #	"%m/%d/%Y %I:%M%p %z")
    starttime = time.strptime("%s/%s/%s %s" % (today.tm_mon, today.tm_mday, today.tm_year, 
	song.tr.td.string.strip()), "%m/%d/%Y %I:%M%p")
    starttime = time.mktime(starttime) - ( 0 * 60 * 60 )
    starttime = time.localtime(starttime)
    #starttime = "{0}/{1}/{2} {3}".format(today.month, today.day, today.year, 
	#song.tr.td.string.strip())
    songcomposer, songtitle = song.tr.td.findNextSibling('td').b.string.split(" - ", 1)
    if getattr(song.tr.td.findNextSibling('td'), "i"):
	songartist = song.tr.td.findNextSibling('td').i.string.strip()
    else:
	songartist = ""
    if starttime.tm_min != -1: #You can change this to '1' to leave out the song during the newscast
        songlist.append([starttime, songtitle.strip(), songcomposer.strip(), songartist, 0])
    else:
        if len(songlist) > 1:
            starttime = songlist[len(songlist) - 1][0]
    #print starttime.tm_hour

    if len(songlist) > 1:
	lastsongtime = songlist[len(songlist) - 2][0]
	if lastsongtime.tm_hour != starttime.tm_hour:
	    #print "New hour"
	    starttime = time.strptime("%s/%s/%s %s:%s" % (lastsongtime.tm_mon, lastsongtime.tm_mday, 
		lastsongtime.tm_year, lastsongtime.tm_hour, 59), "%m/%d/%Y %H:%M")
	    #print starttime

	songlist[len(songlist) - 2][4] = (time.mktime(starttime) - time.mktime(lastsongtime))

#print len(songlist)
lastsongtime = songlist[len(songlist) - 1][0]
starttime = time.strptime("%s/%s/%s %s:%s" % (lastsongtime.tm_mon, lastsongtime.tm_mday, 
	    lastsongtime.tm_year, lastsongtime.tm_hour, 59), "%m/%d/%Y %H:%M")
songlist[len(songlist) - 1][4] = (time.mktime(starttime) - time.mktime(lastsongtime))
track = songlist[0][0]
f = open("c24_%s-%s-%s_%s.xml" % (track.tm_mon, track.tm_mday, 
    track.tm_year, track.tm_hour), 'w')
f.write("<tracks>")
#print "<tracks>"
lasthour = track.tm_hour
for songfields in songlist:
    if songfields[0].tm_hour != lasthour:
	f.write("</tracks>")
	#print "</tracks>"
	f.close()
	#print songfields[0].tm_hour
	f = open("c24_%s-%s-%s_%s.xml" % (songfields[0].tm_mon, songfields[0].tm_mday, 
	    songfields[0].tm_year, songfields[0].tm_hour), 'w')
	f.write("<tracks>")
	#print "<tracks>"
    trackstring = "<track>"
    trackstring = trackstring + "<track_start_time>" + time.strftime("%B %d, %Y %H:%M:%S", songfields[0]) + "</track_start_time>"
    trackstring = trackstring + "<track_title>" + songfields[1] + "</track_title>"
    trackstring = trackstring + "<artist>" + songfields[2] + "</artist>"
    trackstring = trackstring + "<album>" + songfields[3] + "</album>"
    trackstring = trackstring + "<track_length>" + "%d" % (songfields[4] * 1000) + "</track_length>"
    trackstring = trackstring + "</track>"
    #print trackstring
    f.write( trackstring )
    lasthour = songfields[0].tm_hour
f.write("</tracks>")
#print "</tracks>"
f.close()

