import click

@click.group()
def cli():
    pass

@cli.command()
@click.arguement('date')
@click.option(
    '--config-file',
    default='~/.config/bfb.conf'
)
def pull_day():
    pass

