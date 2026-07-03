# ActiveSplat ROS 2 迁移与部署操作手册

## 1. 导言
本手册详细记录了 ActiveSplat 算法架构从 ROS 1 (Python 3.8) 迁移至 ROS 2 Jazzy (Python 3.12) 的标准化部署流程。除核心指令指南外，本手册亦对编译环境构建、底层依赖兼容性修正以及 ROS 2 节点生命周期管理进行了严谨的技术归档。这为后续的异构平台迁移、系统二次开发及高斯建图算法扩展提供了坚实的技术参考。

## 2. 系统与架构选型分析
在环境重构阶段，经过充分的性能论证与编译测试，本项目确立了以下基础运行环境规范：

### 2.1 底层计算平台规范
- **操作系统**：Ubuntu 24.04 LTS (原生支持硬件级 OpenGL/EGL，向下兼容 WSL2 CPU 渲染)
- **机器人操作系统**：ROS 2 Jazzy Jalisco
- **Python 环境**：Python 3.12
- **CUDA 架构**：系统级 CUDA 12.6

### 2.2 核心技术栈决策依据
1. **采用系统级 CUDA 12.6 的技术必要性**
   在常规的深度学习部署中，通常通过 `pip` 或 `conda` 获取闭源附带的精简版 CUDA 运行时即可满足计算需求。然而，本项目重度依赖 `diff-gaussian-rasterization` (高斯光栅化核心引擎) 与 `Habitat-Sim` (物理级物理与渲染仿真器) 这两个底层 C++/CUDA 拓展模块。此类模块在编译期需要调用完整的 NVCC 编译器链路与全量 CUDA 核心头文件。`pip` 内置的沙盒版 CUDA 缺乏这些基础设施，会导致编译器无法完成底层的动态链接库构建。
   此外，Ubuntu 24.04 搭载的 GCC 13 版本引入了极为严格的标准库包含审查与语法校验机制，早期的 CUDA 版本会与其产生严重的语法冲突。经过验证，CUDA 12.6 及其对应的底层头文件能够与 GCC 13 完美适配，从根本上保证了底层光栅化代码编译的成功率与计算稳定性。

2. **Python 3.12 与依赖生态的兼容性重构**
   引入 Python 3.12 为系统带来了显著的运行期性能提升，但也附加了更为严苛的语法规范。例如，Python 3.12 强化了对 `dataclass` 类型默认参数的审查，严禁在类属性中使用可变对象（如空字典 `{}` 或空列表 `[]`）作为默认值。为此，本项目中引入了自动化的抽象语法树 (AST) 补丁脚本（`scripts/patch_habitat_dataclass.py`），通过代码注入技术将非法定义重写为 `field(default_factory=dict)`，彻底规避了 `habitat-lab` 启动时的初始化异常。
   同时，系统升级处理了由于 Numpy 2.x 引入的底层 API 变化所诱发的警告信息，通过精准的矩阵降维与布尔型重塑，消除了高并发数据流在 Open3D 及 ROS 2 序列化时可能产生的兼容性隐患。

## 3. 环境配置与编译流程

### 3.1 基础依赖与 ROS 2 安装
依据官方规范部署适用于 Ubuntu 24.04 的 ROS 2 Jazzy Desktop 版本。安装完成后，需将环境变量加载语句注入终端配置：
```bash
echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

### 3.2 源码同步与沙盒环境初始化
借助 Miniconda 构建隔离的运行沙盒：
```bash
mkdir -p ~/ActiveSplat/src && cd ~/ActiveSplat
git clone -b ros2-migration https://github.com/SanCharYang/ActiveSplat.git src/ActiveSplat
cd src/ActiveSplat
git submodule update --init --recursive --progress

conda create -n ActiveSplat312 python=3.12 -y
conda activate ActiveSplat312

# 安装基于 CUDA 12.4+ 构建的 PyTorch 2.5 系列核心计算库
pip install torch==2.5.1 torchvision==0.20.1 torchaudio==2.5.1 --index-url https://download.pytorch.org/whl/cu124
pip install -r requirements.txt
```

### 3.3 Habitat 仿真器编译重构
#### 必须采用 CMake 实施手动编译的缘由
早期工作流通常利用 `python setup.py install` 全自动构建 `habitat-sim`。但在升级至 Python 3.12 与 GCC 13 后，该自动化构建链存在两大逻辑缺陷：首先，其难以规避 Conda 环境内嵌的交叉链接器污染，极易链接到错误的底层 `glibc` 引发段错误；其次，其经常遗漏关键宏指令，触发标准库头文件 `cstdint` 缺失的编译阻断。
为确保最高级别的编译可控性与环境净度，本项目废弃了原生的 `setup.py`，转而使用 CMake 执行显式的跨平台编译控制。
- 借由 `unset` 抹除所有 Conda 环境变量污染源。
- 利用 `-DCMAKE_CXX_FLAGS="-include cstdint"` 强制达成 GCC 13 全局兼容。
- 显式关闭 `BUILD_WITH_CUDA=OFF`，规避陈旧 CUDA 算子与高版本驱动的编译冲突，交由后续的光栅化模块负责算力加速。

**标准化编译执行流**：
```bash
# 1. 挂载上层依赖库
cd ~/ActiveSplat/src/ActiveSplat/submodules/habitat/habitat-lab
pip install -e habitat-lab
pip install -e habitat-baselines

# 2. 清除污染并配置 CMake
cd ~/ActiveSplat/src/ActiveSplat/submodules/habitat/habitat-sim
rm -rf build && mkdir build && cd build
unset CFLAGS CXXFLAGS CPPFLAGS LDFLAGS CMAKE_ARGS CC CXX CONDA_BUILD_SYSROOT

cmake \
  -DBUILD_PYTHON_BINDINGS=ON \
  -DPYTHON_EXECUTABLE=$(which python) \
  -DCMAKE_BUILD_TYPE=RelWithDebInfo \
  -DBUILD_GUI_VIEWERS=ON \
  -DBUILD_WITH_BULLET=OFF \
  -DBUILD_WITH_CUDA=OFF \
  -DCMAKE_C_COMPILER=/usr/bin/gcc \
  -DCMAKE_CXX_COMPILER=/usr/bin/g++ \
  -DCMAKE_CXX_FLAGS="-include cstdint" \
  ../src

# 3. 开启多核全速编译
make -j$(nproc)

# 4. 动态链接库软链与安装
mkdir -p ../src_python/habitat_sim/_ext/
cp build/RelWithDebInfo/lib/habitat_sim_bindings.cpython-312-x86_64-linux-gnu.so ../src_python/habitat_sim/_ext/
echo "$(realpath ../src_python)" > $(python -c "import site; print(site.getsitepackages()[0])")/habitat_sim.pth
echo "$(realpath build/deps/magnum-bindings/src/python)" >> $(python -c "import site; print(site.getsitepackages()[0])")/habitat_sim.pth
pip install ./deps/magnum-bindings/src/python

# 5. 执行 Python 3.12 语法树自动修复
cd ~/ActiveSplat/src/ActiveSplat
python scripts/patch_habitat_dataclass.py
```

### 3.4 高斯光栅化引擎编译
受 GCC 13 头文件调整影响，高斯底层库同样需要提前注入头文件进行修正，随后解除构建隔离实现就地安装：
```bash
cd ~/ActiveSplat/src/ActiveSplat/submodules/diff-gaussian-rasterization
sed -i '1i #include <cstdint>' cuda_rasterizer/rasterizer_impl.h
pip install -e . --no-build-isolation
```

### 3.5 ROS 2 工作空间编译
作为架构的顶层，需通过最新的 `colcon` 工具链完成模块链接：
```bash
cd ~/ActiveSplat
sudo apt install python3-colcon-common-extensions -y
pip install empy==3.3.4 lark catkin_pkg

colcon build --symlink-install
source install/setup.bash
```

## 4. 系统运行与节点管理机制

### 4.1 数据集对接
部署官方的 Gibson/Matterport3D 数据集，于项目根目录 `config/user_config.json` 模板中映射数据集物理绝对路径。

### 4.2 ROS 2 节点并发与通信可靠性规约
ROS 2 的微服务架构在带来高效数据分发的同时，亦对并发管控与类型安全提出了更加严苛的要求，特此在迁移中确立了以下规范以消除各类潜在宕机异常：
1. **强类型返回断言保障**：`rclpy` 框架中所有被触发的 Server 回调必须且仅能返回被明确初始化的 Response 对象。若隐式触发返回 `None` 或类型残缺，底层负责 PyObject 桥接转换的 `rosidl_generator_py` 将触发诸如 `PyBool_Check` 失败之类的灾难性断言（Assertion Failed）进而直接终止进程。通过严格的 `.astype(bool)` 类型转换与健全的合法 `return res`，从根源断绝了底层数据结构崩塌的可能性。
2. **多线程安全阻断机制与资源无死锁释放**：当核心流程到达生命周期末端（Graceful Shutdown），由于 Mapper 进程的守护线程、订阅轮询循环与跨节点客户端存在极强的时序耦合。此时若鲁莽销毁节点，会因服务句柄悬空抛出 `InvalidHandle`。此外，注销服务时严禁调用不存在的 `.shutdown()` 接口。必须调用标准接口 `.destroy()` 并在正确释放内部并发锁、彻底终结子线程阻塞后方可退出。如此处理，可确保无头服务以完美时序安全收官而免除任何死锁滞留现象。

### 4.3 任务调度机制
项目摒弃了原系统复杂的终端分发，现采用集中化的启动脚本处理一切节点串联与环境挂载：

```bash
# 执行流 A：图形实时监控模式（推荐运行于配备显示输出的物理主机）
ros2 launch activesplat habitat.launch.py hide_mapper_windows:=0 hide_planner_windows:=0 scene_id:=Denmark

# 执行流 B：完全静默运行模式（面向远程终端、SSH及计算集群调度）
ros2 launch activesplat habitat.launch.py hide_mapper_windows:=1 hide_planner_windows:=1 scene_id:=Denmark
```

### 4.4 高保真 3D 成果解算
系统运行结束后，由仿真器内建管线生成的数百万级三维高斯球参数将封存为原生的 Numpy 二进制档案 (`params.npz`)。本项目集成了一个高效的后处理矩阵解算器：
```bash
python src/ActiveSplat/scripts/npz_to_ply.py --input src/ActiveSplat/results/<TIMESTAMP>_gibson_Denmark/gaussians_data/params.npz
```
该脚本将利用张量切片直接剥离无效高斯并将自适应色彩模型进行数学逆变，进而导出通用图形学标准的 `.ply` 文件，全面兼容包括 [SuperSplat](https://playcanvas.com/supersplat/editor) 在内的现代 WebGL 平台直接渲染与多重漫游。
