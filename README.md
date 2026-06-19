<p align="center">

  <h2 align="center">ActiveSplat: High-Fidelity Scene Reconstruction<br>through Active Gaussian Splatting (ROS 2 Jazzy Edition)</h2>
  <p align="center">
    <a href="https://li-yuetao.github.io/"><strong>Yuetao Li</strong></a><sup>1,2*</sup>
    ·
    <a href="https://github.com/kzj18"><strong>Zijia Kuang</strong></a><sup>2*</sup>
    ·
    <a href="https://laura-ting.github.io/"><strong>Ting Li</strong></a><sup>2</sup>
    ·
    <a href=""><strong>Qun Hao</strong></a><sup>1</sup>
    ·
    <a href="https://zikeyan.github.io/"><strong>Zike Yan</strong></a><sup>2†</sup>
    ·
    <a href="https://air.tsinghua.edu.cn/en/info/1046/1196.htm"><strong>Guyue Zhou</strong></a><sup>2</sup>
    ·
    <a href="https://scholar.google.nl/citations?hl=en&user=GDQ23eAAAAAJ&view_op=list_works"><strong>Shaohui Zhang</strong></a><sup>1†</sup>
  <p align="center">
        <sup>1</sup>Beijing Institute of Technology, <sup>2</sup>AIR, Tsinghua University
  </p>

<h3 align="center">
    <a href="https://ieeexplore.ieee.org/abstract/document/11037548"> <img src="https://img.shields.io/badge/IEEE-RA--L-004c99"> </a>
    <a href="https://arxiv.org/abs/2410.21955" target="_blank">
    <img src="https://img.shields.io/badge/arXiv-2410.21955-blue?logo=arxiv&color=%23B31B1B" alt="Paper arXiv"></a>
    <a href="https://li-yuetao.github.io/ActiveSplat/" target="_blank">
    <img src="https://img.shields.io/badge/Project-Page-a" alt="Project Page"></a>
    <a href="https://opensource.org/licenses/MIT" target="_blank">
    <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"></a>
</h3>
<div align="center"></div>

<div align=center> <img src="media/ui-x5.gif" width="850"/> </div>

> [!NOTE]
> **What's New in this Repo?**
> We have successfully migrated the original ROS 1 codebase to **ROS 2 (Jazzy)**! The environment has been upgraded to support **Python 3.12**, significantly modernizing the framework. We've introduced a unified `ros2 launch` script, resolved insidious deep-level Numpy/Open3D compatibility issues, and integrated a one-click Plymouth exporter. Enjoy a much more stable and robust experience!

<span class="dperact">ActiveSplat</span> enables the agent to explore the environment autonomously to build a 3D map on the fly. The integration of a Gaussian map and a Voronoi graph assures efficient and complete exploration with high-fidelity reconstruction results.

## 💡 News
* **[16 June 2025]** 🎉 Our paper **ActiveSplat** has been officially published by **IEEE RA-L 2025**!
* **[27 May 2025]** Our paper **ActiveSplat** has been accepted to **IEEE RA-L 2025**!
* **[25 Feb 2025]** 🚀 The source code of **ActiveSplat** is now **publicly available**!

## 🛠️ Installation

Our environment is robustly tested on **Ubuntu (原生系统 / WSL2)** with **ROS 2 Jazzy**, **CUDA 12.4+**, and **Python 3.12**.

Clone the repository and create the conda environment:

```bash
mkdir -p ~/ActiveSplat/src && cd ~/ActiveSplat
git clone git@github.com:Li-Yuetao/ActiveSplat.git src/ActiveSplat
cd src/ActiveSplat
git submodule update --init --progress

# It is highly recommended to use Python 3.12 for modern ecosystem support
conda create -n ActiveSplat312 python=3.12
conda activate ActiveSplat312
```

Install PyTorch by following the [instructions](https://pytorch.org/get-started/locally/). For modern CUDA (e.g. 12.4):

```bash
conda install pytorch==2.5.1 torchvision==0.20.1 torchaudio==2.5.1 pytorch-cuda=12.4 -c pytorch -c nvidia

# Strictly install requirements to avoid version conflicts (especially numpy < 2.0)
pip install -r requirements.txt
```

Install `diff-gaussian-rasterization`:

```bash
cd ~/ActiveSplat/src/ActiveSplat/submodules/diff-gaussian-rasterization
python setup.py install
pip install .
```

## 🖥️ Preparation

### Simulated environment

[Habitat-lab](https://github.com/facebookresearch/habitat-lab) and [habitat-sim](https://github.com/facebookresearch/habitat-sim) need to be installed for simulation. Because we use Python 3.12, **Habitat-Sim must be compiled from source (`main` branch)**.

```bash
cd ~/ActiveSplat/src/ActiveSplat/submodules/habitat/habitat-lab
pip install -e habitat-lab
pip install -e habitat-baselines

cd ~/ActiveSplat/src/ActiveSplat/submodules/habitat/habitat-sim
# Compile habitat-sim with CUDA from source
python setup.py install --with-cuda
```

### Build ROS 2 Workspace

We migrated from `catkin_make` to modern `colcon build`:

```bash
cd ~/ActiveSplat
# Ensure ROS 2 Jazzy is sourced
source /opt/ros/jazzy/setup.bash
colcon build

# Source the newly built workspace
source install/setup.bash
```

## 🚀 Run

### Config Datasets Path
Copy the `user_config.json` file from the `config/.templates` folder to the `config` folder, and set the absolute paths for the Gibson and MP3D datasets in `user_config.json`.

<details>
  <summary>[Datasets folder structure (click to expand)]</summary>

```
  datasets_folder
    ├── gibson_habitat
    │   ├── gibson
    │   │   ├── Adrian.glb
    │   │   └── ...
    │   └── ...
    ├── matterport
    │   ├── v1
    │   │   ├── scans
    │   │   └── tasks
    │   |       ├── 1LXtFkjw3qL
    │   |       |   ├── 1LXtFkjw3qL.glb
    │   |       |   └── ...
    │   |       └── ...
    │   ├── v2
    |   └── ...
    └── ...
```
</details>

### Run ActiveSplat (ROS 2)

Thanks to the ROS 2 migration, you no longer need multiple terminals. A unified launch file handles the synchronization of the Mapper and Planner nodes.

#### Mode 1: Headless Mode (WSL2 / Server / High Performance)
> [!IMPORTANT]
> If you are running inside **WSL2** or over SSH, you **MUST** use headless mode to prevent OpenGL EGL Driver segmentation faults.
```bash
# E.g., Gibson - Denmark
ros2 launch activesplat habitat.launch.py hide_mapper_windows:=1 hide_planner_windows:=1 scene_id:=Denmark
```

#### Mode 2: Full GUI Mode (Native Ubuntu / Display Support)
If you have a native Ubuntu system with proper NVIDIA drivers, you can watch the agent reconstruct the 3D world in real-time.
```bash
ros2 launch activesplat habitat.launch.py hide_mapper_windows:=0 hide_planner_windows:=0 scene_id:=Denmark
```

### Review the Generated 3D Map
Once the run is complete, the map data is saved as a numpy zip in `results/<timestamp>_gibson_Denmark/gaussians_data/params.npz`. 
We provide a utility script to convert this directly to standard `.ply` format, which can be dragged into any WebGL viewer (like SuperSplat):
```bash
python scripts/export_ply.py --npz results/<timestamp>_gibson_Denmark/gaussians_data/params.npz
# This generates model.ply in the same directory!
```

### Eval Results
Evaluate actions, this will read the actions from the `actions.txt` file in the result folder and evaluate them to generate the `actions_error.txt` file.
#### Single scene
```bash
result_name="2025-02-25_11-43-48_gibson_Denmark"
python scripts/judges/eval_actions.py --save_path results/$result_name/actions_error.txt --config results/$result_name/config.json --user_config config/user_config.json --actions results/$result_name/actions.txt --gpu_id 0
```

#### Batch scenes
```bash
# If you want to force re-evaluation, you can add the `--force` flag
python scripts/batch/eval_results_actions.py --results_dir ./results --gpu_id 0
```

## ✏️ Acknowledgments

Our implementation is built upon <a href="https://github.com/kzj18/activeINR-S">ANM-S</a>. We would also like to thank the authors of the following open-source repositories:

- <a href="https://github.com/spla-tam/SplaTAM">SplaTAM</a> for the mapper implementation.
- <a href="https://github.com/muskie82/MonoGS">MonoGS</a> for the online gaussian map visualization.

If you find these works helpful, please consider citing them as well.

## 🎓 Citation

If you find our code/work useful in your research, please consider citing the following:
```bibtex
@article{li2025activesplat,
    title={Activesplat: High-fidelity scene reconstruction through active gaussian splatting},
    author={Li, Yuetao and Kuang, Zijia and Li, Ting and Hao, Qun and Yan, Zike and Zhou, Guyue and Zhang, Shaohui},
    journal={IEEE Robotics and Automation Letters},
    year={2025},
    publisher={IEEE}
}
```