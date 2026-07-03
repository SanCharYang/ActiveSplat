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

## 📖 Introduction
**ActiveSplat** is an autonomous exploration and 3D mapping framework. It enables an agent to explore unknown environments autonomously and build a high-fidelity 3D map on the fly. By deeply integrating a **3D Gaussian Splatting (3DGS)** representation with a **Voronoi graph-based path planner**, ActiveSplat ensures efficient and complete scene exploration while maintaining photorealistic reconstruction results.

## 🌟 ROS 2 Migration Achievements & Environment
This repository hosts the heavily modernized and migrated version of ActiveSplat. The original architecture was built on ROS 1 and Python 3.8. We have successfully upgraded the entire framework to adapt to modern robotic software stacks:

- **Adapted Environments**: 
  - Operating System: Native Ubuntu 24.04 (Recommended) / WSL2 Ubuntu 24.04
  - ROS Version: **ROS 2 Jazzy**
  - Python: **Python 3.12**
  - Compute: CUDA 12.4+
- **Migration Highlights**:
  - Replaced the deprecated `catkin` build system with `colcon`.
  - Migrated all nodes, services, and publishers/subscribers from `rospy` to `rclpy`.
  - Resolved strict typing, dataclass, and PyBind11 compatibility issues introduced by Python 3.12.
  - Provided a unified `ros2 launch` mechanism, eliminating the need to manually spawn multiple terminals.
  - Handled implicit and explicit headless context setups for both Native and WSL2 executions.

## 🛠️ Operation & Migration Manual
For comprehensive instructions on how to install dependencies, configure the datasets, build the ROS 2 workspace, and run ActiveSplat in both headless and GUI modes, please refer to our detailed manual:

👉 **[ActiveSplat ROS 2 Operation Manual](docs/operation_manual.md)**

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