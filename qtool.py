import os
from datetime import timedelta
from typing import Dict, Any, Optional

import click
import configparser
import tabulate
from couchbase.auth import PasswordAuthenticator
from couchbase.cluster import Cluster, ClusterOptions, ClusterTimeoutOptions, QueryOptions
from couchbase.exceptions import CouchbaseException, ParsingFailedException

APP_NAME = 'qtool'
BASE_DIR = os.path.realpath(os.path.dirname(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, '.configs.ini')


class ConfigManager:
    """Manages configuration file operations"""
    
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.parser = configparser.ConfigParser()
        self._ensure_config_file()
    
    def _ensure_config_file(self):
        """Ensure the config file and section exist"""
        if not os.path.exists(self.config_path):
            self.parser['CLUSTER'] = {}
            self._write_config()
        else:
            self.parser.read(self.config_path)
            if 'CLUSTER' not in self.parser:
                self.parser['CLUSTER'] = {}
    
    def _write_config(self):
        """Write config to file"""
        with open(self.config_path, 'w') as configfile:
            self.parser.write(configfile, space_around_delimiters=False)
    
    def get(self, section: str, option: str, default: Any = None) -> Any:
        """Get a configuration value"""
        self.parser.read(self.config_path)
        try:
            return self.parser.get(section, option)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return default
    
    def set(self, section: str, option: str, value: str) -> None:
        """Set a configuration value"""
        self.parser.read(self.config_path)
        if section not in self.parser:
            self.parser[section] = {}
        self.parser.set(section, option, str(value))
        self._write_config()


class CouchbaseClient:
    """Handles Couchbase connection and query execution"""
    
    def __init__(self, address: str, username: str, password: str):
        self.address = address
        self.username = username
        self.password = password
        self.cluster: Optional[Cluster] = None
    
    def connect(self) -> bool:
        """Establish connection to Couchbase cluster"""
        try:
            click.secho(f"CONNECTING TO '{self.address}'", fg='green')
            
            timeout_options = ClusterTimeoutOptions(
                kv_timeout=timedelta(seconds=5),
                query_timeout=timedelta(seconds=10)
            )
            
            auth = PasswordAuthenticator(self.username, self.password)
            cluster_options = ClusterOptions(auth, timeout_options=timeout_options)
            
            self.cluster = Cluster.connect(
                f"couchbase://{self.address}",
                cluster_options
            )
            
            return True
            
        except CouchbaseException as e:
            click.secho(f"Connection failed: {e}", fg='red')
            return False
    
    def execute_query(self, query: str) -> None:
        """Execute a N1QL query and display results"""
        if not self.cluster:
            raise RuntimeError("Not connected to cluster")
        
        try:
            click.secho(f"Executing query: {query}", fg='yellow')
            result = self.cluster.query(query, QueryOptions(metrics=True))
            
            # Display results
            self._display_results(result)
            
            # Display execution metrics
            metrics = result.metadata().metrics()
            if metrics:
                click.secho(f"\nExecution time: {metrics.execution_time()}", fg='yellow')
                
        except (CouchbaseException, ParsingFailedException) as e:
            click.secho(f"Query execution failed: {e}", fg='red')
            raise
    
    @staticmethod
    def _display_results(result) -> None:
        """Display query results in a formatted table"""
        rows = [flatten_dict(row) for row in result.rows()]
        
        if not rows:
            click.secho("No results returned", fg='yellow')
            return
        
        table = tabulate.tabulate(
            rows,
            headers='keys',
            tablefmt='csv',
            showindex=True
        )
        click.secho(f"\n{table}", fg='white')


def flatten_dict(data: Dict, separator: str = '.', prefix: str = '') -> Dict:
    """Flatten a nested dictionary"""
    items = {}
    for key, value in data.items():
        new_key = f"{prefix}{separator}{key}" if prefix else key
        
        if isinstance(value, dict):
            items.update(flatten_dict(value, separator, new_key))
        else:
            items[new_key] = value
    
    return items


config_manager = ConfigManager(CONFIG_PATH)


@click.group()
def cli():
    """CLI Application to query Couchbase"""
    click.echo("Starting qtool...")


@cli.command()
@click.option('--address', '-a', default='127.0.0.1:8091', required=True, 
              prompt="Cluster address or IP")
@click.option('--username', '-u', default='Administrator', required=True, 
              prompt="Username")
@click.option('--password', '-p', required=True, prompt="Password", hide_input=True)
def configure(address: str, username: str, password: str):
    """Store user connection preferences"""
    config_manager.set('CLUSTER', 'address', address)
    config_manager.set('CLUSTER', 'username', username)
    config_manager.set('CLUSTER', 'password', password)
    
    saved_address = config_manager.get('CLUSTER', 'address')
    saved_username = config_manager.get('CLUSTER', 'username')
    saved_password = "***"  # Don't display actual password
    
    click.secho(f"Configuration saved:", fg='green')
    click.secho(f"  Address: {saved_address}", fg='green')
    click.secho(f"  Username: {saved_username}", fg='green')
    click.secho(f"  Password: {saved_password}", fg='green')


@cli.command()
@click.option('--address', '-a', required=False, help="Cluster address")
@click.option('--username', '-u', required=False, help="Username")
@click.option('--password', '-p', required=False, help="Password", hide_input=True)
@click.option('--query', '-q', required=True, help="N1QL query to execute")
def execute(address: Optional[str], username: Optional[str], 
            password: Optional[str], query: str):
    """Execute N1QL query and display results"""
    # Get configuration from arguments or stored config
    address = address or config_manager.get('CLUSTER', 'address')
    username = username or config_manager.get('CLUSTER', 'username')
    password = password or config_manager.get('CLUSTER', 'password')
    
    if not all([address, username, password]):
        click.secho("Missing connection parameters. Please run 'configure' first.", fg='red')
        return
    
    click.clear()
    
    # Create and use Couchbase client
    client = CouchbaseClient(address, username, password)
    
    if client.connect():
        try:
            client.execute_query(query)
        except Exception as e:
            click.secho(f"Operation failed: {e}", fg='red')


if __name__ == '__main__':
    cli()
