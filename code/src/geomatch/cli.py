#!/usr/bin/env python
# coding: utf-8

import click
from datetime import timedelta
from .parallel import main as par_main
from .mongo import main as mongo_main
from .geomatch import main as geomatch_main

@click.group()
def cli():
    pass

@cli.command()
@click.option('--distance', default=160.934, help="Radius of spatial search space [km].")
@click.option('--delta', default=360, help="Delta in temporal space on each site(!) [min].")
@click.option('--percentage', default=0.01, help="Percentage of IASI data [0.0-1.0].")
def parallel(distance, delta, percentage):
    delta = timedelta(minutes=delta)
    par_main(distance, delta, percentage)


@cli.command()
@click.option('--distance', default=160.934, help="Radius of spatial search space [km].")
@click.option('--delta', default=360, help="Delta in temporal space on each site(!) [min].")
@click.option('--percentage', default=0.01, help="Percentage of IASI data [0.0-1.0].")
def mongo(distance, delta, percentage):
    delta = timedelta(minutes=delta)
    mongo_main(distance, delta, percentage)


@cli.command()
@click.option('--distance', default=160.934, help="Radius of spatial search space [km].")
@click.option('--delta', default=360, help="Delta in temporal space on each site(!) [min].")
@click.argument('ix', type=int)
def single(distance, delta, ix):
    delta = timedelta(minutes=delta)
    geomatch_main(distance, delta, ix)


def main():
    cli()
