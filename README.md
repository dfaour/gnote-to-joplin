# gnote-to-joplin
Tool to export gnote/tomboy notes to a format compatible with joplin (https://joplinapp.org/), preserving formatting (including bold, italics, and bulleted lists)

Written by David Faour, December 2020
Licensed under GPL 3.0

Usage:
First make sure the directory on line 15 is accurate, then run

>python3 gnote-to-joplin.py

By default, this will place all your exported notes in the export/ directory (it will not touch the original files). You can then import them easily into joplin via MD - Markdown File or Directory.
