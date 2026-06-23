from setuptools import find_packages, setup

package_name = 'nao_control'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(),
    data_files=[
        ('share/ament_index/resource_index/packages',
         ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/config', ['config/bridge.yaml']),
        ('share/' + package_name + '/launch', ['launch/simulation.launch.py']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='krishnamaithreya',
    maintainer_email='krishnamaithreya@gmail.com',
    description='Nao humanoid control nodes for Gazebo simulation',
    license='MIT',

    entry_points={
        'console_scripts': [
            'joint_commander = nao_control.joint_commander:main',
            'walk_controller = nao_control.walk_controller:main',
            'head_controller = nao_control.head_controller:main',
            'sensor_monitor = nao_control.sensor_monitor:main',
            'demo_sequence = nao_control.demo_sequence:main',
            'trajectory_bridge = nao_control.trajectory_bridge:main',
        ],
    },
)
