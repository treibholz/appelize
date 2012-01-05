#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
This program "appelizes" your music into a separate directory.

It recodes audio files that don't work in the apple world (like flac and ogg)
and hardlinks the unknown ones (like mp3, jpeg and so on...). The result is a
space saving copy of your music.

At the moment it recodes everything to mp3, but other formats will be
supported in the future.
"""

__revision__ = "0.2"

import os
import re
import sys
import mutagen
import threading
from time import sleep

class musicDirectories(object): # {{{
   """
   initialize your two directories

   @srcDir      : the source directory, where your free music lives
   @destDir     : the destination directory, where your non-free music
                  will live.
   @max_threads : (optional) the amount of threads you want to start,
                  default is the amount of cpus found in the system
                  (or one)
   """

   def __init__(self, srcDir, destDir, max_threads=False): # {{{
      super(musicDirectories, self).__init__()

      self.recodeExtensions = { 'ogg'  : 'mp3',
                                'flac' : 'mp3',
                              }

      # if max_threads is not set, set the amount of CPUs. If this is not possible
      # maybe because it is an old linux or no linux at all, set it to 1.
      if not max_threads:
         try:
            # this is a very primitive way, we need a better method here...
            self.max_threads = int(open('/sys/devices/system/cpu/possible').readline().strip()[-1])+1
         except:
            self.max_threads = 1

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

      work_threads = []

      for i in self.recode_queue:
         inFile  = os.path.join(self.srcDir,i)
         # get the extension of the outfile
         destExt = self.recodeExtensions[os.path.splitext(i)[1][1:]]
         outFile = os.path.join(self.destDir, '%s.%s' % (os.path.splitext(i)[0], destExt,) )

         if not os.path.exists(outFile):
            self.mkDestDir(i)
            sleep(0.1)

            while Recode.thread_count >= self.max_threads:
               sleep(0.1)

            thread = Recode(inFile,outFile,destExt)
            work_threads.append(thread)
            thread.start()

      for t in work_threads:
         t.join()
   # }}}

# }}}

class Recode(threading.Thread): # {{{
   """The actual recoding happens here."""

   thread_count = 0
   lock = threading.Lock()

   def __init__(self, inFile, outFile, outFormat='mp3'): # {{{
      """recode"""
      super(Recode, self).__init__()
      Recode.lock.acquire()
      Recode.thread_count += 1
      Recode.lock.release()

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

      self.inFile  = re.sub('`','\`',inFile.decode('utf8'))
      self.outFile = re.sub('`','\`',outFile.decode('utf8'))

      # read the tags from the file
      tags = mutagen.File(inFile)
      if tags == None:
         print "%s has no readable tags"  % (inFile, )
         self.cmd='/bin/true'
      else:

         # get the format according to the extension (cheap!)
         inFormat = os.path.splitext(inFile)[1][1:].lower()

         decoder = {  'flac'   : u'flac --silent --stdout --decode ',
                      'ogg'    : u'oggdec --quiet --output=- ',
                   }

         encoder = {  'mp3' :  u'lame',
                      'm4a' :  u'faac',
                   }

         encoderOpts = { 'lame' : u'-q 0 -V 0 -b 192 -B 320 --quiet -' }

         tagOptions = ''
         # assemble the options for the (id3-)tags
         for i in tags.keys():
            try:
               tagOpt = tagTranslate[encoder[outFormat]][i]
               tag = re.sub('"','\\"',re.sub('`','\`',tags[i][0]))
               tagOptions += u""" %s "%s" """ % ( tagOpt, tag, )
            except KeyError:
               pass
         self.cmd = """%s "%s" | %s %s %s "%s" """ % (decoder[inFormat], self.inFile, encoder[outFormat], tagOptions, encoderOpts[encoder[outFormat]], self.outFile, )

   # }}}

   def run(self): # {{{
      """Do the work: recode the file"""
      print "recoding: %s" % (self.inFile,)
      print self.cmd
      os.system(self.cmd.encode('utf8'))

      Recode.lock.acquire()
      Recode.thread_count -= 1
      Recode.lock.release()


   # }}}

# }}}

if __name__ == "__main__":

   if len(sys.argv) != 3:
      print "usage: %s <srcDir> <destDir>"
      sys.exit(1)
   else:
      srcDir = sys.argv[1]
      destDir = sys.argv[2]

      m = musicDirectories(srcDir, destDir)

      m.easywork()
      m.hardwork()




# vim:foldmethod=marker:tabstop=3:autoindent:shiftwidth=3:expandtab
