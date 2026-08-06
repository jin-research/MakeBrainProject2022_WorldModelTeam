import time
import pytz
import datetime

datafilename = "./data/" + str(datetime.datetime.now(pytz.timezone('Asia/Tokyo'))) + "_data.bin"
datafilename = datafilename.replace(":","_")

print("datafilename",datafilename)
