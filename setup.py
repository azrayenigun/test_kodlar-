import os
from glob import glob
from setuptools import setup

package_name = 'arc_rover_autonomy'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob(os.path.join('launch', '*launch.[pxy][yma]*'))),
        (os.path.join('share', package_name, 'config'), glob(os.path.join('config', '*.yaml'))),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='azra',
    maintainer_email='azra@todo.todo',
    description='Lupus Arm Autonomy Package',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'yayin_yap = arc_rover_autonomy.yayin_yapan:main',
            'dinle = arc_rover_autonomy.dinleyen:main',
            'hesapla = arc_rover_autonomy.servis_node:main',
            'dummy_vision = arc_rover_autonomy.dummy_vision:main',
            'main_autonomy = arc_rover_autonomy.main_autonomy:main',
            'task_delivery = arc_rover_autonomy.task_delivery:main',
            'master_node = arc_rover_autonomy.master_node:main',
        ],
    },
)
import os
from glob import glob
from setuptools import setup

package_name = 'arc_rover_autonomy'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob(os.path.join('launch', '*launch.[pxy][yma]*'))),
        (os.path.join('share', package_name, 'config'), glob(os.path.join('config', '*.yaml'))),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='azra',
    maintainer_email='azra@todo.todo',
    description='Lupus Arm Autonomy Package',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'yayin_yap = arc_rover_autonomy.yayin_yapan:main',
            'dinle = arc_rover_autonomy.dinleyen:main',
            'hesapla = arc_rover_autonomy.servis_node:main',
            'dummy_vision = arc_rover_autonomy.dummy_vision:main',
            'main_autonomy = arc_rover_autonomy.main_autonomy:main',
            'task_delivery = arc_rover_autonomy.task_delivery:main',
            'master_node = arc_rover_autonomy.master_node:main',
        ],
    },
)
import os
from glob import glob
from setuptools import setup

package_name = 'arc_rover_autonomy'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob(os.path.join('launch', '*launch.[pxy][yma]*'))),
        (os.path.join('share', package_name, 'config'), glob(os.path.join('config', '*.yaml'))),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='azra',
    maintainer_email='azra@todo.todo',
    description='Lupus Arm Autonomy Package',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'yayin_yap = arc_rover_autonomy.yayin_yapan:main',
            'dinle = arc_rover_autonomy.dinleyen:main',
            'hesapla = arc_rover_autonomy.servis_node:main',
            'dummy_vision = arc_rover_autonomy.dummy_vision:main',
            'main_autonomy = arc_rover_autonomy.main_autonomy:main',
            'task_delivery = arc_rover_autonomy.task_delivery:main',
            'master_node = arc_rover_autonomy.master_node:main',
        ],
    },
)

