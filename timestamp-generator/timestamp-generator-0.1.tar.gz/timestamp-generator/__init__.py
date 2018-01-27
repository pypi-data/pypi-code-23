
#Requirerments:
#TinyTag library, install using the command: "pip install tinytag"
#mutagen python library
#install using: pip install mutagen

from tinytag import TinyTag
#from mutagen.mp3 import MP3
import os
import sys
import datetime

def printtime(rawtotal):

    start_min = int(rawtotal // 60)                           #calculate starting_min
    start_sec =  int(((rawtotal / 60) - start_min) * 60)      #calculate starting_sec
    if(start_min < 10):
        sys.stdout.write("0")                                   #if starting min is one digit, print additional 0 before to lined up times neatly
    sys.stdout.write(str(start_min))
    sys.stdout.write(':')
    if(start_sec < 10):
        sys.stdout.write("0")                                  #if starting sec is one digit, print additional 0 before to lined up times neatly
    sys.stdout.write(str(start_sec))

print('\nWhat is the audio filetype?')
print('1) mp3  ')
print('2) flac  ')
print('3) wav  ')
print('4) oog  ')
print('5) wma  ')
type = input('')

                                                                               #get album folder location
print('\nWhat is the name of the folder?')
foldername = input('')       #gets user input
print(" ")
#optional override:
#foldername = 'nameofmyalbumfolder/music/thisone'


#let user choose from availiable formats: mp3, flac, wav

arr = os.listdir(foldername)
count = 0
songcount = 0
songlist=[]
#build list of song filenames ending in .mp3
maxlen = 0;

for x in arr:
    if type == "1":
        if arr[count][-4:] == '.mp3':         #if filename ends in ".mp3"
            if len(arr[count]) > maxlen:
                maxlen = len(arr[count])      #set maxlength to longest filename
            songlist.append(arr[count])       #add filename to songlist
            songcount= songcount+1            #increment songcount

    elif type == "2":
        if arr[count][-5:] == '.flac':         #if filename ends in ".mp3"
            if len(arr[count]) > maxlen:
                maxlen = len(arr[count])      #set maxlength to longest filename
            songlist.append(arr[count])       #add filename to songlist
            songcount= songcount+1            #increment songcount
    elif type == "3":
        if arr[count][-4:] == '.wav':         #if filename ends in ".mp3"
            if len(arr[count]) > maxlen:
                maxlen = len(arr[count])      #set maxlength to longest filename
            songlist.append(arr[count])       #add filename to songlist
            songcount= songcount+1            #increment songcount
    elif type == "4":
        if arr[count][-4:] == '.oog':         #if filename ends in ".mp3"
            if len(arr[count]) > maxlen:
                maxlen = len(arr[count])      #set maxlength to longest filename
            songlist.append(arr[count])       #add filename to songlist
            songcount= songcount+1            #increment songcount
    elif type == "5":
        if arr[count][-4:] == '.wma':         #if filename ends in ".mp3"
            if len(arr[count]) > maxlen:
                maxlen = len(arr[count])      #set maxlength to longest filename
            songlist.append(arr[count])       #add filename to songlist
            songcount= songcount+1            #increment songcount

    count=count+1


#Go through songlist and calculate / display times:
total_min = 0;
total_sec = 0;
rawtotal = 0;
count = 0
rawtotal_start = 0;
for z in songlist:                          #songlist[count] =  filename of current song in the list 'songlist'
    f = foldername + "/" + songlist[count]
#    audio = MP3(f)

    tag = TinyTag.get(f)
    rawlength = tag.duration

#    rawlength = audio.info.length           #rawlength of .mp3 file in seconds
    rawtotal = rawlength + rawtotal         #rawtotal = running total of all songs in songlist[]

    name =  songlist[count]                             #get song filename to print
    currentlen = len(name)                              #find currentlen of the song
    sys.stdout.write(name[:-4])
    sys.stdout.write(" ")                               ## print the name and " "

    while currentlen < maxlen:                          #while the current song's filename is shorter than maxlen:
        sys.stdout.write(' ')                           #print an additonal space so times are all lined up neatly when displayed
        currentlen=currentlen+1

    if count == 0:
#        sys.stdout.write("[RT_S]")                                   #if it is the first song:
        sys.stdout.write("00:00")                       # print start time as "00:00"
        rawtotal_start = rawtotal_start + rawlength      #update rawtotal start
    else:
#        sys.stdout.write("[RT_S]")
        printtime(rawtotal_start)                                             #else if it is NOT the first song:
#        sys.stdout.write(str(rawtotal_start))
        rawtotal_start = rawtotal_start + rawlength                           #update rawtotal start

    sys.stdout.write(" - ")
#    sys.stdout.write("[RT]")
    printtime(rawtotal)
#    sys.stdout.write(str(rawtotal))

    print("")
    count=count+1
