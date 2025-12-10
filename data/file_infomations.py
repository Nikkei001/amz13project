# static_column -- 逆透视中不变的列
# column_to_transfer -- 准备逆透视的列
# unpivoted_column -- 逆透视后的列
FILE_INFOMATION = [
    {
        'file_path': r'C:\Users\Administrator\OneDrive\文档\产品库存数量表\产品库存数量表原表\产品库存数量表_原表\原表',
        'key_word': 'copy',
        'sheet': '美国库存状况',
        'column_used': ['产品编号', '新产品编号', '新产品编号2', "新产品编号3"],
        'column_dropna': ['产品编号'],
        'database_table': 'productIDs',
        'static_column': ['产品编号'],
        'column_to_transfer': ['新产品编号', '新产品编号2', "新产品编号3"],
        'unpivoted_column': '迭代编码'
    },
    {
        'file_path': r'D:\Nikkei\learning\CodingProj\originalFiles\productAndInventoryTableData',
        'key_word': '海外仓库存状况统计表导出',
        'sheet': 'sheet1',
        'column_used': ['产品编号', '迭代产品'],
        'column_dropna': ['产品编号'],
        'database_table': 'findNewProductIDs',
        'static_column': [],
        'column_to_transfer': "",
        'unpivoted_column': []
    }
]

def main():
    print("hola")

if __name__ == "__main__":
    main()