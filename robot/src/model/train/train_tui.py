#!/usr/bin/env python3
"""
YOLOv26 训练工具 - TUI 版本
基于 Rich 库实现终端图形化训练界面
"""
import sys
import os
import threading
import re
from pathlib import Path

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from trainer import YOLOTrainer
from utils import check_gpu, get_optimal_batch_size

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, IntPrompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.layout import Layout
from rich.live import Live
from rich.text import Text
from rich.align import Align
from rich import box

console = Console()


class YOLOTrainingTUI:
    """YOLOv26 训练 TUI 交互界面"""

    def __init__(self):
        self.config = {
            'model_name': 'yolo26n.pt',
            'data_yaml': './src/datasets/coco/yolosets/data.yaml',
            'epochs': 100,
            'batch': 16,
            'imgsz': 640,
            'device': 0,
            'workers': 8,
            'project': './src/model/model_root',
        }
        self.trainer = None
        self.training_thread = None
        self.is_training = False

    def show_banner(self):
        """显示程序横幅"""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║     ██╗   ██╗ ██████╗ ██╗  ██╗   ██╗██████╗   ██████╗       ║
║     ╚██╗ ██╔╝██╔═══██╗██║  ╚██╗ ██╔╝╚════██╗ ██╔═══██╗      ║
║      ╚████╔╝ ██║   ██║██║   ╚████╔╝  █████╔╝ ██║   ██║      ║
║       ╚██╔╝  ██║   ██║██║    ╚██╔╝  ██╔═══╝  ██║   ██║      ║
║        ██║   ╚██████╔╝███████╗ ██║   ███████╗╚██████╔╝      ║
║        ╚═╝    ╚═════╝ ╚══════╝ ╚═╝   ╚══════╝ ╚═════╝       ║
║                                                              ║
║                    YOLOv26 训练工具 v1.0                     ║
╚══════════════════════════════════════════════════════════════╝
        """
        console.print(Align.center(Text(banner, style="bold cyan")), style="bold cyan")

    def show_gpu_info(self):
        """显示 GPU 信息"""
        has_gpu, name, memory = check_gpu()
        if has_gpu:
            info = f"🎮 GPU: {name} | 显存: {memory:.1f} GB | 可用: ✅"
            console.print(Panel(info, title="硬件检测", border_style="green"))
        else:
            console.print(Panel("⚠️ GPU 不可用，将使用 CPU 训练（速度较慢）", title="硬件检测", border_style="yellow"))
        return has_gpu, memory

    def configure_training(self, gpu_memory: float = 8.0):
        """交互式配置训练参数"""
        console.print("\n[bold yellow]📝 训练参数配置[/bold yellow]")
        console.print("-" * 50)

        # ========== 模型选项（已修正任务类型描述） ==========
        model_options = {
            '1':  ('yolo26n.pt',   'Detection Nano',               '最快，最低显存'),
            '2':  ('yolo26s.pt',   'Detection Small',              '速度与精度平衡，推荐'),
            '3':  ('yolo26m.pt',   'Detection Medium',             '更高精度，需更多显存'),
            '4':  ('yolo26l.pt',   'Detection Large',              '高精度，显存要求高'),
            '5':  ('yolo26x.pt',   'Detection Extra Large',        '最高精度，速度较慢'),
            '6':  ('yolo26n-seg.pt', 'Instance Segmentation Nano', '最快，最低显存'),
            '7':  ('yolo26s-seg.pt', 'Instance Segmentation Small','速度与精度平衡，推荐'),
            '8':  ('yolo26m-seg.pt', 'Instance Segmentation Medium','更高精度，需更多显存'),
            '9':  ('yolo26l-seg.pt', 'Instance Segmentation Large', '高精度，专业级设备'),
            '10': ('yolo26x-seg.pt', 'Instance Segmentation Extra Large','最高精度，速度较慢'),
            '11': ('yolo26n-sem.pt', 'Semantic Segmentation Nano', '最快，最低显存'),
            '12': ('yolo26s-sem.pt', 'Semantic Segmentation Small','速度与精度平衡，推荐'),
            '13': ('yolo26m-sem.pt', 'Semantic Segmentation Medium','更高精度，需更多显存'),
            '14': ('yolo26l-sem.pt', 'Semantic Segmentation Large', '高精度，专业级设备'),
            '15': ('yolo26x-sem.pt', 'Semantic Segmentation Extra Large','最高精度，速度较慢')
        }

        model_table = Table(title="可用模型", box=box.ROUNDED)
        model_table.add_column("序号", style="cyan")
        model_table.add_column("模型", style="green")
        model_table.add_column("特点", style="white")
        for key, (name, size, desc) in model_options.items():
            model_table.add_row(key, f"{size} ({name})", desc)
        console.print(model_table)

        # 动态生成可选项（'1' 到 '15'）
        valid_choices = list(model_options.keys())
        choice = Prompt.ask("请选择模型", choices=valid_choices, default='2')
        self.config['model_name'] = model_options[choice][0]

        # 数据集路径
        default_data = self.config['data_yaml']
        data_path = Prompt.ask("数据集配置文件路径", default=default_data)
        self.config['data_yaml'] = data_path

        # 训练轮数
        self.config['epochs'] = IntPrompt.ask("训练轮数 (epochs)", default=100)

        # Batch Size（根据显存推荐）
        # 从模型名称中提取尺寸标识 (n/s/m/l/x)
        model_name = self.config['model_name']
        match = re.search(r'yolo26([nsmlx])', model_name)
        size_char = match.group(1) if match else 's'  # 默认 's'
        suggested_batch = get_optimal_batch_size(gpu_memory, size_char)
        self.config['batch'] = IntPrompt.ask("批次大小 (batch)", default=suggested_batch)

        # 图像尺寸
        self.config['imgsz'] = IntPrompt.ask("输入图像尺寸 (imgsz, 32的倍数)", default=640)

        # 数据加载线程
        self.config['workers'] = IntPrompt.ask("数据加载线程数 (workers)", default=8)

        # 实验名称
        exp_name = Prompt.ask("实验名称 (留空自动生成)", default="")
        if exp_name:
            self.config['name'] = exp_name

        self.show_config_summary()

    def show_config_summary(self):
        """显示配置摘要"""
        table = Table(title="训练配置摘要", box=box.ROUNDED)
        table.add_column("参数", style="cyan")
        table.add_column("值", style="green")

        table.add_row("模型", self.config['model_name'])
        table.add_row("数据集", self.config['data_yaml'])
        table.add_row("训练轮数", str(self.config['epochs']))
        table.add_row("批次大小", str(self.config['batch']))
        table.add_row("图像尺寸", str(self.config['imgsz']))
        table.add_row("GPU 设备", f"cuda:{self.config['device']}" if torch.cuda.is_available() else "cpu")
        table.add_row("数据线程", str(self.config['workers']))
        table.add_row("保存目录", f"{self.config['project']}")

        console.print(table)

        if not Confirm.ask("\n确认开始训练？", default=True):
            console.print("[red]训练已取消[/red]")
            sys.exit(0)

    def start_training(self):
        """启动训练"""
        console.print("\n[bold green]🚀 开始训练 YOLOv26 模型...[/bold green]\n")

        # 创建训练器实例
        self.trainer = YOLOTrainer(
            model_name=self.config['model_name'],
            data_yaml=self.config['data_yaml'],
            epochs=self.config['epochs'],
            batch=self.config['batch'],
            imgsz=self.config['imgsz'],
            device=self.config['device'],
            workers=self.config['workers'],
            project=self.config['project'],
            name=self.config.get('name')
        )

        # 使用 Progress 显示训练进度
        with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TimeElapsedColumn(),
                console=console,
                transient=False,
        ) as progress:
            task = progress.add_task("[cyan]训练中...", total=self.config['epochs'])

            # 在后台线程中运行训练
            def run_training():
                try:
                    self.trainer.train()
                except Exception as e:
                    console.print(f"[red]训练出错: {e}[/red]")

            training_thread = threading.Thread(target=run_training)
            training_thread.start()

            # 模拟进度更新（实际训练中可通过回调更新）
            import time
            for epoch in range(1, self.config['epochs'] + 1):
                time.sleep(0.5)  # 模拟训练过程
                progress.update(task, advance=1)

            training_thread.join()

        # 训练完成后的处理
        console.print("\n[bold green]✅ 训练完成！[/bold green]")

        # 导出训练结果 CSV
        csv_path = self.trainer.export_csv()
        console.print(f"📊 训练结果已保存至: {csv_path}")

        # 显示结果摘要
        self.show_results()

    def show_results(self):
        """显示训练结果摘要"""
        import pandas as pd

        results_path = os.path.join(self.config['project'],
                                    self.trainer.name if hasattr(self.trainer, 'name') else 'yolo26',
                                    'results.csv')

        if os.path.exists(results_path):
            df = pd.read_csv(results_path)
            if len(df) > 0:
                latest = df.iloc[-1]

                result_table = Table(title="训练结果摘要", box=box.ROUNDED)
                result_table.add_column("指标", style="cyan")
                result_table.add_column("最终值", style="green")

                if 'metrics/mAP50(B)' in latest:
                    result_table.add_row("mAP@0.5", f"{latest['metrics/mAP50(B)']:.4f}")
                if 'metrics/mAP50-95(B)' in latest:
                    result_table.add_row("mAP@0.5:0.95", f"{latest['metrics/mAP50-95(B)']:.4f}")
                if 'metrics/precision(B)' in latest:
                    result_table.add_row("Precision", f"{latest['metrics/precision(B)']:.4f}")
                if 'metrics/recall(B)' in latest:
                    result_table.add_row("Recall", f"{latest['metrics/recall(B)']:.4f}")

                console.print(result_table)

    def run(self):
        """运行主程序"""
        self.show_banner()

        # 检查 GPU
        has_gpu, gpu_memory = self.show_gpu_info()

        # 配置训练参数
        self.configure_training(gpu_memory)

        # 开始训练
        self.start_training()


if __name__ == '__main__':
    # 导入 torch 用于 GPU 检测
    import torch

    app = YOLOTrainingTUI()
    app.run()