import os

def rename(dir, name):
    oldName = "{}\\{}".format(dir, name)
    oldNumber = int(name[:-4])
    newName = "{}\\{}.bmp".format(dir, oldNumber - 2)
    os.rename(oldName, newName)

directory = input("Enter directory to fix: ")
#removes 1.bmp and subtracts 2 from the name of every succeeding bmp

files = os.listdir(directory)

for i in files:
    if ".bmp" in i:
        rename(directory, i)
