# Development Container

This project is set up to run in a [GitHub Codespace](https://github.com/features/codespaces)  
(or any other service that understands [devcontainers](https://containers.dev/)).

## Usage

- **GitHub Codespaces**  
  Simply click the green **“Code”** button in GitHub and choose  
  **“Create codespace on main”** (or whichever branch you want).  
  GitHub will build the container defined in `devcontainer.json` automatically.  
  No local setup is required.

- **Local development (optional)**  
  If you want to run this devcontainer locally:
  1. Install [Docker Desktop](https://www.docker.com/products/docker-desktop/)  
     (or Podman, with the VS Code extension).
  2. Install the [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) for VS Code.
  3. Open this project in VS Code and run:  
     **Dev Containers: Reopen in Container** from the Command Palette.

## Notes

- Python 3.12 base image.  
- A local `.venv` is created inside the workspace.  
- [`uv`](https://github.com/astral-sh/uv) is installed into the `.venv` and used to install project dependencies from `pyproject.toml`.  
- VS Code is configured to use the `.venv` automatically.
