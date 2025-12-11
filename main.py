from data.file_infomations import FILE_INFOMATION as finfos
from utils.file_processing import fileProcessing
from utils.exportToDatabase import export_to_postgres
from data.returned_data import returned_data_collection
import pandas as pd

# 上传没有经过逆透视的产品编码表
for fileinfo in finfos:
    fileProcessing(fileinfo)

# 上传经过逆透视的迭代编码表
fileProcessing(finfos[0], True, "productid_iteration_unpivoted")

# 处理后上传经过处理的作图顺序表
ordinaryPlotOrder_df = returned_data_collection.get("普通产品作图顺序表")
stosensePlotOrder_df = returned_data_collection.get("stosense作图顺序表")

PlotOrder_df = pd.concat(
    objs=[ordinaryPlotOrder_df, stosensePlotOrder_df],
    axis=0,
    ignore_index=False,
    keys=['normal', 'stosense']
)
PlotOrder_df['产品编号'] = PlotOrder_df['产品编号'].str.upper()
selectedPlotOrder_df = PlotOrder_df[PlotOrder_df['产品编号'].str.contains('I87', na=False)]
export_to_postgres(
    selectedPlotOrder_df,
    "CombinedProductPlotOrder"
)



def main():
    print("hola")

if __name__ == "__main__":
    main()