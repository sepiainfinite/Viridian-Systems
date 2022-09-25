# Installing Docker for Ignition Development

## Install Windows Subsystem for Linux (WSL)

1. Launch Command Prompt with `Win+R` and then type `cmd`.

2. Run the following command: `wsl --install`, then restart your computer for the WSL installation to take affect.

3. After the installation, change the default version with `wsl --set-default-version 2`.

4. Once installation is complete, create a username and password from 'Ubuntu for Windows' application that was installed or by typing `wsl` in command prompt.

*The entry prompt will not show any characters as you type your password.*

## Program installation

Install the following programs:

1. [Visual Studio Code](https://code.visualstudio.com/Download)

Visual Studio Code also needs the following extensions:

- [Remote - WSL](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-wsl)
- [Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python)
- [Docker](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-docker)

2. [Git for Windows](https://gitforwindows.org/), from the "Choosing default editor used by git" page, select "Use Visual Studio Code" as the default editor.

## Install and Set Up Docker Inside WSL Ubuntu

Docker is a tool that makes it easy to set up containerized applications from existing images. Your Ignition development environment will live inside a Docker container.

We will not be using Docker Desktop for Windows for this project. We will instead be downloading and installing Docker onto Ubuntu within WSL. All commands in this section will need to be run in Ubuntu.

### Install Docker

From inside VSCode, ``CTRL+Shift+` `` to open a terminal panel.

 Check the '>' icon at the top right of the terminal panel says 'wsl'. To change to wsl the plus '+' icon has a drop down menu that can select/ change the default terminal profile to 'wsl'.

1. Update list of available packages with `sudo apt update`. Enter your password as well.

2. Install Docker with `sudo apt install docker.io -y`.

3. Check the Docker installation by running `docker --version`.

### Configure wsl to launch docker at startup

1. Open file that controls sudo command execution: `sudo visudo`.

2. Add the following code to the end of your file. ("yourusername" is the ubuntu username you set)

```bash
# Docker daemon specification
yourusername ALL=(ALL) NOPASSWD: /usr/bin/dockerd
```

3. Press `CTRL+X` to exit.

4. Press `Y` to confirm save.

5. Press `ENTER` to confirm file name.

6. Open bash configuration file in vs-code: `code ~/.bashrc`. It will install vs-code server in WSL, making it easier to access these files in the future.

7. Add the following to the end of the file:

```bash
# Start Docker daemon automatically when logging in if not running.
RUNNING=`ps aux | grep dockerd | grep -v grep`
if [ -z "$RUNNING" ]; then
    sudo dockerd > /dev/null 2>&1 &
    disown
fi
```

8. Save and quit.

9. Add your username to the docker group so Docker can be ran as a non-root user. `sudo usermod -aG docker $USER`.

10. Close and re-open VS Code, this should force you to re-log into ubuntu

12. Verify the installation of docker with `docker ps`. If you see `CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES` then docker is correctly installed and running.

### Install Docker Compose

1. Download latest version of Docker Compose:

```bash
sudo curl -kL https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64 -o /usr/local/bin/docker-compose
```

2. Apply executable permissions to the binary: `sudo chmod +x /usr/local/bin/docker-compose`.

3. Verify Docker Compose installation: `docker-compose --version`.

## Create Docker Container for Ignition

1. From your home directory create a folder for your project work.

2. Open the folder in VSCode from explorer and create a new directory called 'ignition-data'.

3. Create a new file called 'docker-compose.yml'

4. Paste the following into the file. **Note:** PATH/TO/WORK/FOLDER is the absolute path to the folder that was made. WSL uses /mnt/c/ as the C:/ Drive that would normally be used to navigate on windows.

```yml
version: "3.8"
services:
  ignition:
    image: inductiveautomation/ignition:8.1.19
    ports:
      - "80:8088"
    volumes:
      - ignition_data:/var/lib/ignition/data
    environment:
      GATEWAY_ADMIN_PASSWORD: password
      IGNITION_UID: 1000
      IGNITION_GID: 1000
      TZ: 'America/Los_Angeles'

volumes:
  ignition_data:
    driver: local
    driver_opts:
      type: none
      device: "PATH/TO/WORK/FOLDER/ignition_data"
      o: bind

```

5. From a terminal panel on VSCode, type `docker-compose up -d` to run the '.yml' file without logs and wait for the downloads to complete.

6. Once the docker container has been created, navigate to <http://localhost/web/home> to see the Ignition home page.

Removing the container can be done with `docker-compose down`in the same directory.

Running the container once it has been set up is done with `docker-compose up -d` with the modifier `-d` specifying to detach logs from the terminal.

## Set up Designer Launcher

1. In your Ignition gateway, click the “Download Designer Launcher” button and go through the steps to complete the installation.

2. Open your Designer Launcher

3. Click “Add Designer”

4. Click the “Manual” tab on the top of the “Add Designer” window

5. Enter <http://localhost:80>

6. Click “Add Designer”

## Connect Ignition Data Folder with Git Repository

1. Open your desired repository.

2. Open your working project folder in VSCode.

3. Use terminal to `cd ignition_data` folder.

4. Use these commands to commit to the git repository:

```bash
git init
git remote add origin URL/TO/REPO
git fetch
git checkout -t origin/master -f
```
