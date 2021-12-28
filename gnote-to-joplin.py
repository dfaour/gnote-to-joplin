#gnote-to-joplin - a tool to export gnote/tomboy notes into a markdown format compatible with joplin, while preserving formatting (bulleted lists, bold, italics)
#
#Written by David Faour, December 2020
#Licensed under GPL 3.0
#
#Usage: first set directory path on line 15, then run python3 gnote-to-joplin.py

import os
import time
import sys
import datetime

startTime = time.time()

directory = os.path.expanduser('~') + "/.local/share/gnote/"

extension = ".note"

outputdir = "export/"
outputextension = ".md"
try:
    os.mkdir(outputdir)
except:
    pass

#Metadata variables - change as needed:
metadata_on = 1 #switch to 0 to turn off adding old metadata into the end of the note
source = "Gnote / Tomboy"
author = "David Faour"


#Definitions for formatting replacements
ul1_fr = '<list><list-item dir="ltr">'
ul2_fr = '</list-item><list-item dir="ltr">'
ul3_fr = '</list-item></list>'

bold_fr = '<bold>'
bold_to = '**'
bold_end_fr = '</bold>'
bold_end_to = '**'

italic_fr = '<italic>'
italic_to = '*'
italic_end_fr = '</italic>'
italic_end_to = '*'

ignore = ['</note-content>','<?xml version="1.0"?>']

title = ""

masterCount = 0

#filename = sys.argv[1]

def convert(lines):

    global filename
    global title

    counter = 0
    level = 0
    bullet = 0
    
    for i in lines:
        newline = i
    #For bullets
        if i[:4] == "<lis": #this means we promote to new bullet level
            level = level + 1
            if bullet == 0: #if this is a new list then level stays at 0
                level = 0
            bullet = 1
        elif i[:4] == "</li": #then do not promote level, stay at same bullet level
            level = level - 1
            if level < 0:
                level = 0
            bullet = 1
        else: #we're not dealing with a list then
            level = 0
            bullet = 0
    
        if bullet == 1:
            replace = '    ' * level + '- '
            newline = newline.replace(ul1_fr,replace).replace(ul2_fr,replace).replace(ul3_fr,replace)
    
        #For bold
        newline = newline.replace(bold_fr,bold_to)
        if bold_end_fr in newline:      #this is required for bold and italics because sometimes we have the </bold> on the next line while joplin expects it on the same line
            if newline[:6] == "</bold": #if the </bold> is at the start of the line put the end ** at the end of the previous line
                lines[counter - 1] = lines[counter - 1].strip() + bold_end_to + "\n"
                newline = newline.replace(bold_end_fr,"")
            else:
                newline = newline.replace(bold_end_fr,bold_end_to)

        #Italic
        newline = newline.replace(italic_fr,italic_to)
        if italic_end_fr in newline:      #see above notes for bold - same applies here
            if newline[:6] == "</ital": 
                lines[counter - 1] = lines[counter - 1].strip() + italic_end_to + "\n"
                newline = newline.replace(italic_end_fr,"")
            else:
                newline = newline.replace(italic_end_fr,italic_end_to)

        #Ignores:
        for j in ignore:
            newline = newline.replace(j,"")

        #put it all together
        lines[counter] = newline
        counter += 1
        if "</text>" in i:      #Let's make a note of this line so we know where the metadata starts
           metadata = counter

    #Get title
    title = lines[1].split("<")
    if len(title) > 3: #for some reason titles are stored differently in different notes - some in line 2 (gives a list of length 6), some in line 3 (then the list in line 2 is only length 2)
        title = title[2][6:]
    if len(title) < 3:
        title = lines[2][9:-9]

    #Now that we have the title we need to kill the first few lines of useless stuff until the note-content starts
    while "note-content" not in lines[0]:
        lines.pop(0)
    
    lines[0] = "# " + title + "\n" #Add in the title

    #Now let's go through the metadata at the end
    lastchangedate = ""
    createdate = ""
    for j in range(metadata - 4,len(lines)):
        k = lines[j]
        k = k.split("<")
        for l in k:
            if "last-change-date" in l and "/last-change-date" not in l:
                lastchangedate = l[17:]
            if "create-date" in l and "/create-date" not in l:
                createdate = l[12:]

    #for joplin ID we will just use the filename
    jid = filename.replace("-","").replace(".note","")

    while "</text>" not in lines[len(lines) - 1]: #now delete these lines
        lines.pop(len(lines) - 1)

    lines.pop(len(lines) - 1) #get rid of the </text> line itself

    #and replace them with the joplin metadata format: - NEVER MIND - this is not working for some reason. Joplin doesn't recognize the metadata and puts it as part of the note. So I am just adding an optional bare bones metadata added to the end of the note
#    meta = "id: \nparent_id:\ncreated_time: " + createdate + "\nupdated_time: " + lastchangedate + "\nis_conflict: 0\nlatitude: 0.00000000\nlongitude: 0.00000000\naltitude: 0.0000\nauthor: " + author + " \nsource_url: \nis_todo: 0\ntodo_due: 0\ntodo_completed: 0\nsource: " + source + "\nsource_application:\napplication_data: \norder: \nuser_created_time: " + createdate + "\nuser_updated_time: " + lastchangedate + "\nencryption_cipher_text: \nencryption_applied: 0\nmarkup_language: 1\nis_shared: 0\ntype_: 1"
    if metadata_on == 1:
        lines.append("\n\n* * *\nNote imported from " + source + " on " + str(datetime.date.today()) + ". Original metadata imported at that time:\n")
        if createdate != "":
            lines.append("Note created: " + createdate + "\n")
        if lastchangedate != "":
            lines.append("Note last changed: " + lastchangedate + "\n")
        if author != "":
            lines.append("Author: " + author)

    return lines




#Now let's start by getting a list of everything in the input directory and then go through one by one

allnotes = os.listdir(directory)
for filename in allnotes:
    if filename.endswith(extension):
        masterCount += 1
        print("Converting " + filename + "...")
        file_object = open(directory + filename,'r')
        lines = file_object.readlines()
        file_object.close()
        lines = convert(lines)
        print("Done! Exporting new note '" + title.replace("\n","") + "' to file + " + outputdir + title.replace("\n","") + outputextension + "...")

        #now output to a new file with name of the note's title
        newFile = open(outputdir + title.replace("\n","").replace("/","").replace("'","").replace('"','').replace("\\","").replace("&","").replace("(","").replace(")","") + outputextension,"w")
        for j in lines:
            newFile.write(j)
        newFile.close()
        print("File successfully converted.")
        print()

print(str(masterCount) + " notes converted in " + str(time.time() - startTime) + " seconds.")
