#cloner
import os
path = input("path to duplicate: ")
number = int(input("number of frames: "))
string = ''

for i in range(number):
    string += "copy {}\\0.bmp {}\\{}.bmp\n".format(path, path, i)

file = open("temp.bat", "w")
file.write(string)
file.close()

os.system("temp")
