#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Tempus data loader

import argparse
import provider
import sys


def import_tomtom(args, shape_options):
    """Load Tomtom (Multinet) data into a PostGIS database."""
    Importer = {
        '1409': provider.MultinetImporter1409,
        None: provider.MultinetImporter
    }[args.model_version]
    shape_options['I'] = False
    mni = Importer(args.source, args.speed_profile, args.prefix, args.dbstring, args.logfile, shape_options, not args.noclean)
    return mni.load()


def import_pt(args):
    """Load Public Transportation from GTFS' data into a PostGIS database."""
    
    if args.pt_network is None:
        sys.stderr.write("A PT network name must be supplied. Use --pt-network\n")
        sys.exit(1)
    gtfsi = provider.GTFSPrimeImporter(args.source, args.dbstring, args.logfile, args.pt_network)
    return gtfsi.load()


def import_navteq(args, shape_options):
    """Load Navteq (Navstreets) data into a PostGIS database."""
    ntqi = provider.NavstreetsImporter(args.source, args.prefix, args.dbstring, args.logfile, shape_options, not args.noclean)
    return ntqi.load()


def import_route120(args, shape_options):
    """Load IGN (Route120) data into a PostGIS database."""
    igni = provider.IGNRoute120Importer(args.source, args.prefix, args.dbstring, args.logfile, shape_options, not args.noclean)
    return igni.load()


def import_route500(args, shape_options):
    """Load IGN (Route500) data into a PostGIS database."""
    igni = provider.IGNRoute500Importer(args.source, args.prefix, args.dbstring, args.logfile, shape_options, not args.noclean)
    return igni.load()


def import_osm(args, shape_options):
    """Load OpenStreetMap (as shapefile) data into a PostGIS database."""
    osmi = provider.OSMImporter(args.source, args.dbstring, args.logfile)
    return osmi.load()


def import_poi(args, shape_options):
    """Load a point shapefile into a PostGIS database."""
    try:
        poi_type = int(args.poi_type)
        if poi_type not in range(1, 6):
            raise ValueError
    except ValueError:
        print "Wrong poi type. Assuming User type (5). Correct values are in range 1-5."
        poi_type = 5
    if args.poi_service_name is None:
        sys.stderr.write("The service name of the POI must be specified with --poi-service-name !\n")
        sys.exit(1)
    subs = {}
    subs["service_name"] = args.poi_service_name
    subs["name"] = args.poi_name_field
    subs["filter"] = args.poi_filter
    poii = provider.POIImporter(args.source, args.prefix, args.dbstring, args.logfile, shape_options, not args.noclean, poi_type, subs)
    return poii.load()

def import_visum(args, shape_options):
    """Load a Visum-extracted Shapefile into a PostGIS database; wait for 4
    distinct transportation modes (pedestrian, bike, private car, taxi)

    Parameters
    ----------
    args: list
        list of arguments passed to loader
    shape_options: dict
        geometry options passed to the ShapeLoader
    
    """
    splitted_modes = args.visum_modes.split(',')
    if len(splitted_modes) != 4:
        sys.stderr.write(("Need 4 comma-separated strings "
                          "(command --visum-modes) for representing "
                          "pedestrians, bikes, private vehicles and taxis!\n"))
        sys.exit(1)
    visumi = provider.VisumDrieaImporter(args.source, args.speed_profile,
                                         args.prefix, args.dbstring,
                                         args.logfile, not args.noclean,
                                         splitted_modes,
                                         options=shape_options)
    return visumi.load()

def reset_db(args):
    r = provider.ResetImporter(source='', dbstring=args.dbstring, logfile=args.logfile, doclean=False)
    return r.load()

def main():
    shape_options = {}
    parser = argparse.ArgumentParser(description='Tempus data loader')
    parser.add_argument(
        '-s', '--source',
        required=False,
        nargs='+',
        help='The source directory/file to load data from')
    parser.add_argument(
        '-sp', '--speed_profile',
        required=False,
        nargs='+',
        help='The source directory/file to load speed profile data from')
    parser.add_argument(
        '-S', '--srid',
        required=False,
        help="Set the SRID for geometries. Defaults to 4326 (lat/lon).")
    parser.add_argument(
        '-R', '--reset',
        required=False,
        help='Reset the database before importing',
        action='store_true', dest='doreset', default=False)
    parser.add_argument(
        '-t', '--type',
        required=False,
        help='The data type (tomtom, navteq, osm, gtfs, poi, route120, route500, visum)')
    parser.add_argument(
        '-m', '--model-version',
        required=False, default=None, dest='model_version',
        help='The data model version (tomtom version)')
    parser.add_argument(
        '-d', '--dbstring',
        required=False,
        help='The PostgreSQL database connection string')
    parser.add_argument(
        '--pglite',
        required=False,
        help='Use the internal cluster (PGLite) with the specified database name')
    parser.add_argument(
        '-p', '--prefix',
        required=False,
        help='Prefix for shapefile names', default="")
    parser.add_argument(
        '-l', '--logfile',
        required=False,
        help='Log file for loading and SQL output')
    parser.add_argument(
        '-i', '--insert',
        required=False, action='store_false', dest='copymode', default=True,
        help='Use insert for SQL mode (default to COPY)')
    parser.add_argument(
        '-W', '--encoding',
        required=False,
        help="Specify the character encoding of Shape's attribute column.")
    parser.add_argument(
        '-n', '--noclean',
        required=False, action='store_true', default=False,
        help="Do not clean temporary SQL file after loading.")
    parser.add_argument(
        '-y', '--poi-type',
        required=False, default=5,
        help="Poi type (1: Car park, 2: shared car, 3: Cycle, 4:Shared cycle, 5:user)")
    parser.add_argument('--poi-name-field', required=False, default="pname", help="Name of the field containing the name of each POI (default 'pname')")
    parser.add_argument('--poi-service-name', required=False, help="Name of the POI service imported (required for POI import)")
    parser.add_argument('--poi-filter', required=False, default="true", help="WHERE clause of the POI import (default 'true', i.e. no filter)")
    parser.add_argument('--pt-network', required=False, help="Name of the public transport to import/delete")
    parser.add_argument('--pt-list', required=False, help="Get the list of public transport networks in the database",
                        action='store_true', dest='do_pt_list', default=False),
    parser.add_argument('--pt-delete', required=False, help="Delete a public transport network (name given by --pt-network)",
                        action='store_true', dest='do_pt_delete', default=False)
    parser.add_argument('--visum-modes', required=False, default="P,B,V,T",
                        help=("Traffic rules for Visum data, under the format "
                              "'<mode_1>:<bitfield_value_1>,...,"
                              "<mode_n>:<bitfield_value_n>'"))

    args = parser.parse_args()

    if args.type in ('tomtom', 'navteq', 'poi'):
        if not args.srid:
            sys.stderr.write("SRID needed for %s data type. Assuming EPSG:4326.\n" % args.type)
            shape_options['s'] = 4326
        else:
            shape_options['s'] = args.srid
    if args.type in ['route120', 'route500']:
        shape_options['s'] = 2154

    if args.copymode:
        shape_options['D'] = True
    if args.encoding:
        shape_options['W'] = args.encoding
    else:
        args.encoding = 'UTF8'
    # default shp2pgsql options
    shape_options['I'] = True
    shape_options['g'] = 'geom'
    shape_options['S'] = True

    if args.pglite is not None:
        import pglite
        args.dbstring = pglite.cluster_params() + " dbname=" + args.pglite
        pglite.start_cluster()

    if args.do_pt_list:
        if args.dbstring is None:
            sys.stderr.write("Please provide a database connection string\n")
            sys.exit(1)
        from provider.gtfsprime import list_gtfs_feeds
        list_gtfs_feeds(args.dbstring)
        sys.exit(0)
    if args.do_pt_delete:
        if args.pt_network is None:
            sys.stderr.write("Please provide a PT network to delete (with --pt-network)\n")
            sys.exit(1)
        if args.dbstring is None:
            sys.stderr.write("Please provide a database connection string\n")
            sys.exit(1)
        from provider.gtfsprime import delete_gtfs_feed
        delete_gtfs_feed(args.dbstring, args.pt_network)
        sys.exit(0)

    if args.type is None:
        parser.print_help()
        sys.exit(1)

    # first reset if needed
    if args.doreset:
        reset_db(args)

    if args.type is not None and args.source is not None:
        r = None
        if args.type == 'tomtom':
            r = import_tomtom(args, shape_options)
        elif args.type == 'osm':
            args.source = args.source[0]
            r = import_osm(args, shape_options)
        elif args.type == 'navteq':
            r = import_navteq(args, shape_options)
        elif args.type == 'route120':
            r = import_route120(args, shape_options)
        elif args.type == 'route500':
            r = import_route500(args, shape_options)
        elif args.type == 'gtfs':
            args.source = args.source[0]
            r = import_pt(args)
        elif args.type == 'poi':
            r = import_poi(args, shape_options)
        elif args.type == 'visum':
            r = import_visum(args, shape_options)

        if not r:
            print "Error during import !"
            sys.exit(1)
    elif not args.doreset:
        sys.stderr.write("Source and type needed !\n")
        sys.exit(1)

    sys.exit(0)

if __name__ == '__main__':
    main()
