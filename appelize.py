#!/usr/bin/python
# -*- coding: utf-8 -*-
#
__revision__ = "$Id$"
#
# $LastChangedDate$
# $Author$
# $Rev$
# $HeadURL$
#

import os

class musicDirectories(object):
   """docstring for musicDirectories"""
   def __init__(self, srcDir, destDir):
      super(musicDirectories, self).__init__()

      self.recodeExtensions = { 'ogg'  : 'mp3',
                                'flac' :'mp3',
                              }
      self.recodeList = []

      # expand the directories
      self.srcDir = os.path.abspath(os.path.expanduser(srcDir))
      self.destDir = os.path.abspath(os.path.expanduser(destDir))

      # FIXME: check if the direcories are on the same filesystem and if
      # it supports hardlinks

      # generate the filelist
      findCmd = 'find "%s" -type f' % self.srcDir
      self.fileList = [ x.strip()[len(self.srcDir)+1:] for x in os.popen(findCmd).readlines() ]


   def checkEncode(self,fileName):
      """docstring for checkEncode"""
      ext = os.path.splitext(fileName)[1][1:].lower()
      if ext in self.recodeExtensions:
         return ext
      else:
         return False

   def recode(self,filename):
      """docstring for recode"""
      self.recodeList.append(filename)

   def hardLink(self,filename):
      """docstring for hardlink"""
      dest = os.path.join(self.destDir,filename)
      if not os.path.exists(dest):
         src = os.path.join(self.srcDir,filename)
         os.link(src,dest)

   def mkDestDir(self,filename):
      """docstring for mkDestDir"""
      destDir = os.path.join(self.destDir,os.path.dirname(filename))
      if not os.path.exists(destDir):
         os.makedirs(destDir)

   def easywork(self):
      """docstring for work"""
      for i in self.fileList:
         self.mkDestDir(i)
         if self.checkEncode(i):
            self.recode(i)
         else:
            self.hardLink(i)

   def hardwork(self):
      """docstring for hardwork"""
      print self.recodeList


if __name__ == "__main__":

   m = musicDirectories('~/Musik', '~/applemusic')

   m.easywork()
   m.hardwork()




# vim:foldmethod=marker:tabstop=3:autoindent:shiftwidth=3:expandtab
