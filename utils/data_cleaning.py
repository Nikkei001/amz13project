"""
Data Cleaning Module for Product-Related Excel Datasets
This module provides functions to process Excel files (typically containing productID data):
1. Locate target Excel files via keyword matching
2. Read specified worksheets/columns
3. Remove missing values & duplicate rows
4. Format data (string conversion, whitespace stripping, invalid value replacement)
It’s designed to prepare clean data for subsequent tasks (e.g., productID iteration tracking).
"""
import pandas as pd
from .findSingleDocument import findSingleDocument

def data_cleaning(file_path, key_word, sheet, column_used, column_dropna):
    """
    Cleans product-related data from target Excel files
    
    Args:
        file_path (str): Directory/file path where the target Excel is stored
        key_word (str): Keyword to locate the target Excel via `findSingleDocument`
        sheet (str): Name of the worksheet to read from the Excel file
        column_used (list): List of columns (names/indexes) to retain from the worksheet
        column_dropna (str): Column to check for missing values (rows with NaN here will be removed)
    
    Returns:
        pandas.DataFrame: Cleaned DataFrame (no missing/duplicate rows, formatted values)
    """
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

