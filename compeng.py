#Composition Engine
import pickle
import time
from structures import *

def saveBMP(data, folder, number):
    header = bytearray(54)
    size = len(data) + 54

    header[0] = 66
    header[1] = 77
    header[2] = size % 256
    header[3] = size % 65536 % 256
    header[4] = size & 65536
    header[10] = 54
    header[14] = 40
    header[18] = 640 % 256
    header[19] = int((640 - (640 % 256))/256);
    header[22] = 360 % 256;
    header[23] = int((360-(360%256))/256);
    header[26] = 1;
    header[28] = 24;
    header[49] = 1;
    
    file = open("{}\{}.bmp".format(folder, number), "wb")
    file.write(header + data)
    file.close()

def load(filename):
    file = open(filename, "rb")
    timeline = pickle.load(file)
    file.close()
    return timeline

def loadFrame(folder, number):
    file = open("{}\{}.bmp".format(folder, number + 2), "rb")
    frame = file.read()[54:]
    file.close()
    return bytearray(frame)

def pad(num):
    num = hex(int(num))[2:]
    if len(num) == 1: num = "0" + num
    return num

class RGB: #tinu.proj
    def __init__(self, *args):
        if len(args) == 1:
            string = args[0]
            self.R = eval("0x" + string[0:2])
            self.G = eval("0x" + string[2:4])
            self.B = eval("0x" + string[4:])
        else:
            self.R = (args[0])
            self.G = (args[1])
            self.B = (args[2])

    def __add__(self, other):
        return RGB(self.R + other.R, self.G + other.G, self.B + other.B)

    def __mul__(self, other):
        return RGB(self.R * other, self.G * other, self.B * other)

    def __eq__(self, other):
        return (self.B == other.B) and (self.G == other.G) and (self.R == other.R)
    
    def __str__(self): #pad out output
        return pad(self.R) + pad(self.G) + pad(self.B)

def render(timeline, folder): #files will be saved as folder\#.bmp where # is the frame number
    frames = 573 #placeholder until actual framenumber can be found

    currentTime = time.time_ns()
    
    for i in range(frames):

        frame = bytearray(640 * 360 * 3)
        print("{}: ".format(i), end = "")
        for t in range(len(timeline)): #go through each layer
            clip = None
            tc = None
            #filter = None
            #filterTc = None
            chromaKey = None #will contain color if true
            position = None #will contain coordinates if true
            opacity = None #will contain percentage if true


            for p in timeline[t]["clips"]:
                #print("{} | {}".format(i, p))
                if p.contains(i):
                    clip = timeline[t]["clips"][p]
                    tc = p
                    print("(L{}) {} F{} | ".format(t, clip.file, i - tc.begin + clip.beginning), end = '')

            for p in timeline[t]["filters"]: #there can be multiple filters at one frame in a given layer
                #print("{} | {}".format(i, p))
                if p.contains(i):
                    if timeline[t]["filters"][p].filterType == "CHROMAKEY":
                        chromaKey = RGB(timeline[t]["filters"][p].beginParam)
                        print("CHROMAKEY {} | ".format(chromaKey), end = '')

                    if timeline[t]["filters"][p].filterType == "POSITION":
                        #divide distance from beginning by length of filter
                        distance = i - p.begin
                        change = distance / (p.end - p.begin)
                        bParam = eval(timeline[t]["filters"][p].beginParam)
                        eParam = eval(timeline[t]["filters"][p].endParam)
                        position = int((1 - change) * bParam[0] + change * eParam[0]), int((1 - change) * bParam[1] + change * eParam[1])
                        print("POSITION {} | ".format(position), end = '')

                    if timeline[t]["filters"][p].filterType == "OPACITY":
                        #divide distance from beginning by length of filter
                        distance = i - p.begin
                        change = distance / (p.end - p.begin)
                        opacity = ((1 - change) * int(timeline[t]["filters"][p].beginParam) + change * int(timeline[t]["filters"][p].endParam)) / 100
                        print("OPACITY {} | ".format(round(opacity, 3)), end = '')

            """
                filter detection rules for filters within the current time
                    is it a key? log down that fact and the color
                    is it a position? log down that fact and the immediate position
                    is it an opacity? log down that fact and the immediate opacity

                    when it comes time to draw the frame
                        if no filter, just replace the current frame
                        if it is just a key,
                        if it is just opacity, for every pixel in the image, mix appropriately
                        if it is just position, 
                        if it is just a key and opacity, for every pixel in the new image, if it's the key, ignore it, if not, mix appropriately
                        if it is just a key and position, 
                        if it is just a position and opacity,
                        if it is a key, position, and opacity, 
            """

            if opacity and position and chromaKey: #implement
                currentFrame = loadFrame(clip.file, i - tc.begin + clip.beginning)
                p = 0

                for x in range(640):
                    for y in range(360):
                        basepos = 3 * (x + y * 640)

                        if (x + position[0]) < 640 and (x + position[0]) >= 0 and (y + position[1]) < 360 and (y + position[1]) >= 0:
                            pixelpos = (x + position[0] + 640 * (y + position[1])) * 3
                            currentColor = RGB(currentFrame[pixelpos], currentFrame[pixelpos + 1], currentFrame[pixelpos + 2])
                            baseColor = RGB(frame[basepos], frame[basepos + 1], frame[basepos + 2])

                            if currentColor != chromaKey:
                                newColor = baseColor * (1 - opacity) + currentColor * opacity
                                frame[basepos] = int(newColor.R)
                                frame[basepos + 1] = int(newColor.G)
                                frame[basepos + 2] = int(newColor.B)

            elif opacity and position:
                pass

            elif opacity and chromaKey:
                currentFrame = loadFrame(clip.file, i - tc.begin + clip.beginning)
                p = 0

                while p < len(frame):
                    currentColor = RGB(currentFrame[p], currentFrame[p + 1], currentFrame[p + 2])
                    baseColor = RGB(frame[p], frame[p + 1], frame[p + 2])

                    if currentColor != chromaKey:
                        newColor = baseColor * (1 - opacity) + currentColor * opacity
                        frame[p] = int(newColor.R)
                        frame[p + 1] = int(newColor.G)
                        frame[p + 2] = int(newColor.B)

                    p += 3

            elif chromaKey and position: #implement
                currentFrame = loadFrame(clip.file, i - tc.begin + clip.beginning)
                p = 0

                for x in range(640):
                    for y in range(360):
                        basepos = 3 * (x + y * 640)

                        if (x + position[0]) < 640 and (x + position[0]) >= 0 and (y + position[1]) < 360 and (y + position[1]) >= 0:
                            pixelpos = (x + position[0] + 640 * (y + position[1])) * 3
                            currentColor = RGB(currentFrame[pixelpos], currentFrame[pixelpos + 1], currentFrame[pixelpos + 2])

                            if currentColor != chromaKey:
                                frame[basepos] = currentColor.R
                                frame[basepos + 1] = currentColor.G
                                frame[basepos + 2] = currentColor.B

            elif position:
                pass

            elif chromaKey:
                currentFrame = loadFrame(clip.file, i - tc.begin + clip.beginning)
                p = 0

                while p < len(frame):
                    currentColor = RGB(currentFrame[p], currentFrame[p + 1], currentFrame[p + 2])

                    if currentColor != chromaKey:
                        frame[p] = currentFrame[p]
                        frame[p + 1] = currentFrame[p + 1]
                        frame[p + 2] = currentFrame[p + 2]
                    
                    p += 3

            elif opacity:
                currentFrame = loadFrame(clip.file, i - tc.begin + clip.beginning)
                
                for p in range(len(frame)):
                    color = int((1 - opacity) * frame[p] + currentFrame[p] * opacity)
                    frame[p] = color

            elif clip: 
                #print("(L{}) {} F{} | ".format(t, clip.file, i - tc.begin + clip.beginning), end = '')
                frame = loadFrame(clip.file, i - tc.begin + clip.beginning)

                  
            
        print("")

        saveBMP(frame, folder, i)
        #print("Saving current frame to {}\{}.bmp".format(folder, i))
        
    
    return (time.time_ns() - currentTime) / (1000*1000*1000)

def test():
    timeline = load("tinu.proj")
    return render(timeline, "test")
