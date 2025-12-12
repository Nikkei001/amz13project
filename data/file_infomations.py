# static_column -- 逆透视中不变的列
# column_to_transfer -- 准备逆透视的列
# unpivoted_column -- 逆透视后的列
FILE_INFOMATION = [
    {
        'file_path': r'./SourceData',
        'key_word': 'copy',
        'sheet': '美国库存状况',
        'column_used': ['业务员', '产品编号', '新产品编号', '新产品编号2', '新产品编号3'],
        'column_dropna': ['产品编号'],
        'database_table': 'productIDs',
        'static_column': ['业务员', '产品编号'],
        'column_to_transfer': ['新产品编号', '新产品编号2', "新产品编号3"],
        'unpivoted_column': '迭代编码',
        'export_to_database': True
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
        'unpivoted_column': "",
        'export_to_database': True
    },
    {
        'file_path': r'D:\Nikkei\learning\CodingProj\originalFiles\productAndInventoryTableData',
        'key_word': '普通产品作图顺序表',
        'sheet': '',
        'column_used': ['产品编号', '上架时间', '销售', '销售(欧洲)'], 
        'column_dropna': ['产品编号'],
        'database_table': 'OrdinaryProductPlotOrder',
        'static_column': [],
        'column_to_transfer': "",
        'unpivoted_column': "",
        'export_to_database': False
    },
    {
        'file_path': r'D:\Nikkei\learning\CodingProj\originalFiles\productAndInventoryTableData',
        'key_word': 'stosense作图顺序表',
        'sheet': '',
        'column_used': ['产品编号', '上架时间', '销售', '销售(欧洲)'], 
        'column_dropna': ['产品编号'],
        'database_table': 'StosenseProductPlotOrder',
        'static_column': [],
        'column_to_transfer': "",
        'unpivoted_column': "",
        'export_to_database': False
    },
    {
       'file_path': r'./SourceData',
        'key_word': 'Copy',
        'sheet': '美国库存状况',
        'column_used': ['业务员', '产品编号', '新产品编号', '新产品编号2', '新产品编号3'],
        'column_dropna': ['产品编号'],
        'database_table': 'productIDs',
        'static_column': ['业务员', '产品编号'],
        'column_to_transfer': ['新产品编号', '新产品编号2', "新产品编号3"],
        'unpivoted_column': '迭代编码',
        'export_to_database': False 
    },
    {
        'file_path': r'./SourceData',
        'key_word': 'Copy',
        'sheet': '品牌部产品状况',
        'column_used': ['业务员', '产品编号', '新产品编号', '新产品编号2', '新产品编号3'],
        'column_dropna': ['产品编号'],
        'database_table': 'productIDs',
        'static_column': ['业务员', '产品编号'],
        'column_to_transfer': ['新产品编号', '新产品编号2', "新产品编号3"],
        'unpivoted_column': '迭代编码',
        'export_to_database': False 
    },
    {
        'file_path': r'./SourceData',
        'key_word': 'Copy',
        'sheet': '德国库存状况',
        'column_used': ['业务员', '产品编号', '新产品编号', '新产品编号2', '新产品编号3'],
        'column_dropna': ['产品编号'],
        'database_table': 'productIDs',
        'static_column': ['业务员', '产品编号'],
        'column_to_transfer': ['新产品编号', '新产品编号2', "新产品编号3"],
        'unpivoted_column': '迭代编码',
        'export_to_database': False 
    },
    {
        'file_path': r'./SourceData',
        'key_word': 'Copy',
        'sheet': '英国库存状况',
        'column_used': ['业务员', '产品编号', '新产品编号', '新产品编号2', '新产品编号3'],
        'column_dropna': ['产品编号'],
        'database_table': 'productIDs',
        'static_column': ['业务员', '产品编号'],
        'column_to_transfer': ['新产品编号', '新产品编号2', "新产品编号3"],
        'unpivoted_column': '迭代编码',
        'export_to_database': False 
    },
    {
        'file_path': r'./SourceData',
        'key_word': 'Copy',
        'sheet': '加拿大库存状况',
        'column_used': ['业务员', '产品编号', '新产品编号', '新产品编号2', '新产品编号3'],
        'column_dropna': ['产品编号'],
        'database_table': 'productIDs',
        'static_column': ['业务员', '产品编号'],
        'column_to_transfer': ['新产品编号', '新产品编号2', "新产品编号3"],
        'unpivoted_column': '迭代编码',
        'export_to_database': False
    }
]

def main():
    print("hola")

if __name__ == "__main__":
    main()