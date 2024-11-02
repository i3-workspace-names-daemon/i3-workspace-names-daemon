from setuptools import setup


with open('README.md', encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='i3-workspace-names-daemon',
    version='0.15.2',
    description='Dynamically update the name of each i3wm workspace using font-awesome icons or the names of applications running in each workspace.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/cboddy/i3-workspace-names-daemon',
    license='MIT',
    zip_safe=False,
    py_modules=['i3_workspace_names_daemon', 'fa_icons'],
    install_requires=["i3ipc"],
    extras_require={'testing': ['flake8', 'pytest', 'pytest-cov', 'pytest-randomly']},
    author='Chris Boddy',
    author_email='chris@boddy.im',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': [
            'i3-workspace-names-daemon=i3_workspace_names_daemon:main'
        ]
    },
)
