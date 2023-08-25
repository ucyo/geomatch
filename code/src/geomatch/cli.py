#!/usr/bin/env python
# coding: utf-8

from datetime import timedelta

import click
from bson.objectid import ObjectId

from .geomatch import main as geomatch_main
from .mongo import main as mongo_main
from .parallel import main as par_main
from .plot import main as plot_main


@click.group()
@click.option(
    "--distance",
    default=20,
    show_default=True,
    type=click.FloatRange(min=0, max=6371),
    help="Spatial tolerance [km].",
)
@click.option(
    "--delta",
    default=120,
    show_default=True,
    type=click.IntRange(min=0),
    help="Temporal tolerance [min].",
)
@click.pass_context
def cli(ctx, distance, delta):
    """Geomatch Tool - Analysis of TROPOMI and IASI satellite tracks."""
    ctx.ensure_object(dict)
    ctx.obj["distance"] = distance
    ctx.obj["delta"] = timedelta(minutes=delta)


@cli.command()
@click.option(
    "--percentage",
    default=1,
    show_default=True,
    type=click.FloatRange(0, 1),
    help="Percentage of IASI data.",
)
@click.option(
    "--output",
    default=None,
    show_default=True,
    type=click.Path(exists=False),
    help="Output json file.",
)
@click.option(
    "--mongo/--no-mongo",
    show_default=True,
    default=False,
    help="Spatial selection using MongoDB.",
)
@click.pass_context
def match(ctx, percentage, output, mongo):
    """Run search algorithm in either geomatch or mongo."""
    distance = ctx.obj["distance"]
    delta = ctx.obj["delta"]

    if mongo:
        click.echo("Using mongo for finding matches.")
        mongo_main(distance, delta, percentage, output=output)
    else:
        click.echo("Using geomatch for finding matches.")
        par_main(distance, delta, percentage, output)


@cli.command()
@click.option("--id", "ident", default=None, type=str, help="Tropomi ID")
@click.option(
    "--ix",
    default=0,
    type=click.IntRange(min=0),
    show_default=True,
    help="Index position in Tropomi DB",
)
@click.option(
    "--output",
    default=None,
    show_default=True,
    type=click.Path(exists=False),
    help="Output html file.",
)
@click.pass_context
def single(ctx, ident, ix, output):
    """Search single TROPOMI entries w/ geomatch and mongodb."""
    distance = ctx.obj["distance"]
    delta = ctx.obj["delta"]
    query = None

    if ident:
        query = {"_id": ObjectId(ident)}
        ix = 0
    if output is not None:
        plot_main(distance, delta, ix, query=query, save=output)
    else:
        geomatch_main(distance, delta, ix, query=query)


def main():
    cli(obj={})
