# 导入所需库
import pandas as pd
import matplotlib.pyplot as plt

# ---------------------- 1. 构建数据 ----------------------
# 月度加班时长数据（对应1-12月）
data = {
    '月份': ['1月', '2月', '3月', '4月', '5月', '6月', 
             '7月', '8月', '9月', '10月', '11月', '12月'],
    '加班时长(小时)': [15.33, 27.68, 25.2, 21.18, 20.52, 21.1,
                     40.02, 40.52, 32.85, 27.87, 46.57, 52.83]
}

# 创建Pandas DataFrame（方便后续分析）
df = pd.DataFrame(data)

# ---------------------- 2. 基础数据分析 ----------------------
# 计算12个月平均加班时长
avg_overtime = df['加班时长(小时)'].mean()
print(f"12个月平均加班时长：{avg_overtime:.2f} 小时")
print("\n月度加班时长详情：")
print(df)

# ---------------------- 3. Matplotlib 绘图 ----------------------
# 设置中文字体（避免中文乱码，根据你的系统调整字体名称）
plt.rcParams['font.sans-serif'] = ['SimHei']  # Windows系统
# plt.rcParams['font.sans-serif'] = ['PingFang SC']  # Mac系统
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# 创建画布
fig, ax = plt.subplots(figsize=(10, 6))

# 绘制月度加班时长折线图
ax.plot(df['月份'], df['加班时长(小时)'], 
        marker='o',  # 数据点标记为圆形
        linewidth=2,  # 折线宽度
        color='#1f77b4',  # 折线颜色
        label='月度加班时长')

# 绘制平均加班时长水平虚线
ax.axhline(y=avg_overtime, 
           color='#ff7f0e',  # 虚线颜色
           linestyle='--',  # 虚线样式
           linewidth=1.5,  # 虚线宽度
           label=f'平均时长({avg_overtime:.2f}小时)')

# ---------------------- 4. 图表美化 ----------------------
ax.set_title('2025年月度加班时长统计', fontsize=14, pad=20)  # 标题
ax.set_xlabel('月份', fontsize=12)  # 横坐标标签
ax.set_ylabel('加班时长（小时）', fontsize=12)  # 纵坐标标签
ax.legend(loc='upper left')  # 图例位置
ax.grid(True, alpha=0.3)  # 网格线（透明度0.3）
plt.tight_layout()  # 自动调整布局

# 显示图表
plt.show()

# ---------------------- 可选：保存图表 ----------------------
# plt.savefig('月度加班时长统计图.png', dpi=300, bbox_inches='tight')