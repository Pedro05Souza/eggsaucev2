<div align="center">
    <img src="eggsauce.png" alt="Logo" width="200" height="200">
    <h3 align="center">Eggsauce</h3>
</div>

<details>
  <summary>Table of Contents</summary>
  <ol>
    <li><a href="#project-dependencies">Project Dependencies</a></li>
    <li><a href="#running-the-bot">Running the Bot</a></li>
  </ol>
</details>

## 🔧 Setting Up Project Dependencies

Follow the steps below to set up the project and get it running in no time. 


> **Note**: Without the proper enviroment variables configured, this project will **NOT** function as intended.

### 1️⃣ Install UV

This project uses [UV](https://astral.sh/uv/) for fast and reliable dependency management. Install it first:

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```bash
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Or use your package manager:
```bash
brew install uv        # macOS
sudo apt install uv    # Linux (Ubuntu/Debian)
```

### 2️⃣ Install Dependencies

Clone the repo and install all dependencies with:

```bash
uv sync
```

UV automatically creates a virtual environment and installs all packages from `pyproject.toml` and `uv.lock`. No manual venv activation needed!

## Running the Bot


1. Install [Docker Desktop](https://www.docker.com/products/docker-desktop.).

2. After installation, confirm Docker is correctly set up by running the following command in your terminal:

```powershell
docker --version
```

### Installing and Running the CLI

1. Install [Docker Desktop](https://www.docker.com/products/docker-desktop/).

2. After installation, confirm Docker is correctly set up by running:

```bash
docker --version
```

3. **Run the CLI**

   UV automatically manages the environment, so you can run the CLI directly:

   ```bash
   uv run eggsauce run --env <environment>
   ```

   The `--env` flag specifies the environment in which the CLI will run. It supports the following options:

  * `dev`: Development environment (default).
  * `prod`: Production environment.

### Additional Commands in the CLI

#### Migrate
Use the migrate command to generate and apply database migrations.
  * Run this command to create a migration:
    ```bash
    eggsauce migrate -name <migration_name>
    ```
    Replace <migration_name> with your desired migration name.
  * The migration is automatically applied after this generation.

#### Build
  * Run this command to build the containers:
    ```bash
    eggsauce build
    ```
  This will execute docker compose build and create the necessary application images.
