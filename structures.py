#use seconds instead of frames or make editing sw account for mixing framerates?

class Clip: #position in timeline is stored separately
  def __init__(self, file, beginning, end):
    self.file = file #origin
    self.beginning = beginning #first frame
    self.end = end #final frame
  
  def __str__(self):
    return "{} | TC:{}-{}".format(self.file, self.beginning, self.end)

"""
Notes on change for the above Clip class
-------
A transition inherits from the Clip type and has links to both source clips, duration, transition type.
Speed, when it causes playback at a nonstandard framerate for the source clip, is to be stored internally to the clip. (e.g. 1x)

Clips will always be at their native resolution without an explicit resize filter.
"""

class Filter: #two keyframes - beginning and end
  def __init__(self, filterType, beginParam, endParam): #nonlinear rate of change function?
    self.filterType = filterType #what kind of effect?
    self.beginParam = beginParam
    self.endParam = endParam

  def __str__(self):
    return "{} | {}->{}".format(self.filterType, self.beginParam, self.endParam)

class Timecode:
  def __init__(self, begin, end):
    self.begin = begin
    self.end = end

  def contains(self, timecode):
    return self.begin <= timecode < self.end

  def __str__(self):
    return "{}:{}".format(self.begin, self.end)
  

"""
FILE FORMAT
-----------
Pickle containing list of layers
Each layer contains a dict with two keys - "filters" and "clips", each of which themselves contain dicts matching Timecode keys to Filter or Clip objects, respectively
"""
