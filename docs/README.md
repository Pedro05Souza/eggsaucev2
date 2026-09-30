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
brew install uv                      # macOS
sudo snap install astral-uv --classic   # Linux (Ubuntu)
```

### 2️⃣ Install Dependencies

Clone the repo and install all dependencies with:

```bash
uv sync --python 3.12
```

UV automatically creates a virtual environment and installs all packages from `pyproject.toml` and `uv.lock`, including the `eggsauce` CLI. No manual venv activation needed!

> **Note**: The project needs Python 3.12. `--python 3.12` makes UV download it if you don't have it, so you only need the flag the first time.

## Running the Bot

1. Install [Docker Desktop](https://www.docker.com/products/docker-desktop/).

2. After installation, confirm Docker is correctly set up by running:

```bash
docker --version
```

3. **Run the CLI**

   Prefix every CLI command with `uv run`, which runs it inside the project's environment:

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
    uv run eggsauce migrate -name <migration_name>
    ```
    Replace <migration_name> with your desired migration name.
  * The migration is automatically applied after this generation.

#### Apply Migrations
  * Run this command to apply pending migrations without generating a new one:
    ```bash
    uv run eggsauce apply-migrations
    ```

#### Build
  * Run this command to build the containers:
    ```bash
    uv run eggsauce build
    ```
  This will execute docker compose build and create the necessary application images.
