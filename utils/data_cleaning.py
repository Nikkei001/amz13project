import pandas as pd
from .findSingleDocument import findSingleDocument

def data_cleaning(file_path, key_word, sheet, column_used, column_dropna):
    df = pd.read_excel(
        findSingleDocument(file_path, keyword=key_word),
        sheet_name = sheet,
        usecols = column_used,   
    ).dropna(subset = column_dropna).drop_duplicates()
    df = df.astype(str).apply(lambda x: x.str.strip()).replace(["", "0", "nan"], None)
    return df

def main():
    print("hola")

if __name__ == "__main__":
    main()

