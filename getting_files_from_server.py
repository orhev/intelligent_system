import ftplib
import zipfile
import os


def get_file(ftp_server, filename):
    try:
        ftp_server.retrbinary("RETR " + filename, open(filename, 'wb').write)
    except:
        print("Error")


dir_path = os.path.dirname(os.path.realpath(__file__))
ftp_server = ftplib.FTP("gtfs.mot.gov.il")
ftp_server.login("", "")
data = []

ftp_server.dir(data.append)

print("Getting files from ftp server...")
get_file(ftp_server, "ClusterToLine.zip")
get_file(ftp_server, "israel-public-transportation.zip")

print("Extracting zip...")
with zipfile.ZipFile(dir_path + '\\israel-public-transportation.zip', 'r') as zip_ref:
    zip_ref.extractall(dir_path)

with zipfile.ZipFile(dir_path + '\\ClusterToLine.zip', 'r') as zip_ref:
    zip_ref.extractall(dir_path)
