#!/usr/bin/env python3
"""
YOLOv26 继续训练工具 - TUI 版本
从已有的 checkpoint (last.pt 或 best.pt) 恢复训练
"""
import sys
import os
from pathlib import Path

import torch
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, IntPrompt, Confirm, FilePathPrompt
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich import box
from ultralytics import YOLO

from utils import check_gpu

console = Console()


class ResumeTrainingTUI:
    """继续训练 TUI 交互界面"""

    def __init__(self):
        self.config = {
            'checkpoint': None,          # 权重路径
            'epochs': 0,                 # 总轮数（最终 epoch）
            'batch': 16,
            'imgsz': 640,
            'device': 0,
            'workers': 8,
            'project': './yolo_src/model/model_root',
            'name': None,
        }

    def show_banner(self):
        """显示程序横幅"""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║     ██████╗ ███████╗███████╗██╗   ██╗███╗   ███╗███████╗    ║
║     ██╔══██╗██╔════╝██╔════╝██║   ██║████╗ ████║██╔════╝    ║
║     ██████╔╝█████╗  █████╗  ██║   ██║██╔████╔██║█████╗      ║
║     ██╔══██╗██╔══╝  ██╔══╝  ██║   ██║██║╚██╔╝██║██╔══╝      ║
║     ██║  ██║███████╗███████╗╚██████╔╝██║ ╚═╝ ██║███████╗    ║
║     ╚═╝  ╚═╝╚══════╝╚══════╝ ╚═════╝ ╚═╝     ╚═╝╚══════╝    ║
║                                                              ║
║                 YOLOv26 继续训练工具 v1.0                    ║
╚══════════════════════════════════════════════════════════════╝
        """
        console.print(Align.center(Text(banner, style="bold magenta")), style="bold magenta")

    def show_gpu_info(self):
        """显示 GPU 信息"""
        has_gpu, name, memory = check_gpu()
        if has_gpu:
            info = f"🎮 GPU: {name} | 显存: {memory:.1f} GB | 可用: ✅"
            console.print(Panel(info, title="硬件检测", border_style="green"))
        else:
            console.print(Panel("⚠️ GPU 不可用，将使用 CPU 训练（速度较慢）", title="硬件检测", border_style="yellow"))
        return has_gpu, memory

    def configure_resume(self):
        """交互式配置继续训练参数"""
        console.print("\n[bold yellow]📝 继续训练参数配置[/bold yellow]")
        console.print("-" * 50)

        # 1. 选择 checkpoint 文件
        default_checkpoint = "./runs/detect/exp/weights/last.pt"
        console.print("[cyan]请输入要恢复的 checkpoint 路径 (last.pt 或 best.pt)[/cyan]")
        checkpoint = Prompt.ask("路径", default=default_checkpoint)
        checkpoint_path = Path(checkpoint)
        if not checkpoint_path.exists():
            console.print(f"[red]❌ 文件不存在: {checkpoint_path}[/red]")
            sys.exit(1)
        self.config['checkpoint'] = str(checkpoint_path)

        # 2. 加载 checkpoint 获取已训练的 epoch 和总轮数信息（可选）
        try:
            ckpt = torch.load(checkpoint_path, map_location='cpu')
            if 'epoch' in ckpt:
                trained_epochs = ckpt['epoch'] + 1  # epoch 从0开始
                console.print(f"[green]✅ 已训练轮数: {trained_epochs}[/green]")
            else:
                trained_epochs = None
            # 尝试获取原始总轮数
            if 'epochs' in ckpt.get('train_args', {}):
                original_epochs = ckpt['train_args']['epochs']
                console.print(f"[green]✅ 原始总轮数: {original_epochs}[/green]")
            else:
                original_epochs = None
        except Exception as e:
            console.print(f"[yellow]⚠️ 无法读取 checkpoint 元信息: {e}[/yellow]")
            trained_epochs = None
            original_epochs = None

        # 3. 设置最终总轮数
        if original_epochs:
            default_epochs = original_epochs
        else:
            default_epochs = 200
        console.print("[cyan]请输入最终的总轮数 (训练将从已有轮数继续到此轮)[/cyan]")
        self.config['epochs'] = IntPrompt.ask("总轮数 (epochs)", default=default_epochs)

        # 4. 其他训练参数（使用原 checkpoint 中的参数，但允许用户调整）
        # 注意：如果修改了 batch/imgsz，可能影响优化器状态，但允许用户覆盖
        console.print("\n[cyan]以下参数将使用 checkpoint 中的值，如需修改请输入新值 (留空则保持原样)[/cyan]")
        # 从 checkpoint 读取原参数（如果有）
        if checkpoint_path.exists():
            try:
                # 尝试获取 train_args
                if 'train_args' in ckpt:
                    old_args = ckpt['train_args']
                    old_batch = old_args.get('batch', 16)
                    old_imgsz = old_args.get('imgsz', 640)
                    old_workers = old_args.get('workers', 8)
                    old_project = old_args.get('project', './yolo_src/model/model_root')
                else:
                    old_batch, old_imgsz, old_workers, old_project = 16, 640, 8, './yolo_src/model/model_root'
            except:
                old_batch, old_imgsz, old_workers, old_project = 16, 640, 8, './yolo_src/model/model_root'
        else:
            old_batch, old_imgsz, old_workers, old_project = 16, 640, 8, './yolo_src/model/model_root'

        batch_input = Prompt.ask("批次大小 (batch)", default=str(old_batch))
        self.config['batch'] = int(batch_input) if batch_input.isdigit() else old_batch

        imgsz_input = Prompt.ask("图像尺寸 (imgsz, 32的倍数)", default=str(old_imgsz))
        self.config['imgsz'] = int(imgsz_input) if imgsz_input.isdigit() else old_imgsz

        workers_input = Prompt.ask("数据加载线程数 (workers)", default=str(old_workers))
        self.config['workers'] = int(workers_input) if workers_input.isdigit() else old_workers

        # 项目保存目录（可能沿用）
        project_input = Prompt.ask("保存目录 (project)", default=old_project)
        self.config['project'] = project_input

        # 实验名称（留空则沿用原名称或自动生成）
        name_input = Prompt.ask("实验名称 (留空自动生成)", default="")
        if name_input:
            self.config['name'] = name_input
        else:
            self.config['name'] = None  # 自动生成

        self.show_config_summary()

    def show_config_summary(self):
        """显示配置摘要"""
        table = Table(title="继续训练配置摘要", box=box.ROUNDED)
        table.add_column("参数", style="cyan")
        table.add_column("值", style="green")

        table.add_row("Checkpoint", self.config['checkpoint'])
        table.add_row("最终总轮数", str(self.config['epochs']))
        table.add_row("批次大小", str(self.config['batch']))
        table.add_row("图像尺寸", str(self.config['imgsz']))
        table.add_row("数据线程", str(self.config['workers']))
        table.add_row("保存目录", self.config['project'])
        table.add_row("实验名称", self.config['name'] if self.config['name'] else "自动生成")

        console.print(table)

        if not Confirm.ask("\n确认继续训练？", default=True):
            console.print("[red]已取消[/red]")
            sys.exit(0)

    def start_resume(self):
        """启动继续训练"""
        console.print("\n[bold green]🔄 正在加载 checkpoint 并恢复训练...[/bold green]\n")

        # 加载模型
        model = YOLO(self.config['checkpoint'])

        # 准备训练参数
        train_args = {
            'epochs': self.config['epochs'],
            'batch': self.config['batch'],
            'imgsz': self.config['imgsz'],
            'workers': self.config['workers'],
            'project': self.config['project'],
            'name': self.config['name'],
            'exist_ok': True,       # 允许覆盖同名
            'resume': True,         # 关键：从 checkpoint 恢复
        }

        # 启动训练
        try:
            results = model.train(**train_args)
            console.print("\n[bold green]✅ 继续训练完成！[/bold green]")
            console.print(f"📁 结果保存在: {results.save_dir}")
        except Exception as e:
            console.print(f"[red]❌ 训练出错: {e}[/red]")
            sys.exit(1)

    def run(self):
        """运行主程序"""
        self.show_banner()
        self.show_gpu_info()
        self.configure_resume()
        self.start_resume()


if __name__ == '__main__':
    app = ResumeTrainingTUI()
    app.run()