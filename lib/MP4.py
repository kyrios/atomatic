#!/usr/bin/env python
# encoding: utf-8
#
# MP4.py
# Copyright (c) 2012 Thorsten Philipp <kyrios@kyri0s.de>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in the 
# Software without restriction, including without limitation the rights to use, copy,
# modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, 
# and to permit persons to whom the Software is furnished to do so, subject to the
# following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION 
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

import sys
import os
import unittest
import mediafile
import re
import Utility
import time
import shutil
from xml.dom.minidom import Document



class MP4(mediafile.mediafile):
  """MP4 Container Class"""
  
  filetype = "MP4"
  def __init__(self):
    super(MP4, self).__init__()
    
    self.__tracks = []
    self.__chapters = {} # Containing dictionaries with starttime (milliseconds) as key and title as value
    self.__images = {}   # See chapters
    self.__urls = {}     # See chapters
    
    self.meta = dict(               # iTunes shows:
                      composer  = None, # Composer
                      title    = None, # Name
                      artist  = None, # Artist
                      album   = None, # Album
                      encodingTool    = None, # Encoded with ..
                      lyrics  = None, # Lyrics
                      albumArtist = None, # Album Artist
                      genre   = None, # Genre
                      tracknum  = None, # Track Number x of
                      comment = None, # Comment
                      podcastURL = None, # Podcast URL
                      )
    self.cover = None
  
  
  def import_File(self,filename,filetype=None):
    """Import an existing file and add all Tracks to the object"""
    
    if filetype is None:
      filetype = filename[-3:]
    
    # =================
    # = Source is m4a =
    # =================
    if filetype == "m4a":  
      cmd = Utility.Cmd("MP4Box -info %s" % filename)
      cmd.run()
      if cmd.isError:
        print cmd.error
      else:
        track = None
        for line in cmd.response:        
          # Track Information
          # Start of a new Track
          p = re.compile(u'^Track.+- TrackID (\d+) - ')
          m = p.match(line)
          if m:
            track = Track()
            self.add_Track(track)

            track.srctype = "mp4" # That's the file! Type of the file!
            track.srctrackid = m.group(1)
            track.srcfilename = filename
        
          p = re.compile(u'Media Info: Language "(.+)" - Type "(.+)"')  
          m = p.match(line)
          if m:
            track.language = m.group(1)
            track.type = m.group(2)
        
          p = re.compile(u'Track is disabled')
          if p.match(line):
            track.enabled = 0
    
    # =================================
    # = Source is raw audio (aif,wav) =
    # =================================        
    elif filetype == "aif" or filetype == "wav":
      track = Track()
      track.srctype = "raw"
      track.srcfilename = filename
      self.add_Track(track)
      
    # ==================
    # = Unknown format =
    # ==================  
    else:
      print >> sys.stderr, "No support for files of type %s" % (filetype)
      raise NotImplementedError
  
  
  
  
  # ============
  # = Chapters =
  # ============  
    
  def add_Chapterobj(self,chapter):
    """Fill __chapters[], __urls[], __images[]"""
    
    if chapter.title is not None:
      self.__chapters[chapter.starttime] = chapter.title
    if chapter.url is not None and chapter.url["link"] is not None and chapter.url["href"] is not None: 
      self.__urls[chapter.starttime] = chapter.url
    if chapter.picture is not None:
      self.__images[chapter.starttime] = chapter.picture
  
  def write_chaptersToFile(self,filename):
    """Writes the Chapter from self.__chapters to the file using mp4chaps (libmp4v2 Handbrake Edition)"""
    
    # Prepare the file
    try:
      chaptertxtname = filename[:-4]+'.chapters.txt'
      chaptertxt = open(chaptertxtname,'w')
    except:
      raise
    
    for starttime in sorted(self.__chapters.keys()):
      timestamp = time.strftime("%H:%M:%S",time.gmtime(starttime/1000))
      line = "%s.%03d %s\n" % (timestamp,int(starttime % 1000),self.__chapters[starttime]) 
      chaptertxt.write(line)
    
    chaptertxt.close()
    
    cmd = Utility.Cmd("mp4chaps",args="--import \"%s\"" % filename)
    cmd.run()
    if cmd.isError:
      raise Exception(cmd.error)
    os.unlink(chaptertxtname)
  
  def write_chapterlinksToFile(self,filename):
    """Write Hyperlink Track to the m4a using MP4Box --ttxt feature"""
    (ttxtfile,ttxtfilename) = Utility.filetemp()
    
    ttxt = Document()
    TextStream = ttxt.createElement("TextStream")
    TextStream.setAttribute("version","1.1")
    ttxt.appendChild(TextStream)
    
    TextStreamHeader = ttxt.createElement("TextStreamHeader")
    TextStreamHeader.setAttribute("width","160")
    TextStreamHeader.setAttribute("height","160")
    TextStreamHeader.setAttribute("layer","65534")
    TextStreamHeader.setAttribute("translation_x","0")
    TextStreamHeader.setAttribute("translation_y","0")
    TextStream.appendChild(TextStreamHeader)
    
    TextSampleDescription = ttxt.createElement("TextSampleDescription")
    TextSampleDescription.setAttribute("horizontalJustification","center")
    TextSampleDescription.setAttribute("verticalJustification","bottom")
    TextSampleDescription.setAttribute("backColor","0 0 0 0")
    TextSampleDescription.setAttribute("verticalText","no")
    TextSampleDescription.setAttribute("fillTextRegion","no")
    TextSampleDescription.setAttribute("continousKaraoke","no")
    TextSampleDescription.setAttribute("scroll","None")
    TextStreamHeader.appendChild(TextSampleDescription)
    
    FontTable = ttxt.createElement("FontTable")
    TextSampleDescription.appendChild(FontTable)
    
    FontTableEntry = ttxt.createElement("FontTableEntry")
    FontTableEntry.setAttribute("fontName","Serif")
    FontTableEntry.setAttribute("fontID","1")
    FontTable.appendChild(FontTableEntry)
    
    TextBox = ttxt.createElement("TextBox")
    TextBox.setAttribute("top","0")
    TextBox.setAttribute("left","0")
    TextBox.setAttribute("bottom","160")
    TextBox.setAttribute("right","160")
    TextSampleDescription.appendChild(TextBox)
    
    Style = ttxt.createElement("Style")
    Style.setAttribute("styles","Normal")
    Style.setAttribute("fontID","1")
    Style.setAttribute("fontSize","0")
    Style.setAttribute("color","0 0 0 ff")
    TextSampleDescription.appendChild(Style)
    
    
    for starttime in sorted(self.__urls.keys()):
      TextSample = ttxt.createElement("TextSample")
      timestamp = time.strftime("%H:%M:%S",time.gmtime(starttime/1000))
      timestamp = "%s.%03d" % (timestamp,int(starttime % 1000))
      TextSample.setAttribute("sampleTime",str(timestamp))
      TextSample.setAttribute("xml:space","preserve")
      TextSampletxt = ttxt.createTextNode(str(self.__urls[starttime]["link"]))
      TextSample.appendChild(TextSampletxt)
      
      HyperLink = ttxt.createElement("HyperLink")
      HyperLink.setAttribute("fromChar","0")
      HyperLink.setAttribute("toChar","4")
      HyperLink.setAttribute("URL",str(self.__urls[starttime]["href"]))
      HyperLink.setAttribute("URLToolTip","")
      TextSample.appendChild(HyperLink)
      
      TextStream.appendChild(TextSample)
    
    ttxtfile.write(ttxt.toprettyxml(encoding="UTF-8"))
    ttxtfile.close()
    # we need to rename the file to nhml for MP4Box to recognize it
    shutil.move(ttxtfilename, ttxtfilename + ".ttxt")
    ttxtfilename = ttxtfilename + ".ttxt"
    print "Filename: %s" % ttxtfilename
    
    cmd = Utility.Cmd("MP4Box",args="-add \'%s\' -ttxt :lang=eng \'%s\'" % (ttxtfilename,filename))
    cmd.run()
    print cmd.command
    print cmd.arguments
    if cmd.isError:
      raise Exception(cmd.error)

      
    # Unlink files
    #os.unlink(ttxtfilename)
    
    
    
    
  
  def write_chapterimagesToFile(self,filename):
    """Writes Images found in self.__images to the m4a using MP4Box.
    """
    # This is kinda complicated. The following things have to happen
    # Read all images. Remeber size.
    # Write all images to a single temp file.
    # Create an NHML file containing the file offset/size and starttime
    # import the images with MP4BOX. Specification is in NHML. jpegs in tempfile
    
    (media,mediafile) = Utility.filetemp()
    (nhmlfile,nhmlfilename) = Utility.filetemp()
    
    # Prepare NHML File
    nhml = Document()
    NHNTStream = nhml.createElement("NHNTStream")
    nhml.appendChild(NHNTStream)
    
    NHNTStream.setAttribute("baseMediaFile",str(mediafile))
    NHNTStream.setAttribute("version","1.0")
    NHNTStream.setAttribute("timeScale","1000")
    NHNTStream.setAttribute("mediaType","vide")
    NHNTStream.setAttribute("mediaSubType","jpeg")
    NHNTStream.setAttribute("codecVendor",".....")
    NHNTStream.setAttribute("codecVersion","0")
    NHNTStream.setAttribute("codecRevision","0")
    NHNTStream.setAttribute("width","300")
    NHNTStream.setAttribute("height","300")
    NHNTStream.setAttribute("compressorName","")
    NHNTStream.setAttribute("temporalQuality","0")
    NHNTStream.setAttribute("spatialQuality","0")
    #NHNTStream.setAttribute("horizontalResolution","4718592")
    #NHNTStream.setAttribute("verticalResolution","4718592")
    NHNTStream.setAttribute("bitDepth","24")
    

    for starttime in sorted(self.__images.keys()):
      try:
        imagefile = open(self.__images[starttime],"rb")
      except:
        raise
      NHNTSample = nhml.createElement("NHNTSample")
      NHNTStream.appendChild(NHNTSample)
      
      NHNTSample.setAttribute("DTS",str(starttime))
      
      media.write(imagefile.read()) # Append current immage to the tempfile
      NHNTSample.setAttribute("dataLength",str(imagefile.tell())) # Size
      
      NHNTSample.setAttribute("isRAP","yes")
      imagefile.close()
      
      # Write image to NHML File

    media.close()
    nhmlfile.write(nhml.toprettyxml(encoding="UTF-8"))
    nhmlfile.close()
    # we need to rename the file to nhml for MP4Box to recognize it
    shutil.move(nhmlfilename, nhmlfilename + ".nhml")
    
    cmd = Utility.Cmd("MP4Box",args="-add %s \"%s\"" % (nhmlfilename + ".nhml",filename))
    cmd.run()
    if cmd.isError:
      raise Exception(cmd.error)
    
    # Unlink files
    os.unlink(mediafile)
    os.unlink(nhmlfilename + ".nhml")
    
    
  # ==================
  # = Write out file =
  # ==================
  
  def write(self,filename):
    """Write the file to disk (craft it..:-)"""
    
    firsttrack = 1
    try:
      os.unlink(filename)
    except OSError:
      pass
    
    
    firsttrack = 1
    
    
    # ==========================================
    # = Add each track to the destination file =
    # ==========================================
    if len(self.get_Tracks()) < 1  :
      raise Exception("No Tracks found")
    for track in self.get_Tracks():
      print "Adding Track %s (%s)" % (track.srctrackid,track.type)
      
      # ========================
      # = # Source is MP4 File =
      # ========================
      if track.srctype == "mp4"  :
        
        # =============
        # = soun:mp4a =
        # =============
        if track.type == "soun:mp4a":
          if firsttrack:
            cmd = Utility.Cmd("MP4Box",args="-new -add %s#%s:lang=%s \"%s\"" % (track.srcfilename,track.srctrackid,track.language,filename))
            firsttrack = 0
          else:
            cmd = Utility.Cmd("MP4Box",args="-add %s#%s:lang=%s \"%s\"" % (track.srcfilename,track.srctrackid,track.language,filename))
          cmd.run()
          if cmd.isError:
            raise Exception(cmd.error)
        else:
          print "Don't know how to handle Track of Type %s" % (track.type)
          
          
      # =======================
      # = Raw Track (aif,wav) =
      # =======================
      elif track.srctype == "raw":
        raise NotImplementedError("aif and wav are not implemented yet")
        if firsttrack:
          cmd = Utility.Cmd("MP4Box",args="-new -add %s \"%s\"" % (track.srcfilename,filename))
        else:
          cmd = Utility.Cmd("MP4Box",args="-add %s \"%s\"" % (track.srcfilename,filename))
          
        cmd.run()
        if cmd.isError:
          raise Exception(cmd.error) 
          
      # =======================
      # = Unknown Source Type =
      # =======================    
      else:
        print "Don't know how to handle Track from Source of type %s" % (track.srctype)
        

    self.write_chaptersToFile(filename)
    self.write_chapterlinksToFile(filename)
    #self.write_chapterimagesToFile(filename)
    self.write_meta(filename)
      
  
  def write_meta(self,filename):
    """Write the meta Atoms to the m4a"""
    for atom in self.meta.keys():
      if self.meta[atom] is not None:
        cmd = Utility.Cmd("Atomicparsley",args="\"%s\" --overWrite --%s \'%s\'" % (filename,atom,self.meta[atom]))
        cmd.run()
        if cmd.isError:
          raise Exception(cmd.error)
           
  
  # ==========
  # = Tracks =
  # ==========  
  def add_Track(self,Trackobj):
    """Add a Track Object to this MP4"""
    self.__tracks.append(Trackobj)
  
  def get_Tracks(self):
    """Return all Track Objects currently registered with this MP4"""
    return self.__tracks
  
  def delete_Track(self,trackid):
    """Delete a Track from __tracks[]. Trackid is the index. You may find out the index by looking at get_Tracks()"""
    
    
    
    
    
  # ================
  # = Atom Parsing =
  # ================
  
  

  
class Track(object):
  """MP4 Track. Can contain anything a MP4 Container Track can contain (well.. in theory)"""
  def __init__(self):
    super(Track, self).__init__()
    

    self.type = None
    self.language = None
    self.enabled = 1
    self.srctype = "MP4"
    self.srcfilename = None
    self.srctrackid = None
    
    
        

class MP4Tests(unittest.TestCase):
  def setUp(self):
    pass


if __name__ == '__main__':
  unittest.main()