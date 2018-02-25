'''
Created on 11 Feb 2018

@author: julianporter
'''
import unittest

import pcm2mp3;

class Test(unittest.TestCase):
    
    def setUp(self):
        self.infile='test.wav';
        self.outfile='test.mp3';
        self.rate=8
        self.quality=5
    
    def test_stream(self):
        with open(self.infile,"rb") as f:
            stream=f.read()
            self.assertRaises(pcm2mp3.MP3Error,pcm2mp3.transcode,stream,bitrate=self.rate,quality=self.quality)
      
    def test_file(self):
        self.assertRaises(pcm2mp3.MP3Error,pcm2mp3.transcode,self.infile,self.outfile,bitrate=self.rate,quality=self.quality) 


    def testName(self):
        return "Trsnscodrer basic tests"


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()