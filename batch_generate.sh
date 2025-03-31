#!/bin/bash

# 生成一系列日期的血糖曲线图表
# 从2025年3月16日到2025年3月29日

# 设置基础变量
DATA_FILE="data/OttaiCGM_20250330.xlsx"
OUTPUT_DIR="images"
ANNOTATIONS_DIR="annotations"

# 确保输出目录存在
mkdir -p $OUTPUT_DIR
mkdir -p $ANNOTATIONS_DIR

# 判断操作系统类型并设置相应的日期处理方式
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS 系统
    # 直接列出所有日期，避免使用日期计算
    DATES=(
        "2025/03/16" "20250316"
        "2025/03/17" "20250317"
        "2025/03/18" "20250318"
        "2025/03/19" "20250319"
        "2025/03/20" "20250320"
        "2025/03/21" "20250321"
        "2025/03/22" "20250322"
        "2025/03/23" "20250323"
        "2025/03/24" "20250324"
        "2025/03/25" "20250325"
        "2025/03/26" "20250326"
        "2025/03/27" "20250327"
        "2025/03/28" "20250328"
        "2025/03/29" "20250329"
    )
    
    # 遍历日期数组
    for ((i=0; i<${#DATES[@]}; i+=2)); do
        current_date="${DATES[i]}"
        formatted_date="${DATES[i+1]}"
        
        # 检查该日期的注释文件是否存在
        annotation_file="${ANNOTATIONS_DIR}/annotations-${formatted_date}.csv"
        annotation_param=""
        if [ -f "$annotation_file" ]; then
            annotation_param="$annotation_file"
        else
            echo "注释文件 $annotation_file 不存在，将不使用注释"
        fi
        
        # 构建并执行命令
        cmd="python3 visualizer.py -d $current_date -f $DATA_FILE"
        if [ -n "$annotation_param" ]; then
            cmd="$cmd -a $annotation_param"
        fi
        cmd="$cmd --peaks --image-dir $OUTPUT_DIR"
        
        echo "执行: $cmd"
        eval $cmd
        
        # 输出成功消息
        echo "已生成 $current_date 的血糖曲线图表"
        echo "------------------------"
    done
else
    # Linux 系统
    # 日期范围
    START_DATE="2025-03-16"
    END_DATE="2025-03-29"

    # 转换日期为秒，用于日期计算
    start_seconds=$(date -d "$START_DATE" +%s)
    end_seconds=$(date -d "$END_DATE" +%s)
    day_seconds=$((60*60*24)) # 一天的秒数

    # 遍历日期范围内的每一天
    current_seconds=$start_seconds
    while [ $current_seconds -le $end_seconds ]; do
        # 格式化当前日期
        current_date=$(date -d @$current_seconds +%Y/%m/%d)
        formatted_date=$(date -d @$current_seconds +%Y%m%d)
        
        # 检查该日期的注释文件是否存在
        annotation_file="${ANNOTATIONS_DIR}/annotations-${formatted_date}.csv"
        annotation_param=""
        if [ -f "$annotation_file" ]; then
            annotation_param="$annotation_file"
        else
            echo "注释文件 $annotation_file 不存在，将不使用注释"
        fi
        
        # 构建并执行命令
        cmd="python3 visualizer.py -d $current_date -f $DATA_FILE"
        if [ -n "$annotation_param" ]; then
            cmd="$cmd -a $annotation_param"
        fi
        cmd="$cmd --peaks --image-dir $OUTPUT_DIR"
        
        echo "执行: $cmd"
        eval $cmd
        
        # 输出成功消息
        echo "已生成 $current_date 的血糖曲线图表"
        echo "------------------------"
        
        # 增加一天
        current_seconds=$((current_seconds + day_seconds))
    done
fi

echo "所有图表生成完成！可在 $OUTPUT_DIR 目录查看结果"