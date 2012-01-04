#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
This program "appelizes" your music in a separate directory
"""

__revision__ = "$Id$"
#
# $LastChangedDate$
# $Author$
# $Rev$
# $HeadURL$
#

import os
import mutagen
import thread
from time import sleep

class musicDirectories(object): # {{{
   """docstring for musicDirectories"""

   def __init__(self, srcDir, destDir): # {{{
      super(musicDirectories, self).__init__()

      self.recodeExtensions = { 'ogg'  : 'mp3',
                                'flac' :'mp3',
                              }
      self.maxThreads = 4 

      self.recodeList = []

      # expand the directories
      self.srcDir = os.path.abspath(os.path.expanduser(srcDir))
      self.destDir = os.path.abspath(os.path.expanduser(destDir))

      # FIXME: check if the direcories are on the same filesystem and if
      # it supports hardlinks

      # generate the filelist
      findCmd = 'find "%s" -type f' % self.srcDir
      self.fileList = [ x.strip()[len(self.srcDir)+1:] for x in os.popen(findCmd).readlines() ]

   # }}}

   def checkEncode(self,fileName): # {{{
      """docstring for checkEncode"""
      ext = os.path.splitext(fileName)[1][1:].lower()
      if ext in self.recodeExtensions:
         return ext
      else:
         return False
   # }}}

   def add_to_recode_queue(self,filename): # {{{
      """docstring for recode"""
      self.recodeList.append(filename)
   # }}}

   def hardLink(self,filename): # {{{
      """docstring for hardlink"""
      dest = os.path.join(self.destDir,filename)
      if not os.path.exists(dest):
         src = os.path.join(self.srcDir,filename)
         os.link(src,dest)
   # }}}

   def mkDestDir(self,filename): # {{{
      """docstring for mkDestDir"""
      destDir = os.path.join(self.destDir,os.path.dirname(filename))
      if not os.path.exists(destDir):
         os.makedirs(destDir)
   # }}}

   def easywork(self): # {{{
      """easywork walks through the filelist and checks whether they
      need to be recoded or not. If they don't need to be recoded, it
      sets the hardlink, otherwise it adds them to the recode queue"""
      for i in self.fileList:
         self.mkDestDir(i)
         if self.checkEncode(i):
            self.add_to_recode_queue(i)
         else:
            self.hardLink(i)
   # }}}

   def hardwork(self): # {{{
      """docstring for hardwork"""
      for i in self.recodeList:
         inFile  = os.path.join(self.srcDir,i)
         outFile = os.path.join(self.destDir, '%s.mp3' % os.path.splitext(i)[0])
         if not os.path.exists(outFile):
            self.mkDestDir(i)
            s = Recode(inFile,outFile)
            s.work()
   # }}}

# }}}

class Recode(object): # {{{
   """docstring for Recode"""
   def __init__(self, inFile, outFile, outFormat='mp3'): # {{{
      super(Recode, self).__init__()

      tagTranslate = { # here will be more soon
         'lame' : {
            "album"        : '--tl',
            "artist"       : '--ta',
            "title"        : '--tt',
            "date"         : '--ty',
            "genre"        : '--tg',
            "tracknumber"  : '--tn'
         }
      }

      self.inFile = inFile

      # read the tags from the file
      tags = mutagen.File(inFile)
      if tags == None:
         print "%s has no readable tags"  % (inFile, )
         self.cmd='/bin/true'
      else:

         # get the format according to the extension (cheap!)
         inFormat = os.path.splitext(inFile)[1][1:].lower()

         decoder = {  'flac'   : 'flac --silent --stdout --decode "%s" ' % (inFile, ),
                           'ogg'    : 'oggdec --quiet --output=- "%s" ' % (inFile, ),
                        }

         encoder = {  'mp3' :  'lame',
                           'm4a' :  'faac',
                        }

         encoderOpts = { 'lame' : '-s 44.1 -q 0 -V 0 -v -b 192 -B 256 --quiet -' }

         tagOptions = ''
         for i in tags.keys():
            try:
               tagOptions += ' %s "%s" ' % ( tagTranslate[encoder[outFormat]][i], tags[i][0], )
            except KeyError:
               pass
         try:
            self.cmd = u'%s | %s %s %s "%s"' % (decoder[inFormat], encoder[outFormat], tagOptions, encoderOpts[encoder[outFormat]], outFile, )
         except:
            print decoder[inFormat]
            print encoder[outFormat]
            print tagOptions
            self.cmd='/bin/true'

   # }}}

   def work(self): # {{{
      """docstring for work"""
      print "recoding: %s" % (self.inFile,)
      #print self.cmd
      os.system(self.cmd.encode('utf8'))
   # }}}

# }}}

if __name__ == "__main__":

   m = musicDirectories('~/Musik/Tool', '~/applemusic')

   m.easywork()
   m.hardwork()




# vim:foldmethod=marker:tabstop=3:autoindent:shiftwidth=3:expandtab
