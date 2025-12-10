from data.file_infomations import FILE_INFOMATION as finfos
from utils import data_cleaning as dacln
from utils import exportToDatabase as extd

def fileProcessing(fileinfo):
    cleaned_data = dacln.data_cleaning(
        fileinfo['file_path'],
        fileinfo['key_word'],
        fileinfo['sheet'],
        fileinfo['column_used'],
        fileinfo['column_dropna']
    )

    exportData = extd.export_to_postgres(
        cleaned_data,
        fileinfo['database_table']
    )

for fileinfo in finfos:
    fileProcessing(fileinfo)

def main():
    print("hola")

if __name__ == "__main__":
    main()