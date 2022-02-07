import os
import click

user_configs = {}

class Repo:
    def __init__(self, home=None):
        self.home = os.path.abspath(home or ".")
        self.db = None

    def __enter__(self):
        path = os.path.join(self.home, "repo.db")
        self.db = connect(path)

    def __exit__(self, exc_type, exc_value, tb):
        self.db.close()

def save_if_true(ctx, param, value):
    if not value:
        ctx.abort()


@click.group()
@click.pass_context
def cli(ctx):
    """Simple Query Tool to execute N1QL queries on couchbase-server"""
    ctx.obj = ctx.with_resource(Repo(repo_home))


@cli.command()
@click.option('--format', required=True, type=click.Choice(['json', 'table', 'csv']), default='json',
              prompt="display format: ")
@click.option('--scope', required=True, default='_default', prompt="scope: ")
@click.option('--chostname', default='127.0.0.1:8091', required=True, prompt="cluster host: ")
@click.option('--collection', default='travel-sample', required=True, prompt="collection: ")
@click.option('--yes', is_flag=True, callback=save_if_true, expose_value=False,
              prompt='Are you sure you want to save preferences?')
def configure(chostname, format, scope, collection):
    """stores user connection preferences"""
    user_configs.update({"chostname": chostname, "format": format, "scope": scope, "collection": collection})
    for k, v in user_configs.items():
        os.system(f"export {k}={v}")
        os.system(f"echo ${k}")

@cli.command()
def execute():
    """helps user execute N1QL query """
    print("Hello Connect")
    click.echo(user_configs)

if __name__=="__main__":
    configure()