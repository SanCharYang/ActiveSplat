cmake_minimum_required(VERSION 3.8)
project(activesplat)

# Default to C++14
if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 14)
endif()

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# ---- Find dependencies ----
find_package(ament_cmake REQUIRED)
find_package(rclpy REQUIRED)
find_package(std_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(cv_bridge REQUIRED)
find_package(image_transport REQUIRED)
find_package(tf2 REQUIRED)
find_package(tf2_ros REQUIRED)
find_package(tf2_geometry_msgs REQUIRED)
find_package(rosidl_default_generators REQUIRED)

# ---- Generate interfaces (msg/srv) ----
rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/Frame.msg"
  "srv/GetDatasetConfig.srv"
  "srv/ResetEnv.srv"
  "srv/GetTopdownConfig.srv"
  "srv/GetTopdown.srv"
  "srv/SetPlannerState.srv"
  "srv/SetMapper.srv"
  "srv/GetOpacity.srv"
  "srv/GetVoronoiGraph.srv"
  "srv/GetNavPath.srv"
  DEPENDENCIES std_msgs sensor_msgs geometry_msgs
)

# ---- Install Python scripts as executables ----
install(PROGRAMS
  scripts/nodes/mapper_node.py
  scripts/nodes/planner_node.py
  DESTINATION lib/${PROJECT_NAME}
)

# ---- Install launch files ----
install(DIRECTORY
  launch/
  DESTINATION share/${PROJECT_NAME}/launch
)

# ---- Install config files ----
install(DIRECTORY
  config/
  DESTINATION share/${PROJECT_NAME}/config
)

# ---- Ament package finalization ----
ament_package()
