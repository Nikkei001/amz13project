from data.file_infomations import FILE_INFOMATION as finfos
from utils.file_processing import fileProcessing
from utils.exportToDatabase import export_to_postgres
from data.returned_data import returned_data_collection
import pandas as pd
import numpy as np

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

# 整合各区域产品编码和业务员对应关系
us_productid_df = returned_data_collection.get("Copy美国库存状况")
us_productid_df['国家'] = '美国'
us_stosense_productid_df = returned_data_collection.get("Copy品牌部产品状况")
us_stosense_productid_df['国家'] = '美国'
eu_productid_df = returned_data_collection.get("Copy德国库存状况")
eu_productid_df['国家'] = '德国'
uk_productid_df = returned_data_collection.get("Copy英国库存状况")
uk_productid_df['国家'] = '英国'
ca_productid_df = returned_data_collection.get("Copy加拿大库存状况")
ca_productid_df['国家'] = '加拿大'

all_regions_productid_df = pd.concat(
    objs=[
        us_productid_df,
        us_stosense_productid_df,
        eu_productid_df,
        uk_productid_df,
        ca_productid_df
    ],
    axis=0,
    ignore_index=True
)

all_regions_productid_df['产品系列'] = all_regions_productid_df['产品编号'] + str('系列')
melted_all_regions_productid_df = pd.melt(
    all_regions_productid_df,
    id_vars= ['业务员', '产品系列', '国家'],
    value_vars= ['产品编号', '新产品编号', '新产品编号2', "新产品编号3"],
    value_name= '全部产品编号'
).drop(columns=['variable']).dropna(subset=['全部产品编号'])

extract_productid = melted_all_regions_productid_df['产品系列'].str.extract(r'(.*)系列')[0]

melted_all_regions_productid_df['产品类别'] = np.where(
    extract_productid == melted_all_regions_productid_df['全部产品编号'],
    '老产品',
    '迭代产品'
)

export_to_postgres(
    melted_all_regions_productid_df,
    "AllRegionsProductIDTable"
)


def main():
    print("hola")
    print(returned_data_collection.keys())

if __name__ == "__main__":
    main()