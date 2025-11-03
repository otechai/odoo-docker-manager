# Odoo Docker Manager

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-required-blue.svg)](https://www.docker.com/)

A robust Python CLI tool for managing Odoo 17 and PostgreSQL 15 Docker containers with ease. Simplify your Odoo development workflow with automated setup, health checks, and powerful management commands.

## 🚀 Features

- **One-Command Setup**: Initialize Odoo environment with secure credentials automatically
- **Docker Management**: Start, stop, restart, and monitor containers effortlessly
- **Health Checks**: Built-in diagnostics and quick testing for all services
- **Addon Management**: Fix common addon issues and manage custom modules
- **Database Operations**: Backup, restore, inspect, and reset databases
- **Security**: Auto-generated secure passwords and best practices
- **Developer-Friendly**: Shell access, log viewing, and SQL execution

## 📋 Prerequisites

- **Docker**: Version 20.10 or higher
- **docker-compose**: Version 1.29 or higher
- **Python**: Version 3.8 or higher
- **Operating System**: Linux, macOS, or Windows with WSL2

### Installation

1. **Install Docker and docker-compose**:
   ```bash
   # Ubuntu/Debian
   sudo apt-get update
   sudo apt-get install docker.io docker-compose
   
   # Start Docker service
   sudo systemctl start docker
   sudo systemctl enable docker
   
   # Add your user to docker group (optional, for non-sudo usage)
   sudo usermod -aG docker $USER
   ```

2. **Clone the repository**:
   ```bash
   git clone https://github.com/otechai/odoo-docker-manager.git
   cd odoo-docker-manager
   ```

3. **Make the script executable**:
   ```bash
   chmod +x odoo_manager.py
   ```

## 🎯 Quick Start

### First-Time Setup

```bash
# Initialize Odoo environment
./odoo_manager.py setup

# Start Odoo
./odoo_manager.py start
```

After 30-60 seconds, Odoo will be available at **http://localhost:8069**

### Daily Workflow

```bash
# Start containers
./odoo_manager.py start

# View logs
./odoo_manager.py logs

# Check status
./odoo_manager.py status

# Stop containers
./odoo_manager.py stop
```

## 📖 Command Reference

### Setup & Initialization

#### `setup`
First-time setup command that:
- Generates `docker-compose.yml` with Odoo 17 and PostgreSQL 15
- Creates `.env` file with secure random passwords
- Creates `addons/` directory for custom modules
- Configures networking and health checks

```bash
./odoo_manager.py setup
```

**Files Created:**
- `docker-compose.yml` - Container orchestration configuration
- `.env` - Environment variables and credentials
- `addons/` - Directory for custom Odoo modules

---

### Container Management

#### `start`
Starts all Odoo containers in detached mode.

```bash
./odoo_manager.py start
```

**What it does:**
- Starts PostgreSQL and Odoo containers
- Waits for services to be ready
- Shows recent logs
- Displays access URL

**Access Odoo at:** http://localhost:8069

---

#### `stop`
Stops all running containers without removing them.

```bash
./odoo_manager.py stop
```

**Use when:** You want to temporarily stop Odoo but keep all data intact.

---

#### `restart`
Restarts all containers.

```bash
./odoo_manager.py restart
```

**Use when:** 
- Configuration changes need to be applied
- Containers are misbehaving
- After addon installation

---

#### `down`
Stops and removes containers but **keeps all data** (volumes persist).

```bash
./odoo_manager.py down
```

**Interactive:** Asks for confirmation before proceeding.

**Use when:** You want to clean up containers but preserve databases and configurations.

---

#### `destroy`
Stops containers and **deletes ALL data** including databases and volumes.

```bash
./odoo_manager.py destroy
```

**⚠️ WARNING:** This is destructive! All databases will be permanently deleted.

**Interactive:** Asks for confirmation before proceeding.

---

### Monitoring & Debugging

#### `logs`
View container logs in real-time.

```bash
# View all logs (follows by default)
./odoo_manager.py logs

# View specific service logs
./odoo_manager.py logs odoo
./odoo_manager.py logs postgres

# View logs without following
./odoo_manager.py logs --no-follow
```

**Tip:** Press `Ctrl+C` to stop following logs.

---

#### `status`
Display comprehensive status information:
- Container status (running/stopped)
- Volume information
- Network configuration
- IP addresses of connected containers

```bash
./odoo_manager.py status
```

**Output includes:**
- Container health
- Volume sizes
- Network connectivity
- Container IP addresses

---

#### `quick-test`
Run a comprehensive health check of all services.

```bash
./odoo_manager.py quick-test
```

**Checks performed:**
1. Docker daemon status
2. Container running state
3. PostgreSQL connectivity
4. Odoo web interface responsiveness
5. Addons directory structure

**Use when:**
- Debugging startup issues
- Verifying installation
- Troubleshooting connectivity

---

### Shell Access

#### `shell`
Open an interactive bash shell inside a container.

```bash
# Open shell in Odoo container (default)
./odoo_manager.py shell

# Open shell in PostgreSQL container
./odoo_manager.py shell postgres
```

**Common uses:**
```bash
# Inside Odoo container
ls /mnt/extra-addons/        # List custom addons
cat /etc/odoo/odoo.conf      # View Odoo configuration
ps aux                       # View running processes

# Inside PostgreSQL container
psql -U odoo                 # Access PostgreSQL CLI
```

**Exit:** Type `exit` or press `Ctrl+D`

---

### Database Operations

#### `backup`
Create a complete backup of database and configuration.

```bash
./odoo_manager.py backup
```

**Creates:**
- `backups/odoo_backup_YYYYMMDD_HHMMSS.tar.gz`

**Includes:**
- Full PostgreSQL database dump
- `.env` file (credentials)
- `docker-compose.yml`
- `addons/` directory

**Restore instructions:**
```bash
# Extract backup
tar -xzf backups/odoo_backup_20241103_120000.tar.gz

# Restart containers
./odoo_manager.py restart
```

---

#### `reinstall-db`
Drop and recreate the Odoo database while keeping containers running.

```bash
./odoo_manager.py reinstall-db
```

**⚠️ WARNING:** Deletes all Odoo data!

**Interactive:** Asks for confirmation before proceeding.

**Use when:**
- You want a fresh Odoo instance
- Database corruption occurs
- Testing fresh installations

---

#### `exec-sql`
Execute SQL queries directly on the PostgreSQL database.

```bash
./odoo_manager.py exec-sql "SELECT * FROM ir_module_module LIMIT 5;"
```

**Examples:**
```bash
# List all installed modules
./odoo_manager.py exec-sql "SELECT name, state FROM ir_module_module WHERE state='installed';"

# Count users
./odoo_manager.py exec-sql "SELECT COUNT(*) FROM res_users;"

# List databases
./odoo_manager.py exec-sql "\l"
```

**Security note:** Be careful with destructive queries (DELETE, DROP, etc.)

---

#### `inspect-db`
List all tables in the Odoo database.

```bash
./odoo_manager.py inspect-db
```

**Output:** Complete list of database tables with schema information.

**Use when:**
- Understanding database structure
- Debugging custom modules
- Database troubleshooting

---

#### `reset-admin`
Reset the admin user password to a secure random password.

```bash
./odoo_manager.py reset-admin
```

**Generates:** 16-character secure random password

**Use when:**
- Forgot admin password
- Security breach
- Testing access control

---

### Addon Management

#### `fix`
Diagnose and fix common addon issues automatically.

```bash
./odoo_manager.py fix
```

**What it does:**
1. Checks if containers are running
2. Validates addon directory structure
3. Verifies `__manifest__.py` files
4. Fixes file permissions (755)
5. Restarts Odoo container
6. Displays troubleshooting steps

**After running:**
1. Wait 30 seconds for Odoo restart
2. Go to **Apps > Update Apps List** (Developer mode required)
3. Remove 'Apps' filter
4. Search for your module

**Enable Developer Mode:**
- Settings > Activate the developer mode
- Or add `?debug=1` to URL

---

### Maintenance

#### `update`
Pull latest container images from Docker Hub.

```bash
./odoo_manager.py update
```

**Updates:**
- Odoo 17 image
- PostgreSQL 15 image

**Note:** Run `restart` after updating to use new images.

---

#### `clean`
Clean up unused Docker resources (images, containers, networks).

```bash
./odoo_manager.py clean
```

**Removes:**
- Stopped containers
- Unused networks
- Dangling images
- Build cache

**Use when:**
- Running low on disk space
- Cleaning up after experiments

---

### Nuclear Options

#### `nuke`
**⚠️ EXTREME CAUTION:** Completely destroy everything and start fresh.

```bash
./odoo_manager.py nuke
```

**Destroys:**
- All containers (running and stopped)
- All volumes and data
- All networks
- Docker system cache

**Interactive:** Asks for multiple confirmations.

**Then offers:** Fresh setup automatically.

**Use when:**
- Complete reset needed
- Unrecoverable errors
- Starting from scratch

---

## 🗂️ Directory Structure

```
odoo-docker-manager/
├── odoo_manager.py          # Main CLI script
├── docker-compose.yml       # Generated by setup
├── .env                     # Generated by setup (credentials)
├── addons/                  # Custom Odoo modules
│   └── my_custom_module/
│       ├── __init__.py
│       ├── __manifest__.py
│       └── ...
└── backups/                 # Created by backup command
    └── odoo_backup_*.tar.gz
```

---

## 🔧 Configuration

### Environment Variables (.env)

Generated automatically by `setup` command:

```bash
# PostgreSQL Configuration
POSTGRES_DB=postgres
POSTGRES_USER=odoo
POSTGRES_PASSWORD=<secure-random-32-chars>

# Odoo Configuration
HOST=postgres
USER=odoo
PASSWORD=<secure-random-32-chars>
```

**Security:** The `.env` file contains sensitive credentials. Never commit it to version control.

### Docker Compose Configuration

The `docker-compose.yml` defines:

- **PostgreSQL 15** with persistent volume
- **Odoo 17** connected to PostgreSQL
- **Network**: Internal bridge network
- **Ports**: 8069 bound to localhost only (127.0.0.1:8069)
- **Volumes**: 
  - Database data
  - Odoo data
  - Custom addons mounted at `/mnt/extra-addons`

---

## 🎨 Custom Addons

### Creating a Custom Module

1. **Create module directory:**
   ```bash
   mkdir -p addons/my_module
   cd addons/my_module
   ```

2. **Create `__init__.py`:**
   ```python
   from . import models
   ```

3. **Create `__manifest__.py`:**
   ```python
   {
       'name': 'My Module',
       'version': '17.0.1.0.0',
       'depends': ['base'],
       'author': 'Your Name',
       'category': 'Custom',
       'description': """
           My custom Odoo module
       """,
       'data': [],
       'installable': True,
       'application': False,
   }
   ```

4. **Fix permissions and reload:**
   ```bash
   ./odoo_manager.py fix
   ```

5. **Install in Odoo:**
   - Enable Developer Mode
   - Go to Apps > Update Apps List
   - Search for "My Module"
   - Click Install

---

## 🐛 Troubleshooting

### Containers won't start

```bash
# Check Docker is running
sudo systemctl status docker

# Check logs for errors
./odoo_manager.py logs

# Verify configuration
./odoo_manager.py status

# Run health check
./odoo_manager.py quick-test
```

### Addon not appearing in Apps list

```bash
# Fix common issues
./odoo_manager.py fix

# Check addon structure
ls -la addons/my_module/
cat addons/my_module/__manifest__.py

# Restart Odoo
./odoo_manager.py restart

# In Odoo UI:
# 1. Enable Developer Mode
# 2. Apps > Update Apps List
# 3. Remove 'Apps' filter
# 4. Search for your module
```

### Database connection errors

```bash
# Check PostgreSQL is ready
./odoo_manager.py quick-test

# Restart containers
./odoo_manager.py restart

# Check PostgreSQL logs
./odoo_manager.py logs postgres

# Test database connection
./odoo_manager.py exec-sql "\l"
```

### Port 8069 already in use

```bash
# Find process using port 8069
sudo lsof -i :8069

# Kill the process
sudo kill -9 <PID>

# Or change port in docker-compose.yml
# Change "127.0.0.1:8069:8069" to "127.0.0.1:8070:8069"
```

### Permission denied errors

```bash
# Fix addon permissions
./odoo_manager.py fix

# Or manually:
chmod -R 755 addons/
```

### Clean slate (nuclear option)

```bash
# Destroy everything and start fresh
./odoo_manager.py nuke
```

---

## 🔒 Security Best Practices

1. **Passwords**: Script generates secure 32-character random passwords automatically
2. **Port binding**: Odoo bound to localhost only (127.0.0.1:8069)
3. **Credentials**: Never commit `.env` file to version control
4. **Updates**: Regularly update images with `./odoo_manager.py update`
5. **Backups**: Create regular backups with `./odoo_manager.py backup`
6. **Production**: Use reverse proxy (nginx) with SSL for production deployments

### .gitignore

Add these to your `.gitignore`:

```gitignore
.env
backups/
*.pyc
__pycache__/
```

---

## 🚀 Advanced Usage

### Running Multiple Odoo Instances

To run multiple Odoo instances, use different directories:

```bash
# Instance 1
mkdir odoo-dev
cd odoo-dev
../odoo_manager.py -d . setup
../odoo_manager.py -d . start

# Instance 2 (change port in docker-compose.yml first)
mkdir odoo-staging
cd odoo-staging
# Edit docker-compose.yml: change port to 8070:8069
../odoo_manager.py -d . setup
../odoo_manager.py -d . start
```

### Automated Backups

Create a cron job for automated backups:

```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * cd /path/to/odoo-docker-manager && ./odoo_manager.py backup
```

### Custom Docker Compose Configuration

You can modify `docker-compose.yml` after generation:

```yaml
# Add custom environment variables
odoo:
  environment:
    - ODOO_LOG_LEVEL=debug
    
# Add additional volumes
volumes:
  - ./config:/etc/odoo

# Change Odoo version
odoo:
  image: odoo:16  # Use Odoo 16 instead
```

---

## 📊 System Requirements

### Minimum Requirements
- **CPU**: 2 cores
- **RAM**: 2 GB
- **Disk**: 10 GB free space
- **OS**: Linux (Ubuntu 20.04+, Debian 10+, CentOS 7+)

### Recommended Requirements
- **CPU**: 4+ cores
- **RAM**: 4+ GB
- **Disk**: 50+ GB SSD
- **OS**: Ubuntu 22.04 LTS or Debian 11+

---

## 🤝 Contributing

Contributions are welcome! This project is licensed under AGPL v3.

### How to Contribute

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -am 'Add feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a Pull Request

### Reporting Issues

Please report issues on GitHub with:
- Operating system and version
- Python version
- Docker and docker-compose versions
- Complete error messages
- Steps to reproduce

---

## 📄 License

This project is licensed under the **GNU Affero General Public License v3.0 (AGPL-3.0)**.

### What this means:

- ✅ **Freedom to use**: Use this software for any purpose
- ✅ **Freedom to study**: Study and modify the source code
- ✅ **Freedom to share**: Distribute copies of the software
- ✅ **Freedom to improve**: Distribute modified versions
- ⚠️ **Network use is distribution**: If you run a modified version on a server and let others interact with it, you must share your modifications
- ⚠️ **Copyleft**: Derivative works must also be AGPL-licensed

See the [LICENSE](LICENSE) file for full terms.

---

## 🙏 Acknowledgments

- **Odoo SA** - For the amazing Odoo ERP system
- **PostgreSQL Global Development Group** - For PostgreSQL database
- **Docker Inc.** - For containerization technology

---

## 📞 Support

- **GitHub Issues**: [Report bugs or request features](https://github.com/otechai/odoo-docker-manager/issues)
- **Odoo Documentation**: https://www.odoo.com/documentation/17.0/
- **Docker Documentation**: https://docs.docker.com/

---

## 🔄 Changelog

### Version 1.0.0 (2024-11-03)
- Initial release
- Docker-based Odoo 17 and PostgreSQL 15 setup
- Complete CLI management interface
- Automated backup and restore
- Addon management and troubleshooting
- Health check system
- Database operations
- Nuclear reset option

---

**Made with ❤️ for the Odoo community**
