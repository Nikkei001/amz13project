# This code tracks the iteration of productIDs.
from data.file_infomations import FILE_INFOMATION as finfos
from utils.file_processing import fileProcessing

for fileinfo in finfos:
    fileProcessing(fileinfo, True)

def main():
    print("hola")

if __name__ == "__main__":
    main()