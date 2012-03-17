#!/usr/bin/env python
# encoding: utf-8

#
# Utility.py
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

import os
import unittest
import tempfile
from subprocess import *


class Cmd(object):
  """Run a binary"""
  def __init__(self,command,args=""):

    super(Cmd, self).__init__()
    
    self.command = command
    self.arguments = args
        
    self.isError = 0
    self.error = []
    self.response = []
    
      
    
  
  def run(self):
    """Execute the command with all it's arguments."""
    cmd = self.command + " " + self.arguments
    process = Popen(cmd,stdout=PIPE,stderr=PIPE,shell="true")
    stdout, stderr = process.communicate()
    self.response = stdout.splitlines()
    self.error = stderr.splitlines()
    
    if len(self.error) > 0:
      self.isError = 1
      
    
  def response_asString(self):
    """return the response as a string (instead of line by line)"""
    return("\n".join(self.response))
    
def filetemp():
  (fd, fname) = tempfile.mkstemp()
  return (os.fdopen(fd, "w+b"), fname)

class UtilityTests(unittest.TestCase):
  def setUp(self):
    pass


if __name__ == '__main__':
  unittest.main()