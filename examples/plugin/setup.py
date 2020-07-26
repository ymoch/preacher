from setuptools import setup

setup(
    name='preacher-plugin-example',
    py_modules=['plugin_example'],
    entry_points={'preacher': '.preacher = plugin_example'},
    install_requires=['preacher'],
)
