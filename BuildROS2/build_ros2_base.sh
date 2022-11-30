#!/bin/sh

UE_PATH=$1
ROS2_WS=$2

cleanup() {
    sudo rm -r -f $1/build $1/install $1/log
    sudo rm -r -f $1/build_renamed $1/install_renamed
}

cleanup $ROS2_WS

export LANG=en_US.UTF-8

# export ROS_DOMAIN_ID=10
# pay attention it can be 'rmw_fastrtps_dynamic_cpp' too
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
# Building ros by exact UE clang toolchain
export MY_SYS_ROOT_PATH=$UE_PATH"/Engine/Extras/ThirdPartyNotUE/SDKs/HostLinux/Linux_x64/v19_clang-11.0.1-centos7/x86_64-unknown-linux-gnu"
# export MY_SYS_ROOT_PATH=$UE_PATH"/Engine/Extras/ThirdPartyNotUE/SDKs/HostLinux/Linux_x64/v20_clang-13.0.1-centos7/x86_64-unknown-linux-gnu"
export CC=$MY_SYS_ROOT_PATH"/bin/clang"
export CXX=$MY_SYS_ROOT_PATH"/bin/clang++"

# -latomic issue - see more here https://github.com/ros2/ros2/issues/418
export MY_LINKER_FLAGS="-latomic "\
"-Wl,-rpath=\${ORIGIN} "\
"-Wl,-rpath-link="$MY_SYS_ROOT_PATH" "\
"-Wl,-rpath-link="$MY_SYS_ROOT_PATH"/usr/lib "\
"-Wl,-rpath-link="$MY_SYS_ROOT_PATH"/usr/lib64 "\
"-Wl,-rpath-link=/usr/lib/x86_64-linux-gnu "\
"-Wl,-rpath-link=/usr/lib "

cd $ROS2_WS
colcon build \
    --cmake-clean-cache \
    --cmake-force-configure \
    --continue-on-error \
    --cmake-args "-DCMAKE_SHARED_LINKER_FLAGS='$MY_LINKER_FLAGS'" "-DCMAKE_EXE_LINKER_FLAGS='$MY_LINKER_FLAGS'" -DBUILD_TESTING=OFF \
    --no-warn-unused-cli \
    --packages-skip \
        ros1_bridge \
        example_interfaces \
        demo_nodes_cpp intra_process_demo quality_of_service_demo_cpp\
        rclc_examples \
        examples_rclcpp_minimal_action_client \
        examples_rclcpp_minimal_action_server \
        examples_rclcpp_minimal_client examples_rclcpp_minimal_service \
        examples_rclcpp_minimal_subscriber examples_rclcpp_minimal_publisher \
        examples_rclcpp_multithreaded_executor examples_rclcpp_minimal_timer \
        examples_rclpy_minimal_action_client examples_rclpy_minimal_action_server \
        examples_rclpy_minimal_publisher examples_rclpy_minimal_subscriber \
        examples_rclpy_minimal_client examples_rclpy_minimal_service \
        examples_rclpy_executors action_tutorials_py demo_nodes_py \
        pendulum_control bag_recorder_nodes composition \
        turtlesim \
        rviz_common rviz_ogre_vendor rviz_rendering rviz_rendering_tests \
        qt_gui_cpp qt_gui_core rqt_py_common rqt_gui \
        rclcpp \
        dummy_sensors laser_geometry message_filters tlsf_cpp \
        test_quality_of_service test_cli_remapping test_cli rclc_parameter \
        rqt_gui_cpp dummy_map_server rclcpp_lifecycle \
        rosbag2_test_common rclcpp_action rclcpp_components\
        rclpy \
        rosidl_runtime_py quality_of_service_demo_py tf2_py rqt_gui_py\
        ros2cli urdf\
        launch_ros launch_testing_ros ros2launch tracetools_launch\
        ros2lifecycle_test_fixtures ros2multicast ros2run ros2trace rosbag2_storage  sros2_cmake test_communication test_security topic_monitor  \
        action_tutorials_cpp demo_nodes_cpp_native examples_rclcpp_minimal_composition image_tools logging_demo ros2param ros2test rosbag2_cpp rosbag2_storage_default_plugins rqt rqt_console rqt_graph rqt_plot rqt_publisher rqt_py_console rqt_service_caller rqt_shell rqt_top rqt_topic test_launch_ros test_rclcpp tf2_ros tracetools_test\
        examples_tf2_py robot_state_publisher ros2component ros_testing rosbag2_compression rosbag2_converter_default_plugins rqt_msg rqt_reconfigure tf2_bullet tf2_eigen tf2_geometry_msgs tf2_kdl tf2_sensor_msgs tf2_tools 

        # geometry2 interactive_markers kdl_parser lifecycle rclc ros2action ros2doctor ros2interface ros2node ros2pkg ros2service ros2topic rosbag2_transport rqt_action rqt_srv rviz_visual_testing_framework sros2 test_tf2

        # rmw_connext_cpp rmw_connext_shared_cpp \
        # rosidl_typesupport_connext_c rosidl_typesupport_connext_cpp  \
        # foonathan_memory_vendor mimick_vendor 
        # rclcpp \
        # cyclonedds \
        # rmw_cyclonedds_cpp \
        # rmw_fastrtps_cpp \
        # rmw_fastrtps_shared_cpp \
        # rosidl_runtime_cpp \
