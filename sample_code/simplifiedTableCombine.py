import pandas as pd
import os

# 读取指定文件夹下所有xls/xlsx文件（排除已生成的合并文件）
source_dir = r"d:\Users\Administrator\Desktop\产品条码类别管理20260826"
files = [f for f in os.listdir(source_dir) if f.endswith(('.xls', '.xlsx')) and not f.startswith('merged')]
# 合并所有文件数据
df_merged = pd.concat([pd.read_excel(os.path.join(source_dir, f)) for f in files], ignore_index=True)
# 输出合并后的文件到指定文件夹
df_merged.to_excel(os.path.join(source_dir, 'merged.xlsx'), index=False)