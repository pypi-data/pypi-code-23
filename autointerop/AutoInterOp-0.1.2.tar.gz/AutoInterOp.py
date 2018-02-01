#!/usr/bin/env python

import os
import glob
import click
import zipfile
import logging
from accessoryFunctions import accessoryFunctions


def replace_line(file_name, line_num, text):
    """
    Replaces a line in a text file
    :param file_name: path to file you want to target
    :param line_num: line number to replace (starts at 0)
    :param text: string to replace line with
    """
    lines = open(file_name, 'r').readlines()
    lines[line_num] = text
    out = open(file_name, 'w')
    out.writelines(lines)
    out.close()


def create_plots(run_folder, output_folder):
    """
    Creates plots from a MiSeq run using InterOp software
    :param run_folder: path to MiSeq run folder
    :param output_folder: path to output folder
    :return: list of paths to each plot file produced
    """
    if output_folder is None:
        output_folder = run_folder
    miseq_run = os.path.basename(run_folder)

    interop_plots = [
        'plot_by_cycle',
        'plot_by_lane',
        'plot_flowcell',
        'plot_qscore_heatmap',
        'plot_qscore_histogram',
        'plot_sample_qc',
    ]

    plot_files = []

    for plot in interop_plots:
        logging.info('Creating plot with {}...'.format(plot))

        gnuplot_output = os.path.join(output_folder, '{}_gnuplot.txt'.format(plot))

        # create gnuplot text file
        cmd = plot
        cmd += " " + run_folder
        cmd += " > {}".format(gnuplot_output)
        logging.debug(cmd)
        os.system(cmd)

        # Set plot name
        output_plot = os.path.join(output_folder, miseq_run + '_' + plot + '.png')

        # Replace line in gnuplot text file
        replace_line(gnuplot_output, 3, "set output '{}'\n".format(output_plot))

        # Feed text file to gnuplot
        cmd = 'cat {} | gnuplot'.format(gnuplot_output)
        os.system(cmd)

        plot_files.append(output_plot)

    # Cleanup text files
    to_delete = glob.glob(os.path.join(output_folder, '*gnuplot.txt'))
    for file in to_delete:
        os.remove(file)

    return plot_files


def generate_summaries(run_folder, output_folder):
    """
    Creates text summary output from a MiSeq run using InterOp software
    :param run_folder: path to MiSeq run folder
    :param output_folder: path to output folder
    :return: list of paths to each text file produced
    """
    miseq_run = os.path.basename(run_folder)

    interop_programs = [
        'index-summary',  # txt
        'imaging_table',  # csv
        'summary'  # txt
    ]

    summary_files = []

    for program in interop_programs:
        logging.info('Creating text output with {}...'.format(program))
        if program == 'index-summary':
            output_filename = os.path.join(output_folder, miseq_run + '_' + program + '.txt')
        else:
            output_filename = os.path.join(output_folder, miseq_run + '_' + program + '.csv')

        cmd = program
        cmd += " " + run_folder
        cmd += " > {}".format(output_filename)
        os.system(cmd)

        summary_files.append(output_filename)

    return summary_files


def dependency_check():
    """
    Checks if any of the InterOp binaries are missing.
    This has way too much package overhead (biopython, OLCTools) for something I should probably just implement myself.
    """
    dependencies = ['aggregate',
                    'imaging_table',
                    'index-summary',
                    'plot_by_cycle',
                    'plot_by_lane',
                    'plot_flowcell',
                    'plot_qscore_heatmap',
                    'plot_qscore_histogram',
                    'plot_sample_qc',
                    'summary']
    missing_dependencies = []
    for dependency in dependencies:
        if accessoryFunctions.dependency_check(dependency) is False:
            missing_dependencies.append(dependency)
    if missing_dependencies:
        logging.error('The following dependencies are not available on your $PATH: {}'
                      '\nPlease install them and try rerunning AutoInterOp.'.format(missing_dependencies))
        quit()


@click.command()
@click.option('-r', '--run_folder',
              type=click.Path(exists=True),
              required=True,
              help='Path to an Illumina MiSeq run folder. '
                   'This should contain a SampleInfo.xml file and an InterOp folder.')
@click.option('-o', '--output_folder',
              type=click.Path(),
              help='Path to desired output folder. Defaults to the same place as the specified run_folder.')
@click.option('-z', '--zip',
              is_flag=True,
              default=False,
              help='Set this flag to zip all output files into a single archive available in your output folder.')
def main(run_folder, zip, output_folder=None):
    logging.basicConfig(
        format='\033[92m \033[1m %(asctime)s %(levelname)s \033[0m %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')

    # Check to see if necessary binaries are present
    dependency_check()

    # Set up output folder
    if output_folder is None:
        output_folder = run_folder

    if not os.path.exists(output_folder):
        logging.info('Creating directory {}'.format(output_folder))
        os.mkdir(output_folder)

    # Grab the name of the MiSeq run folder
    miseq_run = os.path.basename(run_folder)

    logging.info('Running InterOp programs on {}'.format(miseq_run))

    # Create plots and summaries
    plot_files = create_plots(run_folder=run_folder, output_folder=output_folder)
    summary_files = generate_summaries(run_folder=run_folder, output_folder=output_folder)
    all_files = plot_files + summary_files

    # If zip flag is specified
    if zip:
        # Zip all output from plot_files and summary_files
        zip_archive = zipfile.ZipFile(os.path.join(output_folder, miseq_run + '_InterOp_output.zip'), 'w')
        for file in all_files:
            zip_archive.write(file, os.path.basename(file))
        zip_archive.close()

        # Delete all extraneous files
        for file in all_files:
            os.remove(file)

    logging.info('InterOp Pipeline completed. Output available at {}'.format(output_folder))

if __name__ == '__main__':
    main()
