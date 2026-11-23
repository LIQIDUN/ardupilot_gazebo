cmake_minimum_required(VERSION 3.0.2)
project(robotic_arm)

find_package(catkin REQUIRED)

catkin_package()

# 安装 meshes 文件夹，确保 Gazebo 能找到
install(DIRECTORY meshes DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION})
install(DIRECTORY urdf DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION})