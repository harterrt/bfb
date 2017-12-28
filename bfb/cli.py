import click
import os
from functional import seq
import csv
import datetime
from .config import default_path as default_config
from .config import Config
from .clover import Clover

pass_config = click.make_pass_decorator(Config, ensure=True) 

@click.group()
def cli():
    pass

@cli.command()
@pass_config
@click.argument('date')
def pull_day(config, date):
    pydate = datetime.datetime.strptime(date, '%Y-%m-%d')

    clover = Clover.from_config(config)
    items = clover.get_all_line_items(pydate)

    dicts_to_csv(items, os.path.expanduser('~/data/bfb/' + date + '.csv'))

def dicts_to_csv(dicts, outpath):
    headers = sorted(list(set(
        seq(dicts)
        .flat_map(lambda x: x.keys())
    )))
    csv_data = [headers]

    for d in dicts:
        csv_data.append([d.get(key) for key in headers])

    with open(outpath, 'w') as outfile:
        csv.writer(outfile).writerows(csv_data)


if __name__ == '__main__':
    cli()
