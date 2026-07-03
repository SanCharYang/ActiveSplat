#!/usr/bin/env python3
import os
PACKAGE_PATH = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir, os.pardir))
SRC_PATH = os.path.abspath(os.path.join(PACKAGE_PATH, 'src'))
import sys
sys.path.append(PACKAGE_PATH)
sys.path.append(SRC_PATH)
import json
import argparse
from typing import Union

import faulthandler

import threading
import torch
import numpy as np
from open3d.visualization import gui
from PIL import ImageFile, Image
ImageFile.LOAD_TRUNCATED_IMAGES = True
Image.MAX_IMAGE_PIXELS = None

import rclpy
from rclpy.node import Node as ROS2Node

from mapper import MapperType
from utils import PROJECT_NAME, GlobalState
from dataloader.dataloader import get_dataset, HabitatDataset
from visualizer.visualizer import Visualizer

if __name__ == '__main__':
    faulthandler.enable()
    seed = 1
    np.random.seed(seed)
    torch.manual_seed(seed)

    parser = argparse.ArgumentParser(description=f'{PROJECT_NAME} mapper node.')
    parser.add_argument('--mapper',
                        type=str,
                        choices=list(MapperType.__members__),
                        required=True,
                        help='Specify the mapper type.')
    parser.add_argument('--config',
                        type=str,
                        required=True,
                        help='Input config url (*.json).')
    parser.add_argument('--scene_id',
                        type=str,
                        required=True,
                        help='Specify test scene id.')
    parser.add_argument('--user_config',
                        type=str,
                        required=True,
                        help='User config url (*.json).')
    parser.add_argument('--gpu_id',
                        type=int,
                        required=True,
                        help='Specify gpu id.')
    parser.add_argument('--mode',
                        type=str,
                        choices=list(GlobalState.__members__)[:-1],
                        required=True,
                        help='Specify the mode to start with.')
    parser.add_argument('--actions',
                        type=str,
                        required=True,
                        help='Specify the actions to replay.')
    parser.add_argument('--parallelized',
                        type=int,
                        required=True,
                        help='Tell the mapper node to be parallelized.')
    parser.add_argument('--hide_windows',
                        type=int,
                        required=True,
                        help='Disable windows.')
    parser.add_argument('--save_runtime_data',
                        type=int,
                        required=True,
                        help='Save runtime data.')
    parser.add_argument('--debug',
                        type=int,
                        default=0,
                        help='Debug mode, output more logs.')
    parser.add_argument('--remark',
                        type=str,
                        default='NONE',
                        help='remark info.')
    
    args, _ = parser.parse_known_args()

    rclpy.init()
    node = rclpy.create_node(
        'mapper_node',
        allow_undeclared_parameters=True,
        automatically_declare_parameters_from_overrides=True
    )
    logger = node.get_logger()
    
    if args.mode == 'REPLAY' and args.actions is None:
        parser.error('Replay mode requires actions to replay.')
    
    if torch.cuda.is_available():
        device = torch.device('cuda', args.gpu_id)
    else:
        logger.warn('No GPU available.')
        device = torch.device('cpu')
        
    os.chdir(PACKAGE_PATH)
    logger.info(f'Current working directory: {os.getcwd()}')
    with open(args.config) as f:
        config = json.load(f)
        if 'env' in config:
            config['env']['config'] = os.path.abspath(
                os.path.join(os.path.dirname(args.config), os.pardir, os.pardir, config['env']['config']))
        if 'sensor' in config:
            config['sensor']['config'] = os.path.abspath(
                os.path.join(os.path.dirname(args.config), os.pardir, os.pardir, config['sensor']['config']))
    
    with open(args.user_config) as f:
        user_config = json.load(f)
    
    dataset:Union[HabitatDataset] = get_dataset(config, user_config, args.scene_id, args.remark)

    hide_windows = bool(args.hide_windows)
    if not hide_windows:
        app = gui.Application.instance
        app.initialize()
    # [ROS2 Migration] Run executor in a background thread.
    # This prevents deadlocks during synchronous service calls in __init__
    # and allows Open3D's app.run() GUI loop to run concurrently in the main thread.
    executor = rclpy.executors.MultiThreadedExecutor()
    executor.add_node(node)
    spin_thread = threading.Thread(target=executor.spin, daemon=True)
    spin_thread.start()

    w = Visualizer(
        MapperType(args.mapper),
        args.config,
        GlobalState(args.mode),
        1 if hide_windows else app.add_font(gui.FontDescription(gui.FontDescription.MONOSPACE)),
        device,
        args.actions,
        dataset,
        bool(args.parallelized),
        hide_windows,
        bool(args.save_runtime_data),
        ros_node=node)
        
    if hide_windows:
        import time
        while rclpy.ok() and getattr(w, 'traing_finished', False) == False:
            time.sleep(1)
    else:
        app.run()
    
    logger.info(f'{PROJECT_NAME} mapper node finished.')
    node.destroy_node()
    import open3d as o3d
    o3d.core.cuda.release_cache()
    rclpy.shutdown()