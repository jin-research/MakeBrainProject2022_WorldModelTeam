
import time
import pytz
import datetime

datafilename = "./data/" + str(datetime.datetime.now(pytz.timezone('Asia/Tokyo'))) + "_data.bin"

f = open("test.txt","a")
f.write("{}\n".format(datafilename))
f.close()
print("write")
f = open("test.txt","a")
f.write("{}\n".format(datafilename))
f.close()
print("write")
f = open("test.txt","w")
f.write("{}\n".format(datafilename))
f.close()
print("write")
f = open("real_data_names_store.txt","r")
print("read :", f.read())
f.close()
