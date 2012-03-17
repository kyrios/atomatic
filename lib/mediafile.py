#!/usr/bin/env python
# encoding: utf-8
#
# mediafile.py
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

import unittest


class mediafile(object):
  """a mediafile (i know this description sucks)"""
  def __init__(self):
    super(mediafile, self).__init__()
    
  def write(self,filename):
    """write the file to the specified destination"""
    raise NotImplementedError
    
  def import_File(self,filename):
    """Import an existing file and add all available tracks to the object."""
    raise NotImplementedError
    
  def add_Chapters(self,chapterlist):
    """Provide a list of Podcast.Chapter Objects."""
    raise NotImplementedError


class mediafileTests(unittest.TestCase):
  def setUp(self):
    pass


if __name__ == '__main__':
  unittest.main()