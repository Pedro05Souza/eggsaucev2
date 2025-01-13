from setuptools import setup

setup(
    name="eggsauce-cli",
    version="0.1.2",
    py_modules=['scripts_cli'],
    package_dir={'': 'tools'},
    install_requires=[
        "python-dotenv",
        "click",
    ],
    entry_points={
        "console_scripts": [
            "eggsauce=scripts_cli:cli"
        ]
    },
)
