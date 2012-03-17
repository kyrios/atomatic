#!/usr/bin/env python
# encoding: utf-8
"""
podcast.py

Copyright (C) 2009  Thorsten Philipp

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

"""

import sys
import os
import unittest
import xml2obj
import MP4



class Podcast(object):
  """Basic Podcast Class.
    Init with an existing mediafile (e.g. .m4a)
    All Audio and Videotracks from this file will be added to this podcast instance.
    Depending on the output format they will be preserved when writing to the disk again. (mp3 will of course not contain a videotrack)
  """
  def __init__(self, srcfile, name=None,url=None,producer=None,comment=None,logo=None,genre="Podcast",episodenum=None,episodename=None,shownotes=None):
    super(Podcast, self).__init__()
    self.srcfile = srcfile
    
    # ==========
    # = Global =
    # ==========
    self.name = name #Name of the podcast
    self.url = url # Podcast URL
    self.producer = producer
    self.comment = comment # Free Text
    self.logo = logo
    self.genre = genre
    
    # ====================
    # = Episode specific =
    # ====================
    self.episodenum = episodenum # Track Number
    self.episodename = episodename
    if self.episodename == None:
      self.episodename = os.path.basename(srcfile)[:-4] # Episode Title
    self.shownotes = shownotes # Lyrics

    
    self.__chapters = []
    self.__targets = []
    
    
  # ==============
  # = Automation =
  # ==============  
  def parse_episode_xml(self,xmlfile):
    """Parse a episode xml. The format of this file is derived from Apples Chapter Tool XML.
    Additional information may be supplied such as episode specific meta information. See the example."""
    
    
    if os.path.isfile(xmlfile):  
      try:
           rawxml = open(xmlfile)
      except IOError: # EA-Fehler
           print >> sys.stderr, "Failed reading Episode XML file '%s'." % self.xmlfile
           return 2
    else:
      raise ("Episode XML %s doesn't exist. Use -e to specify the file" % xmlfile)

    Parser = xml2obj.Xml2Obj()
    XML = Parser.Parse(rawxml)
    
    for root in XML.getElements():
      
      
      if root.name == "CHAPTERS":
        for element in root.getElements():
            chapter = Chapter(starttime = self.__to_milliseconds(element.getAttribute("starttime")))
            for elem in element.getElements():
              if elem.name == "TITLE":
                chapter.title = elem.getData()
              elif elem.name == "PICTURE":
                basedir = os.path.abspath(os.path.dirname(xmlfile))
                imagepath = os.path.abspath(basedir + os.path.sep + elem.getData())
                if not os.path.isfile(imagepath):
                  print "WARNING: Chapterimage %s doesn't exist. Ignoring" % imagepath
                else:
                  chapter.picture = imagepath
              elif elem.name == "LINK":
                chapter.url = dict(link=elem.getData(),href=elem.getAttribute('href'))
              else:
                print "WARNING. Unknown Element found in XML %s" % elem.name
            self.add_chapter(chapter)
            
      if root.name == "TITLE":
        self.episodename = root.getData()
      if root.name == "NUMBER":
        self.episodenum = root.getData()
      if root.name == "SHOWNOTES":
        self.shownotes = root.getData()
        self.shownotes = self.shownotes.replace('\\n','\n') # Convert string '\n' to real linebreak
        
  # =============
  # = Write out =
  # =============
  def add_Target(self,filetype="Audio",fileformat="m4a"):
    """Add a target format which can be written later on with self.write()
    filetype: Audio or Video
    fileformat: m4a, mp3, ogg (...)
    """
    # =================
    # = Audio Podcast =
    # =================
    if filetype == "Audio":
      
      # =======
      # = m4a =
      # =======
      if fileformat == "m4a":
        print "Adding m4a Output"
        
        target = MP4.MP4()
        target.suffix = "m4a"
        target.import_File(self.srcfile)
        for chapter in self.get_Chapters():  
          target.add_Chapterobj(chapter)
        
        
        target.meta['composer'] = self.producer
        target.meta['title'] = self.episodename
        target.meta['artist'] = self.producer
        target.meta['album'] = self.name
        target.meta['encodingTool'] = "Atomatic 0.1 (http://www.atomatic.info)"
        target.meta['lyrics'] = self.shownotes
        target.meta['albumArtist'] = self.producer
        target.meta['genre'] = "Podcast"
        target.meta['tracknum'] = self.episodenum
        target.meta['comment'] = self.producer
        target.meta['podcastURL'] = self.url
        
        
        
        self.__targets.append(target)
      else  :
        raise NotImplementedError
    
    # =================
    # = Video Podcast =
    # =================:
    elif filetype == "Video":
      raise NotImplementedError()
    
    else:
      raise NotImplementedError()
      
      
      
    
    
    
    
    
  def write(self,destinationfolder):
    """write the podcast to disk. Format depends on configuration (self.targets)"""
    for target in self.__targets:
      filename = "%s - [%s] %s.%s" % (self.name,self.episodenum,self.episodename,target.suffix)
      destination = "%s%s%s" % (destinationfolder,os.path.sep,filename)

      target.write(destination)
  
  # ============
  # = Chapters =
  # ============
    
  def add_chapter(self,Chapterobj):
    """Add a Chapter Object to this podcast"""
    self.__chapters.append(Chapterobj)      
     
  def get_Chapters(self):
    """Returns defined Chapters as a list of Chapter Objects"""
    return self.__chapters




  # =====================
  # = Utility Functions =
  # =====================
  def __to_milliseconds(self,timestring):
    """Convert and return a timestring (mm:ss) to milliseconds"""
    try:
      (hours,mins,secs) = timestring.split(":")
    except ValueError:
        hours = 0
        (mins,secs) = timestring.split(":")
        
    return (int(hours)*60*60 + int(mins)*60 + int(secs))*1000





class Chapter(object):
  """A Chapter within a Podcast Episode."""
  def __init__(self, starttime=0,title=None,picture=None,url=None):
    super(Chapter, self).__init__()
    self.starttime = starttime
    self.title = title
    self.picture = picture
    self.url = url
    

    



class podcastTests(unittest.TestCase):
  def setUp(self):
    pass


if __name__ == '__main__':
  unittest.main()