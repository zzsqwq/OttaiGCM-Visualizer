import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import argparse
import os
import sys
import csv

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 读取Excel数据
def load_glucose_data(file_path, target_date):
    # 读取Excel文件
    df = pd.read_excel(file_path)
    
    # 转换时间列为datetime
    df['时刻'] = pd.to_datetime(df['时刻'])
    
    # 筛选指定日期的数据
    target_date = pd.to_datetime(target_date).date()
    df_filtered = df[df['时刻'].dt.date == target_date]
    
    if df_filtered.empty:
        available_dates = df['时刻'].dt.date.unique()
        print(f"错误: 没有找到 {target_date} 的数据")
        print(f"可用日期: {', '.join([str(d) for d in available_dates])}")
        sys.exit(1)
    
    # 按时间排序
    df_filtered = df_filtered.sort_values('时刻')
    
    return df_filtered

# 从CSV文件加载活动注释
def load_annotations_from_csv(csv_file, date_str=None):
    if not os.path.exists(csv_file):
        print(f"错误: 找不到注释文件 '{csv_file}'")
        return None
    
    annotations = []
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader, None)  # 跳过标题行
            
            for row in reader:
                if len(row) < 2:
                    continue
                    
                time_str = row[0].strip()
                description = row[1].strip()
                
                # 可选的第三列作为y偏移量
                y_offset = 0
                if len(row) > 2 and row[2].strip():
                    try:
                        y_offset = float(row[2])
                    except ValueError:
                        pass
                
                # 如果有日期列（第四列），检查是否匹配目标日期
                if len(row) > 3 and row[3].strip() and date_str:
                    if parse_date(row[3]).date() != parse_date(date_str).date():
                        continue
                
                # 将时间和描述加入注释列表
                annotations.append((time_str, description, y_offset))
        
        return annotations
    except Exception as e:
        print(f"读取CSV文件时出错: {e}")
        return None

# 创建活动注释列表
def create_annotations(date_str, custom_annotations=None, annotations_file=None):
    # 活动注释数据 (时间, 内容, y位置)
    annotations = []
    
    # 解析日期
    base_date = pd.to_datetime(date_str).date()
    
    # 如果提供了注释文件，从文件加载
    if annotations_file:
        csv_annotations = load_annotations_from_csv(annotations_file, date_str)
        if csv_annotations:
            for time_str, text, y_offset in csv_annotations:
                try:
                    time = datetime.strptime(time_str, "%H:%M").time()
                    dt = datetime.combine(base_date, time)
                    annotations.append((dt, text, y_offset))
                except ValueError:
                    print(f"警告: 无法解析时间 '{time_str}'，忽略此注释")
            return annotations
    
    # 如果提供了自定义注释，使用它们
    if custom_annotations:
        for time_str, text in custom_annotations:
            time = datetime.strptime(time_str, "%H:%M").time()
            dt = datetime.combine(base_date, time)
            annotations.append((dt, text, 0))  # 使用默认y偏移量
        return annotations
    
    # 默认注释 - 2025年3月17日
    if base_date == pd.to_datetime("2025/3/17").date():
        annotations.append((datetime.combine(base_date, datetime.strptime("10:30", "%H:%M").time()), "一根玉米肠", 0))
        annotations.append((datetime.combine(base_date, datetime.strptime("12:10", "%H:%M").time()), "吃饭15分钟，紫米+香干炒肉+番茄炒蛋", 0.8))
        annotations.append((datetime.combine(base_date, datetime.strptime("12:30", "%H:%M").time()), "散步20min", -0.8))
        annotations.append((datetime.combine(base_date, datetime.strptime("15:53", "%H:%M").time()), "一包干脆面，一包肉松饼干", 0.5))
        annotations.append((datetime.combine(base_date, datetime.strptime("17:00", "%H:%M").time()), "一根玉米肠", 0))
        annotations.append((datetime.combine(base_date, datetime.strptime("18:20", "%H:%M").time()), "吃饭10分钟，杂粮米+清炒莴笋+葱油手撕鸡", 0.7))
        annotations.append((datetime.combine(base_date, datetime.strptime("18:40", "%H:%M").time()), "散步15min", -0.7))
        annotations.append((datetime.combine(base_date, datetime.strptime("19:05", "%H:%M").time()), "打哈欠，很困", 0.4))
        annotations.append((datetime.combine(base_date, datetime.strptime("21:44", "%H:%M").time()), "椭圆机半小时", -0.4))
        annotations.append((datetime.combine(base_date, datetime.strptime("23:50", "%H:%M").time()), "两包干脆面+两根玉米肠", 0.3, "2025/3/17"))
    else:
        print(f"注意: 没有为 {base_date} 预设注释，图表将不包含活动标记")
    
    return annotations

# 创建示例注释CSV文件
def create_sample_annotations_file():
    filename = "sample_annotations.csv"
    if os.path.exists(filename):
        return filename
    
    with open(filename, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["时间", "活动描述", "Y偏移量", "日期(可选)"])
        writer.writerow(["10:30", "一根玉米肠", "0", "2025/3/17"])
        writer.writerow(["12:10", "吃饭15分钟，紫米+香干炒肉+番茄炒蛋", "0.8", "2025/3/17"])
        writer.writerow(["12:30", "散步20min", "-0.8", "2025/3/17"])
        writer.writerow(["15:53", "一包干脆面，一包肉松饼干", "0.5", "2025/3/17"])
        writer.writerow(["17:00", "一根玉米肠", "0", "2025/3/17"])
        writer.writerow(["18:20", "吃饭10分钟，杂粮米+清炒莴笋+葱油手撕鸡", "0.7", "2025/3/17"])
        writer.writerow(["18:40", "散步15min", "-0.7", "2025/3/17"])
        writer.writerow(["19:05", "打哈欠，很困", "0.4", "2025/3/17"])
        writer.writerow(["21:44", "椭圆机半小时", "-0.4", "2025/3/17"])
        writer.writerow(["23:50", "两包干脆面+两根玉米肠", "0.3", "2025/3/17"])
        writer.writerow(["08:30", "早餐：燕麦粥", "0.5", "2025/3/16"])
        writer.writerow(["12:00", "午餐：米饭+炒青菜+鱼", "0.6", "2025/3/16"])
        writer.writerow(["15:30", "水果：一个苹果", "-0.3", "2025/3/16"])
        writer.writerow(["18:30", "晚餐：面条+豆腐", "0.4", "2025/3/16"])
    
    print(f"已创建示例注释文件: {filename}")
    return filename

# 解析日期字符串的各种格式
def parse_date(date_str):
    # 尝试各种常见的日期格式
    formats = [
        "%Y/%m/%d", "%Y-%m-%d", "%Y.%m.%d",
        "%Y年%m月%d日", "%m/%d/%Y", "%d/%m/%Y",
        "%m-%d-%Y", "%d-%m-%Y"
    ]
    
    for fmt in formats:
        try:
            return pd.to_datetime(date_str, format=fmt)
        except:
            continue
    
    # 如果所有格式都失败，使用pandas默认解析
    try:
        return pd.to_datetime(date_str)
    except:
        print(f"错误: 无法解析日期 '{date_str}'")
        print("请使用以下格式之一: YYYY/MM/DD, YYYY-MM-DD, MM/DD/YYYY, DD/MM/YYYY 等")
        sys.exit(1)

# 绘制血糖曲线图
def plot_glucose_curve(df, annotations, date_str):
    # 更接近参考图的配色方案
    normal_color = '#4a86e8'  # 正常范围的蓝色
    warning_color = '#f39c12'  # 超标范围的黄色（更鲜明的橙色）
    fill_color = '#e8f2fe'  # 浅蓝色填充
    annotation_color = '#e74c3c'  # 鲜红色
    grid_color = '#e6e6e6'  # 浅灰色网格
    
    fig, ax = plt.subplots(figsize=(14, 6))
    fig.patch.set_facecolor('#FFFFFF')  
    ax.set_facecolor('#F9FBFF')  # 更淡的背景色
    
    # 设置临界值
    normal_max = 7.8
    normal_min = 3.9
    
    # 处理数据，确保颜色分界清晰
    # 对每个点根据血糖值决定颜色
    for i in range(1, len(df)):
        x1, y1 = df['时刻'].iloc[i-1], df['血糖值mmol/L'].iloc[i-1]
        x2, y2 = df['时刻'].iloc[i], df['血糖值mmol/L'].iloc[i]
        
        # 检查线段是否穿过参考线(7.8)
        if (y1 <= normal_max and y2 > normal_max) or (y1 > normal_max and y2 <= normal_max):
            # 计算穿过参考线的时间点（线性插值）
            t = (normal_max - y1) / (y2 - y1)
            cross_time = x1 + t * (x2 - x1)
            
            # 绘制参考线以下部分（蓝色）
            if y1 <= normal_max:
                ax.plot([x1, cross_time], [y1, normal_max], color=normal_color, linewidth=2.0, solid_capstyle='round')
                ax.plot([cross_time, x2], [normal_max, y2], color=warning_color, linewidth=2.5, solid_capstyle='round')
            else:
                ax.plot([x1, cross_time], [y1, normal_max], color=warning_color, linewidth=2.5, solid_capstyle='round')
                ax.plot([cross_time, x2], [normal_max, y2], color=normal_color, linewidth=2.0, solid_capstyle='round')
        else:
            # 整个线段使用同一颜色
            if y1 > normal_max or y2 > normal_max:
                color = warning_color
                linewidth = 2.5
            else:
                color = normal_color
                linewidth = 2.0
            
            ax.plot([x1, x2], [y1, y2], color=color, linewidth=linewidth, solid_capstyle='round')
    
    # 填充背景颜色 - 使用统一的填充色
    ax.fill_between(df['时刻'], 0, df['血糖值mmol/L'], color=fill_color, alpha=0.65)
    
    # 设置坐标轴范围
    date = pd.to_datetime(date_str).date()
    ax.set_xlim([datetime.combine(date, datetime.min.time()), 
                 datetime.combine(date + timedelta(days=1), datetime.min.time())])
    
    # 设置坐标轴格式
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=6))
    ax.xaxis.set_minor_locator(mdates.HourLocator())
    
    # 血糖值最大最小范围
    min_glucose = max(0, min(3.5, df['血糖值mmol/L'].min() - 0.5))  # 确保显示完整参考区间
    max_glucose = df['血糖值mmol/L'].max() + 3.5  # 增加一点顶部空间用于标注
    ax.set_ylim([min_glucose, max_glucose])
    
    # 添加参考区间指示线 - 更明显的样式
    ax.axhline(y=normal_min, color='#95a5a6', linestyle='--', linewidth=1.2, alpha=0.8)
    ax.axhline(y=normal_max, color=warning_color, linestyle='--', linewidth=1.2, alpha=0.8)
    
    # 添加参考区间文本标注 - 添加更详细的说明
    ax.text(datetime.combine(date, datetime.strptime("00:15", "%H:%M").time()), 
            normal_min - 0.2, f"{normal_min} mmol/L (下限)", 
            fontsize=9, color='#555555', ha='left', va='top')
    
    ax.text(datetime.combine(date, datetime.strptime("00:15", "%H:%M").time()), 
            normal_max + 0.2, f"{normal_max} mmol/L (上限)", 
            fontsize=9, color=warning_color, ha='left', va='bottom')
    
    # 添加图例
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], color=normal_color, lw=2, label='正常范围'),
        Line2D([0], [0], color=warning_color, lw=2, label='超出正常范围')
    ]
    ax.legend(handles=legend_elements, loc='upper left', frameon=True, 
              facecolor='white', edgecolor='#DDDDDD', fontsize=9)
    
    # 美化轴和边框
    for spine in ax.spines.values():
        spine.set_color('#DDDDDD')
        spine.set_linewidth(0.5)
    
    # 测量数据点在图上的实际位置
    trans = ax.transData
    
    # 获取每个时间点对应的血糖值
    time_to_glucose = {}
    for dt, text, y_offset in annotations:
        if dt in df['时刻'].values:
            idx = df[df['时刻'] == dt].index[0]
            glucose_value = df.loc[idx, '血糖值mmol/L']
        else:
            nearest_idx = (df['时刻'] - dt).abs().idxmin()
            glucose_value = df.loc[nearest_idx, '血糖值mmol/L']
        time_to_glucose[dt] = glucose_value
    
    # 获取图表尺寸的大小，用于计算相对偏移
    fig_width_px = fig.get_figwidth() * fig.dpi
    fig_height_px = fig.get_figheight() * fig.dpi
    
    # 重写标注布局算法，完全消除重叠
    all_annotations = []
    for dt, text, y_offset in annotations:
        all_annotations.append((dt, text, y_offset))
    
    # 按时间排序所有标注
    all_annotations.sort(key=lambda x: x[0])
    
    # 跟踪已经使用的区域
    used_regions = []  # 存储 (x_min, x_max, y_min, y_max) 的元组
    
    # 用于存储每个时间段的标注计数
    hour_counts = {}
    
    # 处理所有标注
    for dt, text, custom_offset in all_annotations:
        glucose_value = time_to_glucose[dt]
        
        # 获取当前时间的小时
        hour = dt.hour
        if hour not in hour_counts:
            hour_counts[hour] = 0
        
        # 计算基础位置
        point = (mdates.date2num(dt), glucose_value)
        
        # 决定标注方向（上/下），基于奇偶小时来保持视觉平衡
        # 但会被自定义偏移量覆盖
        if custom_offset > 0:
            direction = 1  # 向上
        elif custom_offset < 0:
            direction = -1  # 向下
        else:
            # 无自定义偏移时，使用奇偶规则
            direction = 1 if hour % 2 == 0 else -1
        
        # 根据自定义偏移和时间点计算垂直偏移 - 增加基础偏移量
        base_offset = 1.5  # 增加基础偏移从1.0到1.5
        
        # 同一小时的标注数量增加，偏移量增加
        count_in_hour = hour_counts[hour]
        hour_counts[hour] += 1
        
        # 调整垂直偏移
        if custom_offset != 0:
            # 使用自定义偏移但确保最小距离
            y_offset = custom_offset * 1.5  # 增大自定义偏移的影响
        else:
            # 根据同一小时的标注数量和方向计算偏移
            y_offset = direction * (base_offset + count_in_hour * 0.5)  # 增加梯度从0.25到0.5
        
        # 限制最大偏移
        max_offset = 3.0  # 增加最大偏移允许更多间距
        min_offset = 1.0 * direction  # 确保最小偏移
        if direction > 0:
            y_offset = max(min(y_offset, max_offset), min_offset)
        else:
            y_offset = min(max(y_offset, -max_offset), min_offset)
        
        # 计算水平偏移（使用文本长度作为参考）
        text_length = len(text)
        
        # 基于文本长度的水平偏移，让长文本有更多偏移
        x_offset = 0
        if count_in_hour > 0:
            # 奇偶交替水平偏移
            if count_in_hour % 2 == 0:
                x_offset = -0.05 * min(text_length, 15)  # 限制最大偏移
            else:
                x_offset = 0.05 * min(text_length, 15)
        
        # 计算文本长度的估计宽度（像素）
        # 中文字符通常比英文宽，约为英文的1.7倍
        chinese_chars = sum(1 for c in text if ord(c) > 256)
        english_chars = len(text) - chinese_chars
        text_width_px = (chinese_chars * 10 + english_chars * 6) * 0.9  # 估计像素宽度
        
        # 坐标转换与检测重叠
        display_point = trans.transform(point)
        
        # 初始文本位置 - 增加垂直偏移倍数
        text_x = display_point[0] + x_offset * 20  # 水平像素偏移
        text_y = display_point[1] + y_offset * 40  # 增加垂直偏移像素从30到40
        
        # 计算文本框的估计高度（像素）
        text_height_px = 20  # 估计高度
        
        # 定义文本框的边界
        x_min = text_x - text_width_px/2 - 5  # 左边界（额外留5像素边距）
        x_max = text_x + text_width_px/2 + 5  # 右边界
        y_min = text_y - text_height_px/2 - 5  # 下边界
        y_max = text_y + text_height_px/2 + 5  # 上边界
        
        # 检查并调整，避免与已有标注重叠
        max_attempts = 8  # 最大尝试次数
        attempt = 0
        original_y = text_y  # 保存原始垂直位置
        
        # 定义检查重叠的函数
        def has_overlap(region1, regions):
            x1_min, x1_max, y1_min, y1_max = region1
            for x2_min, x2_max, y2_min, y2_max in regions:
                # 检查两个矩形是否重叠
                if (x1_min < x2_max and x1_max > x2_min and
                    y1_min < y2_max and y1_max > y2_min):
                    return True
            return False
        
        new_region = (x_min, x_max, y_min, y_max)
        while attempt < max_attempts and has_overlap(new_region, used_regions):
            attempt += 1
            
            # 尝试垂直移动
            offset_sign = 1 if attempt % 2 == 0 else -1  # 上下交替尝试
            offset_magnitude = (attempt // 2 + 1) * 15  # 每次增加偏移量
            
            # 应用新的垂直偏移
            text_y = original_y + offset_sign * offset_magnitude
            
            # 更新区域边界
            y_min = text_y - text_height_px/2 - 5
            y_max = text_y + text_height_px/2 + 5
            new_region = (x_min, x_max, y_min, y_max)
        
        # 添加到已使用区域
        used_regions.append(new_region)
        
        # 转回数据坐标
        inv_trans = ax.transData.inverted()
        text_point = inv_trans.transform((text_x, text_y))
        
        # 计算箭头弯曲方向
        if text_point[1] > glucose_value:
            # 标注在血糖值上方
            arc_direction = 0.1
        else:
            # 标注在血糖值下方
            arc_direction = -0.1
            
        # 箭头样式 - 更改箭头属性增加可见度
        arrow_props = dict(
            arrowstyle='-|>',
            shrinkA=0,  # 不减少起点
            shrinkB=3,  # 减小终点压缩
            color=annotation_color,
            linewidth=1.2,  # 增加线宽
            connectionstyle=f'arc3,rad={arc_direction * 1.5}'  # 增加弯曲程度
        )
        
        # 文本框样式 - 参考图样式（无边框）
        bbox_props = dict(
            boxstyle='round,pad=0.3',
            fc='white',
            ec='white',
            alpha=0.95
        )
        
        # 添加标注
        ax.annotate(
            f"{dt.strftime('%H:%M')} {text}",
            xy=point,
            xytext=text_point,
            arrowprops=arrow_props,
            ha='center',
            va='center',
            bbox=bbox_props,
            color=annotation_color,
            fontsize=9,
            weight='normal'
        )
    
    # 设置标题和标签
    formatted_date = date.strftime("%Y年%m月%d日")
    plt.title(f"每日血糖曲线({formatted_date})", fontsize=15, color="#333333", fontweight='bold')
    plt.xlabel("")
    plt.ylabel("mmol/L", color="#555555")
    
    # 网格 - 更淡的虚线，参考图样式
    plt.grid(True, color=grid_color, linestyle='--', linewidth=0.5, alpha=0.7)
    
    # 美化刻度
    ax.tick_params(colors='#999999', labelsize=9)
    
    # 自动调整布局
    plt.tight_layout()
    
    return fig

def main():
    # 设置命令行参数
    parser = argparse.ArgumentParser(description='绘制每日血糖曲线图')
    parser.add_argument('-d', '--date', type=str, default="2025/3/17",
                        help='日期 (默认: 2025/3/17)')
    parser.add_argument('-f', '--file', type=str, default='OttaiCGM_04E3E5F13CE6.xlsx',
                        help='Excel文件路径 (默认: OttaiCGM_04E3E5F13CE6.xlsx)')
    parser.add_argument('-o', '--output', type=str, default=None,
                        help='输出图像文件名 (默认: 血糖曲线_YYYY年MM月DD日.png)')
    parser.add_argument('-s', '--show', action='store_true',
                        help='显示图表 (默认: False)')
    parser.add_argument('-a', '--annotations', type=str, default=None,
                        help='注释CSV文件路径')
    parser.add_argument('--create-sample', action='store_true',
                        help='创建示例注释CSV文件')
    
    args = parser.parse_args()
    
    # 创建示例注释文件
    if args.create_sample:
        create_sample_annotations_file()
        if not args.annotations:
            args.annotations = "sample_annotations.csv"
    
    # 解析日期
    target_date = parse_date(args.date)
    date_str = target_date.strftime("%Y/%m/%d")
    
    # 检查文件是否存在
    if not os.path.exists(args.file):
        print(f"错误: 找不到文件 '{args.file}'")
        sys.exit(1)
    
    # 加载数据
    df = load_glucose_data(args.file, target_date)
    
    # 创建注释
    annotations = create_annotations(date_str, annotations_file=args.annotations)
    
    # 绘制图表
    fig = plot_glucose_curve(df, annotations, date_str)
    
    # 设置输出文件名
    if args.output:
        output_file = args.output
    else:
        formatted_date = target_date.strftime("%Y年%m月%d日")
        output_file = f'血糖曲线_{formatted_date}.png'
    
    # 保存图表
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"图表已保存为: {output_file}")
    
    # 显示图表
    if args.show:
        plt.show()

if __name__ == "__main__":
    main()