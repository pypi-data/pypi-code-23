from sfsimodels import output as mo
from collections import OrderedDict


def save_figure(ap, figure, name, publish=True, name_ext="", ftype=".png", latex=False, dpi=150):
    """
    Saves a figure and produces python output.

    :param ap: (module), all paths
    :param figure: (Figure object)
    :param name: (str), the name of the figure
    :param publish: (bool) if True then save in publication location, else in temp dir
    :param name_ext: (str) An extension for the file name
    :param ftype: (str) the suffix for file type (e.g. '.png')
    :param latex: (bool), if true then return a string of latex script to include the figure
    :param dpi: (int), the dots per inch of the saved figure
    :return: (str)
    """
    figure.tight_layout()

    if not publish:
        figure.savefig(ap.TEMP_FIGURE_PATH + name + name_ext + ftype, dpi=dpi)
    else:
        figure.savefig(ap.PUBLICATION_FIGURE_PATH + name + name_ext + ftype, dpi=dpi)
    if latex:
        return latex_for_figure(ap, name, ftype)
    return ""


def latex_for_figure(ap, name, ftype):
    str_parts = ["",
                    "\\begin{figure}[H]",
                    "\centering",
                    "\\includegraphics{%s/%s%s}" % (ap.FIGURE_FOLDER, name, ftype),
                    "\\caption{%s \label{fig: %s}}" % (name.replace("_", " "), name),
                    "\\end{figure}"
                 ]
    return "\n".join(str_parts)


def output_to_table(**kwargs):
    mo.output_to_table(**kwargs)


def add_table_ends(**kwargs):
    mo.add_table_ends(**kwargs)


def get_file_name_for_build_results(python_name):
    name = python_name.replace('.py', '')
    name = name.split("figure_")[-1]
    name = "fig_results_" + name + ".txt"
    return name


def unpack_build_results(python_name, titles):
    res_fpath = get_file_name_for_build_results(python_name)
    res_file = open(res_fpath)
    res_lines = res_file.readlines()
    data = OrderedDict()
    for line in res_lines:
        # name, sd_start, sd_end, period, max_disp_time
        items = line.split(",")
        if items[0] not in data:
            data[items[0]] = OrderedDict()
            for i in range(len(items)):
                data[items[0]][titles[i]] = []

        for i in range(len(items)):
            try:
                data[items[0]][titles[i]].append(float(items[i]))
            except ValueError:
                data[items[0]][titles[i]].append(items[i])
    return data

