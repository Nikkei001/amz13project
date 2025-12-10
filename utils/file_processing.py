from utils import data_cleaning as dacln
from utils import exportToDatabase as extd
import pandas as pd

def fileProcessing(fileinfo, need_melt = False, customTableName = ""):
    cleaned_data = dacln.data_cleaning(
        fileinfo['file_path'],
        fileinfo['key_word'],
        fileinfo['sheet'],
        fileinfo['column_used'],
        fileinfo['column_dropna']
    )

    if need_melt:
        melted_data = pd.melt(
            cleaned_data,
            fileinfo['static_column'],
            fileinfo['column_to_transfer'],
            fileinfo['unpivoted_column']        
        )

    exportData = extd.export_to_postgres(
        melted_data if need_melt else cleaned_data,
        customTableName if need_melt else fileinfo['database_table']
    )

def main():
    print("hola")

if __name__ == "__main__":
    main()
