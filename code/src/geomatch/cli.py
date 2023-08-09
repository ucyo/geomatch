#!/usr/bin/env python
# coding: utf-8

from datetime import timedelta

import click
from bson.objectid import ObjectId

from .geomatch import main as geomatch_main
from .mongo import main as mongo_main
from .parallel import main as par_main


@click.group()
def cli():
    """Geomatch Tool - Analysis of TROPOMI and IASI satellite tracks."""
    pass


@cli.command()
@click.option(
    "--distance", default=160.934, help="Radius of spatial search space [km]."
)
@click.option(
    "--delta", default=360, help="Delta in temporal space on each site(!) [min]."
)
@click.option(
    "--percentage",
    default=0.01,
    type=click.FloatRange(0, 1),
    help="Percentage of IASI data [0.0-1.0].",
)
def parallel(distance, delta, percentage):
    """Run search algorithm in parallel."""
    delta = timedelta(minutes=delta)
    par_main(distance, delta, percentage)


@cli.command()
@click.option(
    "--distance", default=160.934, help="Radius of spatial search space [km]."
)
@click.option(
    "--delta", default=360, help="Delta in temporal space on each site(!) [min]."
)
@click.option(
    "--percentage",
    default=0.01,
    type=click.FloatRange(0, 1),
    help="Percentage of IASI data [0.0-1.0].",
)
def mongo(distance, delta, percentage):
    """Use database itself for search in parallel."""
    delta = timedelta(minutes=delta)
    mongo_main(distance, delta, percentage)


@cli.command()
@click.option(
    "--distance",
    default=160.934,
    type=click.FloatRange(min=0, max=6371),
    help="Radius of spatial search space [km].",
)
@click.option(
    "--delta",
    default=360,
    type=click.IntRange(min=0),
    help="Delta in temporal space on each site(!) [min].",
)
@click.option("--id", "ident", default=None, type=str, help="Tropomi ID")
@click.option(
    "--ix", default=0, type=click.IntRange(min=0), help="Index position in Tropomi DB"
)
def single(distance, delta, ident, ix):
    """Search single TROPOMI entries w/ geomatch and mongodb."""
    delta = timedelta(minutes=delta)
    query = None
    if ident:
        query = {"_id": ObjectId(ident)}
        ix = 0
    geomatch_main(distance, delta, ix, query=query)


def main():
    cli()
