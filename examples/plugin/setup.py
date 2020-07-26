from setuptools import setup

setup(
    name='preacher-plugin-example',
    version='0.0.0',
    py_modules=['custom_matcher'],
    entry_points={'preacher': 'matcher = custom_matcher'},
    install_requires=['preacher'],
)
