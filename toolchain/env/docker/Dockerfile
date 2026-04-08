FROM tuna/ubuntu:24.04

# 设置环境变量，避免交互式安装
ENV DEBIAN_FRONTEND=noninteractive

# 更新包列表并安装必要工具
RUN apt-get update && \
    apt-get install -y wget curl bzip2 ca-certificates && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 下载并安装Anaconda3 2024.02版本
RUN wget https://mirrors.tuna.tsinghua.edu.cn/anaconda/archive/Anaconda3-2024.02-Linux-x86_64.sh -O /tmp/anaconda.sh && \
    bash /tmp/anaconda.sh -b -p /opt/anaconda3 && \
    rm /tmp/anaconda.sh

# 初始化conda并设置环境变量
ENV PATH="/opt/anaconda3/bin:${PATH}"

# 验证安装
RUN conda --version && python --version

# 设置工作目录
WORKDIR /workspace