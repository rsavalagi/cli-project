import os
from datetime import timedelta

import click
import configparser
import tabulate
from couchbase.auth import PasswordAuthenticator
from couchbase.cluster import Cluster, ClusterOptions, ClusterTimeoutOptions, QueryOptions
from couchbase.exceptions import CouchbaseException, ParsingFailedException

APP_NAME = 'qtool'
BASE_DIR = os.path.realpath(os.path.dirname(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, '.configs.ini')
parser = configparser.ConfigParser()


def get_config(**kwargs):
    parser.read(CONFIG_PATH)
    return parser.get(section=kwargs.get('section'), option=kwargs.get('option'))


def set_config(**kwargs):
    parser.read(CONFIG_PATH)
    parser.set(kwargs.get("section"), kwargs.get("option"), kwargs.get("value"))
    with open(CONFIG_PATH, 'w') as configfile:
        parser.write(configfile, space_around_delimiters=False)


def flatten_dict(innerElement, separator='.', prefix=''):
    return {f"{prefix}{separator}{k}" if prefix else k: v for kk, vv in innerElement.items() for k, v in
            flatten_dict(vv, separator, kk).items()} if isinstance(innerElement, dict) else {
        prefix: innerElement}


@click.group()
def cli():
    """CLI Application to query CouchBD"""
    click.echo(f"starting...")


@cli.command()
@click.option('--address', '-a', default='127.0.0.1:8091', required=True, prompt="cluster address or ip ")
@click.option('--username', '-u', default='Administrator', required=True, prompt="username ")
@click.option('--password', '-p', required=True, prompt="password ")
def configure(address, username, password):
    """stores user connection preferences"""
    set_config(section='CLUSTER', option="address", value=address)
    set_config(section='CLUSTER', option="username", value=username)
    set_config(section='CLUSTER', option="password", value=password)

    address = get_config(section='CLUSTER', option="address")
    username = get_config(section='CLUSTER', option="username")
    password = get_config(section='CLUSTER', option="password")

    
    click.secho(f"saved configs: {address}, {username}, {password}", fg='green')


@cli.command()
@click.option('--address', '-a', required=False)
@click.option('--username', '-u', required=False)
@click.option('--password', '-p', required=False)
@click.option('--query', '-q', required=True)
def execute(address, username, password, query):
    """executes N1QL query and displays results """
    if not username:
        username = get_config(section='CLUSTER', option="username")
    if not address:
        address = get_config(section='CLUSTER', option="address")
    if not password:
        password = get_config(section='CLUSTER', option="password")

    click.clear()

    connectionSuccess = False
    try:
        click.secho(f"CONNECTING TO '{address}'", fg='green')
        timeout_options = ClusterTimeoutOptions(kv_timeout=timedelta(seconds=5), query_timeout=timedelta(seconds=10))
        cluster = Cluster.connect(f"couchbase://{address}", ClusterOptions(PasswordAuthenticator(username, password),
                                                                           timeout_options=timeout_options))
        connectionSuccess = True
    except CouchbaseException as ce:
        click.secho(f"connection failed due to {ce}", fg='red')
        cluster = None

    if connectionSuccess:
        try:
            click.secho(f"{query}", fg='yellow')
            result = cluster.query(query, QueryOptions(metrics=True))

            click.secho(f"\n")
            rows = [flatten_dict(row) for row in result.rows()]

            click.secho(tabulate.tabulate(rows, headers='keys', tablefmt='csv', showindex=True), fg='white')

            click.secho(f"\n{result.metadata().metrics().execution_time()}", fg='yellow')

        except (CouchbaseException, ParsingFailedException) as ex:
            click.secho(f"failed to parse response due to {ex}")
