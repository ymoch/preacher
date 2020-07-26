from setuptools import setup

setup(
    name='preacher-plugin-example',
    version='0.0.0',
    py_modules=['plugin_example'],
    entry_points={'preacher': '.preacher = plugin_example'},
    install_requires=['preacher'],
)
