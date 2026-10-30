import os
import polars as pl
import xlsxwriter


def not_blank(col):
    """列非空，且去掉首尾空白后不为空"""
    return pl.col(col).is_not_null() & (pl.col(col).str.strip_chars() != "")


def write_styled_excel(df, output_path):
    """按莫兰迪配色输出带格式的 Excel"""
    # 莫兰迪色系
    header_bg = "#6F7F78"      # 灰绿
    header_font = "#FBFAF7"    # 暖白
    row_bg_1 = "#F7F5F1"       # 暖象牙白
    row_bg_2 = "#EAEEEA"       # 浅灰绿
    border_color = "#D8D4CC"   # 浅灰棕
    text_color = "#3E4742"     # 深灰绿

    workbook = xlsxwriter.Workbook(output_path)
    worksheet = workbook.add_worksheet("Sheet1")

    base_format = {
        "font_name": "微软雅黑",
        "font_size": 10,
        "font_color": text_color,
        "border": 1,
        "border_color": border_color,
        "valign": "vcenter",
    }

    header_format = workbook.add_format({
        **base_format,
        "bold": True,
        "font_size": 11,
        "font_color": header_font,
        "bg_color": header_bg,
        "align": "center",
    })

    align_map = {
        "销售": "center",
        "信息合并": "left",
        "销售确认发货": "right",
        "销售说明发货原因": "left",
        "销量预估": "right",
    }
    width_map = {
        "销售": 10,
        "信息合并": 20,
        "销售确认发货": 15,
        "销售说明发货原因": 48,
        "销量预估": 11,
    }

    row_formats = {}
    for band, bg in ((0, row_bg_1), (1, row_bg_2)):
        for col in df.columns:
            row_formats[(band, col)] = workbook.add_format({
                **base_format,
                "bg_color": bg,
                "align": align_map.get(col, "left"),
                "text_wrap": col == "销售说明发货原因",
                # 这两列强制为文本格式
                "num_format": "@" if col in ("销售确认发货", "销量预估") else "General",
            })

    for j, col in enumerate(df.columns):
        worksheet.set_column(j, j, width_map.get(col, 14))
        worksheet.write_string(0, j, str(col), header_format)
    worksheet.set_row(0, 30)

    reason_idx = df.columns.index("销售说明发货原因") if "销售说明发货原因" in df.columns else -1
    # 这两列为空时按文本 "0" 填充（保留文本格式和绿色角标）
    zero_fill_idx = {
        j for j, c in enumerate(df.columns)
        if c in ("销售确认发货", "销量预估")
    }

    for i in range(df.height):
        band = i % 2
        values = df.row(i)
        # 长文本按列宽估算换行行数
        row_height = 22
        if reason_idx >= 0 and values[reason_idx]:
            lines = max(1, -(-len(str(values[reason_idx])) // 24))
            row_height = max(22, lines * 16 + 6)
        worksheet.set_row(i + 1, row_height)

        for j, value in enumerate(values):
            fmt = row_formats[(band, df.columns[j])]
            if j in zero_fill_idx:
                # 空值或纯空白都填 "0"（字符串，保持文本格式）
                if value is None or str(value).strip() == "":
                    worksheet.write_string(i + 1, j, "0", fmt)
                else:
                    worksheet.write_string(i + 1, j, str(value), fmt)
            elif value is None:
                worksheet.write_blank(i + 1, j, None, fmt)
            else:
                worksheet.write_string(i + 1, j, str(value), fmt)

    worksheet.freeze_panes(1, 0)
    worksheet.autofilter(0, 0, df.height, len(df.columns) - 1)
    worksheet.hide_gridlines(2)
    worksheet.set_tab_color(header_bg)
    workbook.close()


def merge_new_products():
    # ===================== 【核心配置区 - 只改这里】 =====================
    # 源文件夹路径
    source_dir = r"d:\Users\Administrator\Desktop\常用路径\每周_PMC发货表原表收集\XLSX"
    # 表头所在行号（从1开始，默认1=第一行，表头在第2行就填2）
    header_row = 4
    # 需要提取的列（和Excel表头完全一致）
    target_columns = ['销售', '产品编号', '站点', '区域', '销售确认发货','销售说明发货原因','销量预估']
    # 筛选条件（空字典=不筛选）
    # 示例：筛选产品总数量>1，订单单号不为空
    filter_conditions = {
        # "产品总数量": pl.col("产品总数量").cast(pl.Int64) > 1,  # 数字筛选
        # "订单单号": not_blank("订单单号")  # 非空筛选
        "销售确认发货": not_blank("销售确认发货"),
        "销量预估": not_blank("销量预估")
    }
    # 多条件组合方式："and"=且（默认），"or"=或
    filter_logic = "or"
    # 输出文件路径
    output_path = r"d:\Users\Administrator\Desktop\pmc发货表合并结果.xlsx"
    # 读取工作表名称
    sheetName = "汇总"
    # ==================================================================

    # 检查路径
    if not os.path.exists(source_dir):
        raise FileNotFoundError(f"路径不存在: {source_dir}")

    # 获取所有 xls 和 xlsx 文件
    excel_files = [
        f for f in os.listdir(source_dir)
        if f.lower().endswith(('.xls', '.xlsx'))
        and os.path.isfile(os.path.join(source_dir, f))
    ]

    if not excel_files:
        raise ValueError(f"未找到任何xls/xlsx文件在路径: {source_dir}")

    all_data = []
    # 表头行号从0开始计数，转换行号
    header_index = header_row - 1

    for file in excel_files:
        file_path = os.path.join(source_dir, file)
        try:
            print(f"正在读取：{file}")
            # 读取文件：支持自定义表头行，全部按字符串读取（等价 pandas dtype=str）
            df = pl.read_excel(
                file_path,
                sheet_name=sheetName,
                read_options={"header_row": header_index, "dtypes": "string"},
                raise_if_empty=False,
            )

            # 清理表头：删除换行符 + 去空格, 如果出错则跳过处理下一个表头
            try:
                df = df.rename({
                    col: str(col).replace('\n', '').replace('\r', '').strip()
                    for col in df.columns
                })
            except Exception as e:
                print(f"清理表头失败: {str(e)}，已跳过")
                continue

            # 校验必须列是否存在
            if all(col in df.columns for col in target_columns):
                # 提取指定列
                filtered_df = df.select(target_columns)

                # 应用筛选条件（由 filter_logic 控制多条件为"且"或"或"）
                exprs = [
                    expr for col, expr in filter_conditions.items()
                    if col in filtered_df.columns
                ]

                if exprs:
                    combined = exprs[0]
                    for expr in exprs[1:]:
                        combined = combined & expr if filter_logic == "and" else combined | expr
                    filtered_df = filtered_df.filter(combined)

                all_data.append(filtered_df)
            else:
                print(f"警告: {file} 缺少必要列，已跳过")

        except Exception as e:
            print(f"处理文件 {file} 失败: {str(e)}")

    if not all_data:
        raise ValueError("未找到任何符合条件的数据")

    # 合并 + 去重（maintain_order=True 保持与 pandas drop_duplicates 一致的行序）
    merged_df = pl.concat(all_data).unique(maintain_order=True)
    # 合并'产品编号', '站点', '区域'三列为一个新列命名为'信息合并'
    merged_df = merged_df.with_columns(
        pl.concat_str(['产品编号', '站点', '区域'], separator='', ignore_nulls=True).alias('信息合并')
    )
    # 保存结果
    merged_df = merged_df.select(['销售', '信息合并', '销售确认发货', '销售说明发货原因','销量预估'])
    write_styled_excel(merged_df, output_path)
    return output_path

if __name__ == "__main__":
    try:
        result_path = merge_new_products()
        print(f"\n✅ 合并完成！结果保存至: {result_path}")
        print(f"📊 总数据行数: {pl.read_excel(result_path, raise_if_empty=False).height}")
    except Exception as e:
        print(f"\n❌ 执行失败: {str(e)}")
