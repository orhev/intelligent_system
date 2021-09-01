import ftplib
import sys


def getFile(ftp, filename):
    try:
        ftp.retrbinary("RETR " + filename, open(filename, 'wb').write)
    except:
        print("Error")


ftp = ftplib.FTP("gtfs.mot.gov.il")
ftp.login("", "")
data = []

ftp.dir(data.append)

getFile(ftp,"ChargingRavKav.zip")
getFile(ftp,"ClusterToLine.zip")
getFile(ftp,"israel-public-transportation.zip")
getFile(ftp,"Tariff.zip")
getFile(ftp,"TrainOfficeLineId.zip")
getFile(ftp,"TripIdToDate.zip")
getFile(ftp,"zones.zip")