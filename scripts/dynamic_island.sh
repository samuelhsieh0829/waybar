#!/bin/bash

# 抓滑鼠位置
read x y < <(hyprctl -j cursorpos | jq -r '[.x, .y] | @tsv')
active_window=$(hyprctl activewindow -j | jq -r '.class + " - " + .title' | cut -c1-60)
# echo "x: $x, y: $y"
x1=860
x2=1160
y1=11
y2=50
# 判斷是否在區域內
if [[ $x -ge $x1 && $x -le $x2 && $y -ge $y1 && $y -le $y2 ]]; then
    # 在區域內，顯示動態島
    echo $(python3 /home/samuel/.config/waybar/scripts/dynamic_island.py)
else
    # 不在區域內，顯示空白
    echo "$active_window"
fi