# 读取不同格式的文件，并进行数据清洗
import pandas as pd
from .findSingleDocument import findSingleDocument
from utils.csvEncodingTest import detect_file_encoding

def data_cleaning(file_path, key_word, sheet, column_used, column_dropna):
    fullFilePath = findSingleDocument(file_path, keyword=key_word)
    format = fullFilePath.suffix.lower()
    if format in ['.xls', '.xlsx']:
        df = pd.read_excel(
            fullFilePath,
            sheet_name = sheet,
            usecols = column_used,   
        ).dropna(subset = column_dropna).drop_duplicates()
        df = df.astype(str).apply(lambda x: x.str.strip()).replace(["", "0", "nan"], None)
        return df
    elif format == '.csv':
        df = pd.read_csv(
            fullFilePath,
            usecols = column_used,
            encoding = detect_file_encoding(fullFilePath)
        ).dropna(subset = column_dropna).drop_duplicates()
        df = df.astype(str).apply(lambda x: x.str.strip()).replace(["", "0", "nan"], None)
        return df

def main():
    print(
        'hola'
    )

if __name__ == "__main__":
    main()


