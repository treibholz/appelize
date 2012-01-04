#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
This program "appelizes" your music into a separate directory.

It recodes audio files that don't work in the apple world (like flac and ogg)
and hardlinks the unknown ones (like mp3, jpeg and so on.) The result is a
space saving copy of your music.

At the moment it recodes everything to mp3, but other formats will be
supported in the future.
"""

__revision__ = "0.1"

import os
import mutagen
import thread
from time import sleep

class musicDirectories(object): # {{{
   """initialize your two directories"""

   def __init__(self, srcDir, destDir): # {{{
      super(musicDirectories, self).__init__()

      self.recodeExtensions = { 'ogg'  : 'mp3',
                                'flac' :'mp3',
                              }
      self.maxThreads = 4 

      self.recode_queue = []

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
      """checkEncode checks if a file needs to be recoded or not,
      according to it's file-extension."""
      ext = os.path.splitext(fileName)[1][1:].lower()
      if ext in self.recodeExtensions:
         return ext
      else:
         return False
   # }}}

   def add_to_recode_queue(self,filename): # {{{
      """add a file to the recode_queue"""
      self.recode_queue.append(filename)
   # }}}

   def hardLink(self,filename): # {{{
      """hardlinks a file, if it isn't there yet."""
      dest = os.path.join(self.destDir,filename)
      if not os.path.exists(dest):
         src = os.path.join(self.srcDir,filename)
         os.link(src,dest)
   # }}}

   def mkDestDir(self,filename): # {{{
      """creates the destination directory"""
      destDir = os.path.join(self.destDir,os.path.dirname(filename))
      if not os.path.exists(destDir):
         os.makedirs(destDir)
   # }}}

   def easywork(self): # {{{
      """easywork walks through the filelist and checks whether they
      need to be recoded or not. If they don't need to be recoded, it
      sets the hardlink, otherwise it adds them to the recode queue.
      This is the easy part."""

      for i in self.fileList:
         self.mkDestDir(i)
         if self.checkEncode(i):
            self.add_to_recode_queue(i)
         else:
            self.hardLink(i)
   # }}}

   def hardwork(self): # {{{
      """hardwork does the hard work, it recodes the files."""

      for i in self.recode_queue:
         inFile  = os.path.join(self.srcDir,i)
         outFile = os.path.join(self.destDir, '%s.mp3' % os.path.splitext(i)[0])
         if not os.path.exists(outFile):
            self.mkDestDir(i)
            s = Recode(inFile,outFile)
            s.work()
   # }}}

# }}}

class Recode(object): # {{{
   """The actual recoding happens here."""
   def __init__(self, inFile, outFile, outFormat='mp3'): # {{{
      """compiles the command to recode"""
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
      """Do the work: recode the file"""
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
