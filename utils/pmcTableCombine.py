import os
import pandas as pd
from pathlib import Path
from.exportToDatabase import export_to_postgres

def merge_new_products():
    # 定义源文件夹路径 (使用原始字符串避免转义问题)
    source_dir = r"D:\Nikkei\learning\CodingProj\amz13project\SourceData\pmc发货表"
    
    # 检查路径是否存在
    if not os.path.exists(source_dir):
        raise FileNotFoundError(f"路径不存在: {source_dir}")
    
    # 获取所有xls文件
    xls_files = [f for f in os.listdir(source_dir) 
                if f.lower().endswith('.xls') and os.path.isfile(os.path.join(source_dir, f))]
    
    if not xls_files:
        raise ValueError(f"未找到任何.xls文件在路径: {source_dir}")
    
    # 存储所有处理后的DataFrame
    all_data = []
    
    for file in xls_files:
        file_path = os.path.join(source_dir, file)
        try:
            # 读取"汇总"sheet
            df = pd.read_excel(file_path, sheet_name='汇总', dtype=str, header=3)
            
            # 处理表头：删除换行符 + 去除前后空格
            df.columns = [col.replace('\n', '').replace('\r', '').strip() 
                          for col in df.columns]
            
            # 选取指定列
            if '产品类型' in df.columns and '产品编号' in df.columns and '站点' in df.columns:
                filtered_df = df[['产品类型', '产品编号', '站点']]
                all_data.append(filtered_df)
            else:
                print(f"警告: 文件 {file} 缺少必要列，已跳过")
                
        except Exception as e:
            print(f"处理文件 {file} 时出错: {str(e)}")
    
    if not all_data:
        raise ValueError("未找到任何符合条件的数据")
    
    # 合并所有DataFrame
    merged_df = pd.concat(all_data, ignore_index=True).drop_duplicates()
    
    # 导出到PostgreSQL数据库
    export_to_postgres(merged_df, "PMCCombinedProducts")
    

# 使用示例
if __name__ == "__main__":
    try:
        result_path = merge_new_products()
        print(f"结果文件已保存至: {result_path}")
    except Exception as e:
        print(f"程序执行失败: {str(e)}")