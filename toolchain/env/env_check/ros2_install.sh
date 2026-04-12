#!/bin/bash

# ROS 2 安装脚本 (Ubuntu 24.04 LTS)
# 支持从清华源安装

set -e

echo "=== ROS 2 安装脚本 ==="

# 1. 设置编码
export LC_ALL=C.UTF-8
export LANG=C.UTF-8

# 2. 添加 ROS 2 GPG 密钥
echo "添加 ROS 2 GPG 密钥..."
sudo apt update && sudo apt install -y curl gnupg lsb-release
curl -s https://mirrors.tuna.tsinghua.edu.cn/ros2/ros.key | sudo gpg --dearmor -o /usr/share/keyrings/ros-archive-keyring.gpg

# 3. 添加清华源 ROS 2 仓库
echo "添加清华源 ROS 2 仓库..."
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] https://mirrors.tuna.tsinghua.edu.cn/ros2/ubuntu $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null

# 4. 安装 ROS 2 (Humble Hawksbill)
echo "安装 ROS 2 Humble..."
sudo apt update
sudo apt install -y ros-humble-desktop python3-argcomplete

# 5. 安装常用工具
echo "安装常用工具..."
sudo apt install -y python3-colcon-common-extensions python3-rosdep python3-rosinstall-generator

# 6. 初始化 rosdep
echo "初始化 rosdep..."
sudo rosdep init
rosdep update --include-eol-distros

# 7. 设置环境变量
echo "设置环境变量..."
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
source /opt/ros/humble/setup.bash

# 8. 安装依赖包管理工具
echo "安装依赖包管理工具..."
pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple/ vcstool

echo "=== ROS 2 安装完成 ==="
echo "请运行 'source ~/.bashrc' 或重新打开终端以生效环境变量"