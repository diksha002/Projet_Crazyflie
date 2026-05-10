from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration
from ament_index_python.packages import get_package_share_directory
import os
import xacro


def generate_launch_description():
    # Package and xacro path
    pkg_share = get_package_share_directory("crazyflie_description")
    xacro_file = os.path.join(pkg_share, "urdf", "crazyflie_body.xacro")


    # Paths to access existing crazyflie_world.sdf instead of empty.sdf
    simulation_root = os.path.abspath(os.path.join(pkg_share, '../../../../../'))
    gz_resource_path = os.path.join(simulation_root, 'simulator_files/gazebo')
    world_file = os.path.join(gz_resource_path, 'worlds/crazyflie_world.sdf')


    # Process xacro → urdf
    robot_description_config = xacro.process_file(xacro_file).toxml()


    # Environment variable for Gazebo
    set_gz_path = SetEnvironmentVariable(
        name='GZ_SIM_RESOURCE_PATH',
        value=gz_resource_path
    )


    # Launch argument for robot name
    robot_name_arg = DeclareLaunchArgument(
        "robot_name",
        default_value="crazyflie",
        description="Name of the robot"
    )

    # For Rviz
    use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation time'
    )
    
    namespace = LaunchConfiguration("robot_name")


    """
    Commented below code:
        - will start existing crazyflie_world.sdf instead of an empty one
        - since the world file already contains a crazyflie model, will not need to spawn the drone

    # Start Gazebo Harmonic (empty world)
    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory("ros_gz_sim"), "launch", "gz_sim.launch.py"
            )
        ),
        launch_arguments={"gz_args": "-r empty.sdf"}.items(),
    )

    # Spawn robot in Gazebo
    spawn_robot = Node(
        package="ros_gz_sim",
        executable="create",
        arguments=[
            "-name", LaunchConfiguration("robot_name"),
            "-string", robot_description_config,
            "-x", "0.0",   # X position
            "-y", "0.0",   # Y position
            "-z", "0.5",   # Z position (height)
        ],
        output="screen",
    )
    """
    # Gazebo with custom world
    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory("ros_gz_sim"), "launch", "gz_sim.launch.py"
            )
        ),
        launch_arguments={"gz_args": f"-r {world_file}"}.items(),
    )


    # Robot State Publisher (for RViz)
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'use_sim_time': LaunchConfiguration('use_sim_time'),
            'robot_description': robot_description_config
        }]
    )

    
    # ROS-Gazebo bridge
    bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        parameters=[{
            "config_file": os.path.join(pkg_share, "config", "ros_gz_crazyflie_bridge.yaml"),
        }],
        output="screen",
    )


    return LaunchDescription([
        set_gz_path,
        robot_name_arg,
        use_sim_time,
        gazebo_launch,
        robot_state_publisher,
        bridge,
    ])
