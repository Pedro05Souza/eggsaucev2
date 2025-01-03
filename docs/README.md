<div align="center">
    <img src="eggsauce.png" alt="Logo" width="200" height="200">
    <h3 align="center">Eggsauce</h3>
</div>

<details>
  <summary>Table of Contents</summary>
  <ol>
    <li><a href="#built-with">Built With</a></li>
    <li><a href="#project-dependencies">Project Dependencies</a></li>
    <li><a href="#running-the-bot">Running the Bot</a></li>
  </ol>
</details>

## Built With

![Static Badge](https://img.shields.io/badge/discord.py-7289DA?style=for-the-badge&logo=discord&logoColor=white)

## 🔧 Setting Up Project Dependencies

Follow the steps below to set up the project and get it running in no time. 


> **Note**: Without the proper enviroment variables configured, this project will **NOT** function as intended.

### 1️⃣ Setting Up a Virtual Environment  

To install dependencies, you must first clone the repo onto a directory of your choice. After proceed with the following terminal command:

```bash
python -m venv venv
```

This will create a virtual python enviroment necessary for installing the dependancies.

### 2️⃣ Activate the Virtual Environment

### Windows

  ```bash
  venv/Scripts/activate
 ```

Note: If you encounter a permission issue, execute the following command in PowerShell:

  ```bash
 Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser 
 ```

### macOS/Linux

  ```bash
source venv/bin/activate
 ```

### 📦 Installing Dependencies

 After activating the virtual environment, install the necessary dependencies with:

  ```bash
pip install -r requirements.txt
 ```

## Running the Bot


1. Install [Docker Desktop](https://www.docker.com/products/docker-desktop.).

2. After installation, confirm Docker is correctly set up by running the following command in your terminal:

```powershell
docker --version
```

3. If Docker is successfully installed, you can proceed by building and running the project using `docker-compose`. Execute the following command:

```powershell
docker compose build
```

followed by

```powershell
docker compose up
```

Your bot should now be live and running! 🎉