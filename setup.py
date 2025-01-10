from setuptools import setup, find_packages

setup(
    name="eggsauce",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "discord.py",
        "python-dotenv",
        "click",
        "pylint",
    ],
    entry_points={
        "console_scripts": [
            "eggsauce=tools.scripts_cli:cli"
        ]
    }
)
