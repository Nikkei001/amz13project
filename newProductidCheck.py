import pandas as pd
from utils.findSingleDocument import findSingleDocument
from sqlalchemy import create_engine
import psycopg2

def data_cleaning(df):
    df = df.astype(str).apply(lambda x: x.str.strip()).replace(["", "0", "nan"], None)
    return df

def export_to_postgres(df, table_name):
    """
    Export DataFrame to PostgreSQL database
    
    Args:
        df: pandas DataFrame to export
        table_name: name of the table to create or replace
    """
    # Create connection string
    conn_string = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
    
    # Create SQLAlchemy engine
    engine = create_engine(conn_string)
    
    try:
        # Export DataFrame to PostgreSQL with schema specified
        df.to_sql(table_name, engine, if_exists='replace', index=False, schema=DB_CONFIG['schema'])
        print(f"Data successfully exported to table '{table_name}' in schema '{DB_CONFIG['schema']}' in database '{DB_CONFIG['database']}'")
    except Exception as e:
        print(f"Error exporting data to PostgreSQL: {e}")
    finally:
        engine.dispose()
    
# import excel file whose name contains "copy"
filepath = findSingleDocument(
    r'C:\Users\Administrator\OneDrive\文档\产品库存数量表\产品库存数量表原表\产品库存数量表_原表\原表', 
    'copy'
)
filepath2 = findSingleDocument(
    r'D:\Nikkei\learning\CodingProj\originalFiles\productAndInventoryTableData', 
    '海外仓库存状况统计表导出'
)
productAndInventoryTable = pd.read_excel(
    filepath, 
    sheet_name='美国库存状况',
    usecols=['产品编号', '新产品编号', '新产品编号2', "新产品编号3"]
).dropna(subset=['产品编号'])

findNewProductIDsTable = pd.read_excel(
    filepath2, 
    sheet_name='sheet1',
    usecols=['产品编号', '迭代产品']
).dropna(subset=['产品编号'])

# Remove duplicate rows
findNewProductIDsTable = findNewProductIDsTable.drop_duplicates()

# Convert all columns to string format
productAndInventoryTable = data_cleaning(productAndInventoryTable)
findNewProductIDsTable = data_cleaning(findNewProductIDsTable)

# Database connection parameters - replace with your actual credentials
DB_CONFIG = {
    'host': 'localhost',
    'database': 'postgres',
    'user': 'postgres',
    'password': 'szy520108',
    'port': '5432',
    'schema': 'WorkFlow'  # Change this to your desired schema name
}



def main():
    print("Hello from amz13project!")
    # Export the product inventory data to PostgreSQL
    export_to_postgres(productAndInventoryTable, 'productIDs')
    export_to_postgres(findNewProductIDsTable, 'findNewProductIDs')

if __name__ == "__main__":
    main()