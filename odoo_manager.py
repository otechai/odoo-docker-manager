#!/usr/bin/env python3
"""
Odoo Docker Manager - Robust Python CLI
Manages Odoo and PostgreSQL Docker containers with proper error handling
Enhanced with rapid prototyping features
"""

import os
import sys
import subprocess
import secrets
import string
import argparse
import time
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, List


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


class OdooDockerManager:
    """Main manager class for Odoo Docker operations"""

    def __init__(self, directory: Optional[str] = None):
        self.script_dir = Path(directory) if directory else Path.cwd()
        self.compose_file = self.script_dir / 'docker-compose.yml'
        self.env_file = self.script_dir / '.env'
        self.addons_dir = self.script_dir / 'addons'
        self.backup_dir = self.script_dir / 'backups'

    @staticmethod
    def print_header():
        """Print application header"""
        print()
        print(f"{Colors.BLUE}{'=' * 50}{Colors.RESET}")
        print(f"{Colors.BLUE}{Colors.BOLD}  Odoo Docker Manager{Colors.RESET}")
        print(f"{Colors.BLUE}{'=' * 50}{Colors.RESET}")
        print()

    @staticmethod
    def print_success(message: str):
        """Print success message"""
        print(f"{Colors.GREEN}✓ {message}{Colors.RESET}")

    @staticmethod
    def print_error(message: str):
        """Print error message"""
        print(f"{Colors.RED}✗ {message}{Colors.RESET}", file=sys.stderr)

    @staticmethod
    def print_info(message: str):
        """Print info message"""
        print(f"{Colors.YELLOW}→ {message}{Colors.RESET}")

    @staticmethod
    def print_warning(message: str):
        """Print warning message"""
        print(f"{Colors.YELLOW}⚠ {message}{Colors.RESET}")

    @staticmethod
    def generate_password(length: int = 32) -> str:
        """Generate a secure random password"""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))

    def run_command(self, cmd: List[str], capture_output: bool = False, 
                   check: bool = True) -> subprocess.CompletedProcess:
        """Run a shell command with error handling"""
        try:
            result = subprocess.run(
                cmd,
                cwd=self.script_dir,
                capture_output=capture_output,
                text=True,
                check=check
            )
            return result
        except subprocess.CalledProcessError as e:
            self.print_error(f"Command failed: {' '.join(cmd)}")
            if e.stderr:
                self.print_error(f"Error: {e.stderr}")
            if check:
                sys.exit(1)
            return e
        except FileNotFoundError:
            self.print_error(f"Command not found: {cmd[0]}")
            self.print_info("Make sure Docker and docker-compose are installed")
            sys.exit(1)

    def check_docker(self) -> bool:
        """Check if Docker is installed and running"""
        try:
            result = self.run_command(['docker', 'info'], capture_output=True, check=False)
            if result.returncode != 0:
                self.print_error("Docker is not running")
                self.print_info("Start Docker with: sudo systemctl start docker")
                return False
            return True
        except Exception as e:
            self.print_error(f"Docker check failed: {e}")
            return False

    def check_docker_compose(self) -> bool:
        """Check if docker-compose is installed"""
        result = self.run_command(['docker-compose', '--version'], 
                                 capture_output=True, check=False)
        return result.returncode == 0

    def confirm_action(self, message: str) -> bool:
        """Ask user for confirmation"""
        response = input(f"{Colors.YELLOW}{message} (y/N): {Colors.RESET}").strip().lower()
        return response in ['y', 'yes']

    def generate_env(self, overwrite: bool = False):
        """Generate .env file with secure credentials"""
        self.print_info("Generating .env file...")

        if self.env_file.exists() and not overwrite:
            if not self.confirm_action("⚠ .env already exists. Overwrite?"):
                self.print_info("Skipping .env generation")
                return

        password = self.generate_password()

        env_content = f"""# PostgreSQL Configuration
POSTGRES_DB=postgres
POSTGRES_USER=odoo
POSTGRES_PASSWORD={password}

# Odoo Configuration
HOST=postgres
USER=odoo
PASSWORD={password}
"""

        try:
            self.env_file.write_text(env_content)
            self.print_success("Generated .env file with secure password")
        except IOError as e:
            self.print_error(f"Failed to write .env file: {e}")
            sys.exit(1)

    def generate_compose(self, overwrite: bool = False):
        """Generate docker-compose.yml file"""
        self.print_info("Generating docker-compose.yml...")

        if self.compose_file.exists() and not overwrite:
            if not self.confirm_action("⚠ docker-compose.yml already exists. Overwrite?"):
                self.print_info("Skipping docker-compose.yml generation")
                return

        compose_content = """version: '3.8'

services:
  postgres:
    image: postgres:15
    container_name: odoo_postgres
    env_file: .env
    volumes:
      - db_data:/var/lib/postgresql/data
    networks:
      - odoo_network
    restart: always
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U odoo"]
      interval: 10s
      timeout: 5s
      retries: 5

  odoo:
    image: odoo:17
    container_name: odoo_app
    env_file: .env
    depends_on:
      postgres:
        condition: service_healthy
    ports:
      - "127.0.0.1:8069:8069"
    volumes:
      - odoo_data:/var/lib/odoo
      - ./addons:/mnt/extra-addons
    networks:
      - odoo_network
    restart: always

networks:
  odoo_network:
    driver: bridge

volumes:
  db_data:
  odoo_data:
"""

        try:
            self.compose_file.write_text(compose_content)
            self.print_success("Generated docker-compose.yml")
        except IOError as e:
            self.print_error(f"Failed to write docker-compose.yml: {e}")
            sys.exit(1)

    def setup(self):
        """Setup Odoo Docker environment"""
        self.print_header()
        self.print_info("Setting up Odoo Docker environment...")

        if not self.check_docker():
            sys.exit(1)

        if not self.check_docker_compose():
            self.print_error("docker-compose is not installed")
            self.print_info("Install it with: sudo apt-get install docker-compose")
            sys.exit(1)

        # Generate configuration files
        self.generate_compose()
        self.generate_env()

        # Create addons directory
        if not self.addons_dir.exists():
            self.addons_dir.mkdir(parents=True)
            self.print_success("Created addons directory")

        self.print_success("Setup complete!")
        print()
        self.print_info(f"Run '{sys.argv[0]} start' to start Odoo")

    def start(self):
        """Start Odoo containers"""
        self.print_header()
        self.print_info("Starting Odoo...")

        if not self.compose_file.exists():
            self.print_error("docker-compose.yml not found")
            self.print_info(f"Run '{sys.argv[0]} setup' first")
            sys.exit(1)

        if not self.check_docker():
            sys.exit(1)

        self.run_command(['docker-compose', 'up', '-d'])

        self.print_success("Odoo is starting...")
        print()
        self.print_info("Waiting for services to be ready (30-60 seconds)...")
        time.sleep(10)

        # Show recent logs
        self.run_command(['docker-compose', 'logs', '--tail=20'])

        print()
        self.print_success("Odoo should be available at: http://localhost:8069")
        self.print_info(f"Check logs with: {sys.argv[0]} logs")

    def stop(self):
        """Stop Odoo containers"""
        self.print_header()
        self.print_info("Stopping Odoo...")
        self.run_command(['docker-compose', 'stop'])
        self.print_success("Odoo stopped")

    def restart(self):
        """Restart Odoo containers"""
        self.print_header()
        self.print_info("Restarting Odoo...")
        self.run_command(['docker-compose', 'restart'])
        self.print_success("Odoo restarted")
        self.print_info(f"Check status with: {sys.argv[0]} status")

    def down(self):
        """Stop and remove containers"""
        self.print_header()
        if self.confirm_action("⚠ This will stop and remove all containers. Continue?"):
            self.run_command(['docker-compose', 'down'])
            self.print_success("Containers removed")
        else:
            self.print_info("Cancelled")

    def destroy(self):
        """Stop containers and delete all data"""
        self.print_header()
        self.print_warning("WARNING: This will DELETE ALL DATA including databases!")
        if self.confirm_action("Are you absolutely sure?"):
            self.run_command(['docker-compose', 'down', '-v'])
            self.print_success("All data destroyed")
        else:
            self.print_info("Cancelled")

    def logs(self, service: Optional[str] = None, follow: bool = True):
        """Show container logs"""
        cmd = ['docker-compose', 'logs']
        if follow:
            cmd.append('-f')
        cmd.extend(['--tail=100'])
        if service:
            cmd.append(service)
        
        try:
            self.run_command(cmd)
        except KeyboardInterrupt:
            print()
            self.print_info("Stopped following logs")

    def status(self):
        """Show container and network status"""
        self.print_header()
        print(f"{Colors.BLUE}Container Status:{Colors.RESET}")
        self.run_command(['docker-compose', 'ps'])
        
        print()
        print(f"{Colors.BLUE}Volume Status:{Colors.RESET}")
        self.run_command(['docker', 'volume', 'ls', '--filter', 'name=odoo'])
        
        print()
        print(f"{Colors.BLUE}Network Status:{Colors.RESET}")
        result = self.run_command(
            ['docker', 'network', 'inspect', 'odoo_odoo_network'],
            capture_output=True,
            check=False
        )
        if result.returncode == 0:
            try:
                network_info = json.loads(result.stdout)
                if network_info and 'Containers' in network_info[0]:
                    containers = network_info[0]['Containers']
                    print(f"Connected containers: {len(containers)}")
                    for container in containers.values():
                        print(f"  - {container['Name']}: {container['IPv4Address']}")
            except (json.JSONDecodeError, KeyError, IndexError):
                print("Network found but couldn't parse details")
        else:
            print("Network not found or not created yet")

    def shell(self, service: str = 'odoo'):
        """Open shell in container"""
        self.print_info(f"Opening shell in {service} container...")
        self.run_command(['docker-compose', 'exec', service, '/bin/bash'])

    def backup(self):
        """Backup database and configuration"""
        self.print_header()
        self.backup_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        db_backup = self.backup_dir / f"db_{timestamp}.sql"
        tar_backup = self.backup_dir / f"odoo_backup_{timestamp}.tar.gz"
        
        self.print_info("Creating database backup...")
        
        # Backup database
        with open(db_backup, 'w') as f:
            result = self.run_command(
                ['docker-compose', 'exec', '-T', 'postgres', 'pg_dumpall', '-U', 'odoo'],
                capture_output=True,
                check=False
            )
            if result.returncode == 0:
                f.write(result.stdout)
                self.print_success(f"Database backup created: {db_backup}")
            else:
                self.print_error("Database backup failed")
                return
        
        # Create tarball
        self.print_info("Creating complete backup archive...")
        files_to_backup = ['.env', 'docker-compose.yml', 'addons', str(db_backup)]
        tar_cmd = ['tar', '-czf', str(tar_backup), '-C', str(self.script_dir)]
        
        # Add only existing files
        for file in files_to_backup:
            file_path = self.script_dir / file
            if file_path.exists():
                tar_cmd.append(file)
        
        self.run_command(tar_cmd, check=False)
        
        # Cleanup temporary DB backup
        db_backup.unlink()
        
        self.print_success(f"Backup created: {tar_backup}")
        print()
        self.print_info(f"Backup size: {tar_backup.stat().st_size / 1024 / 1024:.2f} MB")

    def clean(self):
        """Clean up Docker resources"""
        self.print_header()
        self.print_info("Cleaning up Docker resources...")
        self.run_command(['docker', 'system', 'prune', '-f'])
        self.print_success("Cleanup complete")

    def update(self):
        """Update container images"""
        self.print_header()
        self.print_info("Updating container images...")
        self.run_command(['docker-compose', 'pull'])
        self.print_success("Images updated")
        self.print_info("Run 'restart' to use updated images")

    def fix(self):
        """Fix common Odoo addon issues"""
        self.print_header()
        self.print_info("Running diagnostics and fixes...")
        
        # Check if containers are running
        if not self._container_running('odoo_app'):
            self.print_error("Odoo container is not running. Start it first.")
            return
        
        # Check addons directory
        if not self.addons_dir.exists():
            self.print_error("Addons directory not found")
            return
        
        addons = [d for d in self.addons_dir.iterdir() if d.is_dir() and not d.name.startswith('.')]
        
        if not addons:
            self.print_warning("No addons found in addons directory")
            return
        
        print()
        self.print_info(f"Found {len(addons)} addon(s):")
        for addon in addons:
            manifest = addon / '__manifest__.py'
            if manifest.exists():
                print(f"  ✓ {addon.name}")
            else:
                print(f"  ✗ {addon.name} (missing __manifest__.py)")
        
        print()
        self.print_info("Checking file permissions...")
        
        # Fix permissions
        self.run_command(['chmod', '-R', '755', str(self.addons_dir)], check=False)
        self.print_success("Permissions fixed")
        
        print()
        self.print_info("Restarting Odoo to reload addons path...")
        self.run_command(['docker-compose', 'restart', 'odoo'], check=False)
        
        print()
        self.print_success("Fixes applied!")
        print()
        print(f"{Colors.YELLOW}Next steps:{Colors.RESET}")
        print("  1. Wait 30 seconds for Odoo to restart")
        print("  2. Go to: Apps > Update Apps List (Developer mode required)")
        print("  3. Remove 'Apps' filter and search for your module")
        print("  4. If still not visible, check logs with: ./odoo_manager.py logs")
        print()
        print(f"{Colors.CYAN}Enable Developer Mode:{Colors.RESET}")
        print("  Settings > Activate the developer mode")
        print("  Or add ?debug=1 to your URL")

    def _container_running(self, name: str) -> bool:
        """Check if a container is running"""
        result = self.run_command(
            ['docker', 'ps', '--filter', f'name={name}', '--format', '{{.Names}}'],
            capture_output=True, check=False
        )
        return name in result.stdout

    def nuke(self):
        """Nuclear option: destroy everything and start fresh"""
        self.print_header()
        self.print_warning("⚠️  NUCLEAR OPTION: This will:")
        print("   - Stop all containers")
        print("   - Delete ALL Odoo databases")
        print("   - Remove ALL volumes")
        print("   - Remove ALL networks")
        print("   - Clean Docker system")
        print()
        
        if not self.confirm_action("Are you ABSOLUTELY sure you want to proceed?"):
            self.print_info("Cancelled")
            return
        
        self.print_info("Nuking everything...")
        
        # Destroy everything
        self.run_command(['docker-compose', 'down', '-v', '--remove-orphans'], check=False)
        
        # Remove containers
        result = self.run_command(
            ['docker', 'ps', '-a', '--filter', 'name=odoo', '--format', '{{.Names}}'],
            capture_output=True, check=False
        )
        if result.stdout.strip():
            for container in result.stdout.strip().split('\n'):
                if container:
                    self.run_command(['docker', 'rm', '-f', container], check=False)
        
        # Remove volumes
        result = self.run_command(
            ['docker', 'volume', 'ls', '--filter', 'name=odoo', '--format', '{{.Name}}'],
            capture_output=True, check=False
        )
        if result.stdout.strip():
            for volume in result.stdout.strip().split('\n'):
                if volume:
                    self.run_command(['docker', 'volume', 'rm', volume], check=False)
        
        # Remove networks (silently ignore if not found)
        networks_to_remove = ['odoo_odoo_network', 'odoo_default', 'odoo2_odoo_network']
        for network in networks_to_remove:
            result = self.run_command(
                ['docker', 'network', 'rm', network],
                capture_output=True,
                check=False
            )
            if result.returncode == 0:
                self.print_success(f"Network removed: {network}")
        
        # System prune
        self.run_command(['docker', 'system', 'prune', '-af', '--volumes'], check=False)
        
        self.print_success("Everything nuked! 💥")
        print()
        if self.confirm_action("Start fresh setup now?"):
            self.setup()

    def reinstall_db(self):
        """Reinstall Odoo database (keep containers running)"""
        self.print_header()
        self.print_warning("⚠️  This will DROP and recreate the Odoo database")
        self.print_info("Containers will keep running")
        print()
        
        if not self.confirm_action("Continue with database reinstall?"):
            self.print_info("Cancelled")
            return
        
        if not self._container_running('odoo_app'):
            self.print_error("Odoo container is not running")
            return
        
        self.print_info("Dropping database...")
        result = self.run_command(
            ['docker-compose', 'exec', '-T', 'postgres', 'psql', '-U', 'odoo', 
             '-c', 'DROP DATABASE IF EXISTS postgres;'],
            capture_output=True, check=False
        )
        
        if result.returncode == 0:
            self.print_success("Database dropped")
            print()
            self.print_info("Odoo will reinitialize on next restart...")
            print()
            self.print_info("Restarting Odoo container...")
            self.run_command(['docker-compose', 'restart', 'odoo'], check=False)
            time.sleep(10)
            self.print_success("Database reinstalled!")
        else:
            self.print_error("Failed to drop database")

    def exec_sql(self, query: str):
        """Execute SQL query in PostgreSQL"""
        self.print_header()
        
        if not self._container_running('odoo_postgres'):
            self.print_error("PostgreSQL container is not running")
            return
        
        self.print_info(f"Executing query: {query}")
        result = self.run_command(
            ['docker-compose', 'exec', '-T', 'postgres', 'psql', '-U', 'odoo', '-c', query],
            capture_output=True, check=False
        )
        
        if result.returncode == 0:
            print(result.stdout)
            self.print_success("Query executed successfully")
        else:
            self.print_error(f"Query failed: {result.stderr}")

    def inspect_db(self):
        """Inspect Odoo database structure and tables"""
        self.print_header()
        
        if not self._container_running('odoo_postgres'):
            self.print_error("PostgreSQL container is not running")
            return
        
        self.print_info("Listing all tables in Odoo database...")
        result = self.run_command(
            ['docker-compose', 'exec', '-T', 'postgres', 'psql', '-U', 'odoo', 
             '-c', r"\dt 'public.*'"],
            capture_output=True, check=False
        )
        
        if result.returncode == 0:
            print(result.stdout)
        else:
            self.print_error(f"Failed to list tables: {result.stderr}")

    def quick_test(self):
        """Run quick connectivity and health check"""
        self.print_header()
        print(f"{Colors.CYAN}Running Quick Health Check...{Colors.RESET}")
        print()
        
        # Check Docker
        print(f"{Colors.BLUE}[1/5] Checking Docker...{Colors.RESET}")
        if self.check_docker():
            self.print_success("Docker is running")
        else:
            self.print_error("Docker check failed")
            return
        
        # Check containers
        print(f"{Colors.BLUE}[2/5] Checking containers...{Colors.RESET}")
        result = self.run_command(
            ['docker-compose', 'ps', '--services', '--filter', 'status=running'],
            capture_output=True, check=False
        )
        if result.returncode == 0:
            services = result.stdout.strip().split('\n')
            if 'postgres' in services and 'odoo' in services:
                self.print_success("All containers running")
            else:
                self.print_error("Some containers are not running")
        
        # Check PostgreSQL
        print(f"{Colors.BLUE}[3/5] Checking PostgreSQL...{Colors.RESET}")
        result = self.run_command(
            ['docker-compose', 'exec', '-T', 'postgres', 'pg_isready', '-U', 'odoo'],
            capture_output=True, check=False
        )
        if result.returncode == 0:
            self.print_success("PostgreSQL is ready")
        else:
            self.print_error("PostgreSQL connection failed")
        
        # Check Odoo web interface
        print(f"{Colors.BLUE}[4/5] Checking Odoo web interface...{Colors.RESET}")
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('127.0.0.1', 8069))
            sock.close()
            if result == 0:
                self.print_success("Odoo web port is responding")
            else:
                self.print_warning("Odoo web port not responding yet (may still be starting)")
        except Exception as e:
            self.print_warning(f"Could not check web port: {e}")
        
        # Check addons
        print(f"{Colors.BLUE}[5/5] Checking addons...{Colors.RESET}")
        if self.addons_dir.exists():
            addon_count = len([d for d in self.addons_dir.iterdir() if d.is_dir() and not d.name.startswith('.')])
            self.print_success(f"Addons directory found ({addon_count} addon folders)")
        else:
            self.print_warning("Addons directory not found")
        
        print()
        self.print_success("Health check complete!")

    def reset_admin(self):
        """Reset admin user password"""
        self.print_header()
        self.print_warning("⚠️  This will reset the admin user password")
        print()
        
        if not self._container_running('odoo_app'):
            self.print_error("Odoo container is not running")
            return
        
        new_password = self.generate_password(length=16)
        
        self.print_info("Resetting admin password...")
        query = f"UPDATE res_users SET password_crypt = crypt('{new_password}', gen_salt('bf')) WHERE login = 'admin';"
        
        result = self.run_command(
            ['docker-compose', 'exec', '-T', 'postgres', 'psql', '-U', 'odoo', '-c', query],
            capture_output=True, check=False
        )
        
        if result.returncode == 0:
            self.print_success("Admin password reset!")
            print()
            print(f"{Colors.CYAN}New credentials:{Colors.RESET}")
            print(f"  Username: admin")
            print(f"  Password: {new_password}")
        else:
            self.print_error(f"Failed to reset password: {result.stderr}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Odoo Docker Manager - Manage Odoo and PostgreSQL containers',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  setup        - First time setup (generates docker-compose.yml and .env)
  start        - Start Odoo containers
  stop         - Stop Odoo containers
  restart      - Restart Odoo containers
  down         - Stop and remove containers (keeps data)
  destroy      - Stop containers and delete ALL data
  logs         - View container logs
  status       - Show container and network status
  shell        - Open bash shell in container
  backup       - Backup database and configuration
  clean        - Clean up Docker resources
  update       - Update container images
  nuke         - ⚠️  NUCLEAR: Destroy everything and start fresh
  fix          - Fix common addon issues and restart Odoo
  reinstall-db - Reinstall database (containers stay running)
  quick-test   - Run health check on all services
  reset-admin  - Reset admin user password
  exec-sql     - Execute SQL query
  inspect-db   - Inspect database tables

Examples:
  %(prog)s setup                                      First time setup
  %(prog)s start                                      Start Odoo
  %(prog)s stop                                       Stop Odoo
  %(prog)s restart                                    Restart Odoo
  %(prog)s logs                                       View all logs (follow mode)
  %(prog)s logs odoo                                  View Odoo logs only
  %(prog)s logs --no-follow                           View logs without following
  %(prog)s status                                     Show container status
  %(prog)s shell                                      Open shell in Odoo container
  %(prog)s shell postgres                             Open shell in PostgreSQL
  %(prog)s backup                                     Backup database and config
  %(prog)s down                                       Stop and remove containers
  %(prog)s destroy                                    Stop and delete all data
  %(prog)s clean                                      Clean Docker resources
  %(prog)s update                                     Update container images
  %(prog)s nuke                                       ⚠️  Nuclear option
  %(prog)s fix                                        Fix addon issues
  %(prog)s reinstall-db                               Reinstall database
  %(prog)s quick-test                                 Run health check
  %(prog)s reset-admin                                Reset admin password
  %(prog)s exec-sql "SELECT * FROM ir_module_module;" Execute SQL
  %(prog)s inspect-db                                 Show database tables
        """
    )
    
    parser.add_argument(
        'command',
        choices=['setup', 'start', 'stop', 'restart', 'down', 'destroy', 
                'logs', 'status', 'shell', 'backup', 'clean', 'update', 'nuke', 
                'fix', 'reinstall-db', 'quick-test', 'reset-admin', 'exec-sql', 'inspect-db'],
        help='Command to execute'
    )
    
    parser.add_argument(
        'service',
        nargs='?',
        help='Service name (for logs/shell) or SQL query (for exec-sql)'
    )
    
    parser.add_argument(
        '-d', '--directory',
        help='Working directory (default: current directory)'
    )
    
    parser.add_argument(
        '--no-follow',
        action='store_true',
        help='Don\'t follow logs (for logs command)'
    )
    
    args = parser.parse_args()
    
    # Create manager instance
    manager = OdooDockerManager(args.directory)
    
    # Execute command
    try:
        if args.command == 'setup':
            manager.setup()
        elif args.command == 'start':
            manager.start()
        elif args.command == 'stop':
            manager.stop()
        elif args.command == 'restart':
            manager.restart()
        elif args.command == 'down':
            manager.down()
        elif args.command == 'destroy':
            manager.destroy()
        elif args.command == 'logs':
            manager.logs(args.service, follow=not args.no_follow)
        elif args.command == 'status':
            manager.status()
        elif args.command == 'shell':
            service = args.service or 'odoo'
            manager.shell(service)
        elif args.command == 'backup':
            manager.backup()
        elif args.command == 'clean':
            manager.clean()
        elif args.command == 'update':
            manager.update()
        elif args.command == 'nuke':
            manager.nuke()
        elif args.command == 'fix':
            manager.fix()
        elif args.command == 'reinstall-db':
            manager.reinstall_db()
        elif args.command == 'quick-test':
            manager.quick_test()
        elif args.command == 'reset-admin':
            manager.reset_admin()
        elif args.command == 'exec-sql':
            if not args.service:
                manager.print_error("SQL query is required. Use: exec-sql \"SELECT * FROM ...\"")
                sys.exit(1)
            manager.exec_sql(args.service)
        elif args.command == 'inspect-db':
            manager.inspect_db()
    except KeyboardInterrupt:
        print()
        manager.print_info("Operation cancelled")
        sys.exit(0)
    except Exception as e:
        manager.print_error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
