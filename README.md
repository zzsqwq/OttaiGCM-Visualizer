# 血糖曲线可视化工具

这是一个用于绘制每日血糖数据曲线图的工具，可以将连续葡萄糖监测数据以及活动记录直观地展示在同一图表上。

## 功能特点

- 从Excel文件中读取连续葡萄糖监测数据
- 在图表上标注各种活动（如饮食、运动等）
- 显示血糖值的变化趋势
- 提供简洁、直观且美观的数据展示
- 支持命令行参数自定义图表生成
- 支持从CSV文件加载自定义活动注释

## 安装依赖

```bash
# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或者 venv\Scripts\activate  # Windows

# 安装依赖包
pip install pandas matplotlib openpyxl
```

## 使用方法

### 基本用法

```bash
python blood_glucose_visualizer.py
```

这将使用默认参数生成2025年3月17日的血糖曲线图。

### 命令行参数

```bash
python blood_glucose_visualizer.py -d "2025/3/17" -f "OttaiCGM_04E3E5F13CE6.xlsx" -s -a "annotations.csv"
```

参数说明：

- `-d, --date`：指定日期，支持多种日期格式，默认为"2025/3/17"
- `-f, --file`：Excel文件路径，默认为"OttaiCGM_04E3E5F13CE6.xlsx"
- `-o, --output`：输出图像文件名，默认为"血糖曲线_YYYY年MM月DD日.png"
- `-s, --show`：显示图表（不指定此参数则只保存图表而不显示）
- `-a, --annotations`：注释CSV文件路径，用于加载自定义活动注释
- `--create-sample`：创建示例注释CSV文件

### 日期格式支持

支持的日期格式包括：
- YYYY/MM/DD（如2025/3/17）
- YYYY-MM-DD（如2025-3-17）
- YYYY.MM.DD（如2025.3.17）
- YYYY年MM月DD日（如2025年3月17日）
- MM/DD/YYYY（如3/17/2025）
- DD/MM/YYYY（如17/3/2025）
等多种格式

## 数据格式要求

### Excel文件格式

Excel文件应包含以下列：
- `时刻`：时间数据（可以是日期时间格式）
- `血糖值mmol/L`：血糖数值，单位为mmol/L

### 注释CSV文件格式

注释CSV文件应包含以下列：
1. `时间`：活动时间（HH:MM格式，如"12:30"）
2. `活动描述`：对活动的描述文本
3. `Y偏移量`（可选）：调整标注位置的偏移量（数字，如"-0.5"、"0.8"）
4. `日期(可选)`：指定注释适用的日期，用于在同一文件中存储多天的注释

示例CSV文件内容：
```
时间,活动描述,Y偏移量,日期(可选)
10:30,一根玉米肠,0,2025/3/17
12:10,吃饭15分钟，紫米+香干炒肉+番茄炒蛋,0.8,2025/3/17
12:30,散步20min,-0.8,2025/3/17
08:30,早餐：燕麦粥,0.5,2025/3/16
```

## 示例

生成特定日期的血糖曲线图：

```bash
python blood_glucose_visualizer.py -d "2025-03-16"
```

指定输出文件名：

```bash
python blood_glucose_visualizer.py -d "2025/3/17" -o "my_glucose_chart.png"
```

使用不同的数据文件并显示图表：

```bash
python blood_glucose_visualizer.py -f "other_cgm_data.xlsx" -s
```

创建示例注释文件并使用它：

```bash
python blood_glucose_visualizer.py --create-sample
```

指定自定义注释文件：

```bash
python blood_glucose_visualizer.py -d "2025-03-16" -a "my_annotations.csv" -s
```

## 自定义注释

有两种方式添加自定义注释：

1. **使用CSV文件**：创建符合上述格式的CSV文件，然后使用`-a`参数指定
2. **修改代码**：修改代码中的`create_annotations`函数，添加预设的注释

可以通过`--create-sample`参数生成一个示例注释文件，作为创建自己的注释文件的参考。

## 预览

![血糖曲线示例](血糖曲线_2025年3月17日.png)