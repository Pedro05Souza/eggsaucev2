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

### Installing and Running the `eggsauce CLI`

Once Docker is successfully installed, follow these steps to set up and run the `eggsauce CLI`:

1. **Install the CLI**  
   Run the following command in your terminal to install the CLI:

   ```bash
   pip install .
   ```

2. **Run the CLI**
  Use the command below to run the `eggsauce CLI:`

  ```bash
   eggsauce run --env <environment>
   ```

   The `--env` flag specifies the environment in which the CLI will run. It supports the following options:

  * `dev`: Development environment (default).
  * `prod`: Production enviroment.
