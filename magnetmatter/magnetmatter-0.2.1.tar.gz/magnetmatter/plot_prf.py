# plot_prf.py

from datetime import datetime
import os, numpy as np, pandas as pd, sys, re, math
import matplotlib.pyplot as plt

""" importing private modules """
from auxiliary import cm2inch
from wrappers import TraceCalls
from find_tools import findfile, findfiles
from prf_plot_tools import extract_out_file, calculate_size, excluded_regions
from prf_plot_tools import prepare_refinement_result, get_spacegroups



@TraceCalls()
def plot_prf(path = "", printsize = "two_in_docx", minmax2theta = (-1000,1000)):
    """
    searches all folders for given path for .prf, .out, .pcr files to plot with refined informations

    Args:
        path: script will be executed at this path
        printsize: options are "two_in_docx", two_in_ppt", "one_in_docx", "one_in_ppt".
        minmax2theta: tuple of min and max 2theta values to be ignored

    Compatibility:
        Script has been tested with refined data from DMC, HRPT (SINQ:PSI)
        and refined data from X-ray sources.
        The FullProf .pcr format is the new format (_not_ classical).

    Side effect:
        Saves plots of "Yobs", "Ycal" and "Ycal-Yobs" for .prf, .out and .pcr files
        found in child folderns. The script is verbose and will tell what it is currently
        doing, if the process was successful and what mistakes occured.

    Common mistake:
        If you change your .pcr, remember to run FullProf to see the effect of the updated
        parameters or added phases. This script stupidly reads in the .out and .prf files.
        Any changes to especially phase names will certainly result in unchanged phase names found
        in plot.
        Therefore always run the .pcr file to update the FullProf output files.

    """

    # printsize = "two_in_ppt" # graphs are 17 cm wide, perfect for two in .ppt
    # printsize = "one_in_docx" # graphs are 17 cm wide, perfect for one in word
    # printsize = "one_in_ppt" # single grpah in .ppt
    # printsize = "two_in_docx" # graphs are 8 cm wide, perfect for two in word

    """ path bookkeeping """
    if path == "":
        path = os.getcwd()
    os.chdir(path)
    folders = [folder for folder in os.listdir() if os.path.isdir(folder) ]

    for folder in folders:
        print("found folder {}".format(folder))
    print("")

    specified_size = True
    if printsize == "two_in_docx":
        graph_width = 8.45 # cm
        graph_height = graph_width*3/4 # cm
        bigger_text = 10 # do not use
        medium_text = 8 # still quite big
        smaller_text = 6 # better
        refsize_text = 5
        micro_text = 4 # 4 good for refinement info.
        subplot_right_space = 8.1#6.8
        dotsize = 1 #
        linewidth = 1
        refinfo_pos_long_text = (1.02,-0.2)#(1.02,-0.07)
        refinfo_pos_short_text = (1.02,-0.07)
        ylabelpos_pre = (0.01,1.05)
        ylabelpos_post = (-0.11,0.50)
        xlabelpos_pre = (1.05,0.15)
        xlabelpos_post = (0.50,-0.12)
        ticklabelpadding = 3
        yticklabel_placeholder = "1000"

    elif printsize == "two_in_ppt":
        graph_width = 15 # cm
        graph_height = graph_width*3/4 # cm
        bigger_text = 14 # do not use
        medium_text = 12 # still quite big
        smaller_text = 10 # better
        refsize_text = 8
        micro_text = 8 # 4 good for refinement info.
        dotsize = 2
        linewidth = 2
        subplot_right_space = 7.7
        refinfo_pos_long_text = (1.03,-0.14)
        refinfo_pos_short_text = (1.03,-0.06)
        ylabelpos_pre = (-0.008,1.05)
        ylabelpos_post = (-0.10,0.50)
        xlabelpos_pre = (1.05,-0.043)
        xlabelpos_post = (0.50,-0.08)
        ticklabelpadding = 6
        yticklabel_placeholder = "100"



    elif printsize == "one_in_docx":
        graph_width = 17 # cm
        graph_height = graph_width*3/4 # cm
        bigger_text = 14 # do not use
        medium_text = 12 # still quite big
        smaller_text = 10 # better
        refsize_text = 8
        micro_text = 8 # 4 good for refinement info.
        dotsize = 2
        linewidth = 2
        subplot_right_space = 6.8
        refinfo_pos_long_text = (1.015,-0.13)
        refinfo_pos_short_text = (1.015,-0.055)
        ylabelpos_pre = (-0.007,1.05)
        ylabelpos_post = (-0.07,0.50)
        xlabelpos_pre = (1.05,-0.043)
        xlabelpos_post = (0.50,-0.07)
        ticklabelpadding = 5
        yticklabel_placeholder = "100"

    elif printsize == "one_in_ppt":
        graph_width = 32 # cm
        graph_height = graph_width*2/5 # cm
        bigger_text = 20 # do not use
        medium_text = 18 # still quite big
        smaller_text = 16 # better
        refsize_text = 10
        micro_text = 10 # 4 good for refinement info.
        dotsize = 3
        linewidth = 2
        subplot_right_space = 4.6
        refinfo_pos_long_text = (1.01,-0.2)
        refinfo_pos_short_text = (1.01,-0.075)
        ylabelpos_pre = (-0.009,1.07)
        ylabelpos_post = (-0.045,0.55)
        xlabelpos_pre = (1.05,-0.063)
        xlabelpos_post = (0.50,-0.10)
        ticklabelpadding = 9
        yticklabel_placeholder = "1000000"

    for folder in folders:
        print("\nworking on", folder); os.chdir(path); os.chdir(folder)

        prf = findfile(".prf"); pcr = findfile(".pcr"); out = findfile(".out");
        if not os.path.exists(prf): print("!-!-!-! skipping \"" + folder + "\" + --> no .prf was found"); continue
        if not os.path.exists(pcr): print("!-!-!-! skipping \"" + folder + "\" + --> no .pcr was found"); continue
        if not os.path.exists(out): print("!-!-!-! skipping \"" + folder + "\" + --> no .out was found"); continue


        try:
            """ try if we can extract DMC data to plot """
            with open(prf, "r") as reading:
                for num,line in enumerate(reading):
                    if num >= 5:
                        numbers = [float(number) for number in line.strip().split() ]
                        if len(yobs) != entries:
                            yobs += numbers
                        elif len(ycalc) != entries:
                            ycalc += numbers
                        else:
                            bragg_reflections += numbers
                    elif num == 2:
                        end,start,step = [float(number) for number in line.strip().split()[0:3]]
                        angles = np.arange(start,end+step,step)
                        entries = len(angles)
                        yobs = list()
                        ycalc = list()
                        bragg_reflections = list()

            """ UNDER DEVELOPMENT: plot indicating lines for bragg reflections """
            # last_value = 0
            # b_r = bragg_reflections
            # for i,value in enumerate(b_r):
            #     if value > 10000:
            #         continue
            #     elif value < last_value:
            #         b_r = b_r[:i]
            #         break
            #     last_value = value
            # br = pd.DataFrame()
            # midway = int(len(b_r)/2)
            # for col_name, col in zip(["ID","2theta"],[ b_r[:midway], b_r[midway:]]):
            #     br[col_name] = col
            """ UNDER DEVELOPMENT: plot indicating lines for bragg reflections """

            """ preparing dataframe """
            df = pd.DataFrame()
            for col_name, col in zip(["2Theta", "Yobs", "Ycal"], [angles, yobs, ycalc]):
                df[col_name] = col
            print("found a DMC .prf")
        except:
            """ if DMC extraction fails, extract x-ray data """
            nb_excluded_regions = excluded_regions()
            df = pd.read_csv(prf, skiprows = 3+nb_excluded_regions, delimiter="[\t]+", engine="python")
            df = df[["2Theta","Yobs","Ycal"]]
            for col in df.columns.values:
                df[col] = pd.to_numeric(df[col], errors="coerce")
            df = df.dropna(axis=0)
            print("found a R1D1 .prf")

        """ check if model data are actual values! otherwise skip datafolder """
        if df.empty: sys.stdout.write("!-!-!-! skipping folder \"" + folder + "\". DataFrame is empty (values in prf might be NaNs)\n"); continue

        df["Yobs-Ycal"] = df["Yobs"]-df["Ycal"]

        """ below code is obsolete """
        if not df[df["2Theta"] > 30.00].empty:
          """ if-check is necessary when treating synchrotron data,
          where angles are less than 20 degrees! """
          # df = df[df["2Theta"] > 20.00]
          # df = df[df["2Theta"] < 92.900]


        """ shortening the view of the diffractogram
        if user has provided a tuple of min-max values """
        if type(minmax2theta) == type(tuple()) and len(minmax2theta) == 2:
          df = df[df["2Theta"] > minmax2theta[0]]
          df = df[df["2Theta"] < minmax2theta[1]]


        """ style of pandas plotting """
        plt.style.use("seaborn")

        """ plot scatter and line plots of observed and calculated """
        fig, ax1 = plt.subplots(figsize = cm2inch(graph_width, graph_height) )
        plt.subplots_adjust(right=subplot_right_space)

        """ extraction of:
        phase names (dict)
        phase fractions (dict)
        wavelength (float)
        refined parameter value and error (dict) """
        wavelength, frac_info, phases, refined_par = extract_out_file()

        """ calculates:
        ab and c-sizes (dict of dicts) """
        size_info = calculate_size(
            wavelength = wavelength,
            phases = phases,
            refined_par = refined_par,
            )

        """ extracting spacegroups from PCR file """
        spacegroups = get_spacegroups()

        """ preparing information such as refined parameters, phases, phase fractions
        crystallite sizes and so to be printed on canvas. """
        combined_text = prepare_refinement_result(
            phases = phases,
            refined_par = refined_par,
            size_info = size_info,
            frac_info = frac_info,
            spacegroups = spacegroups,
            wavelength = wavelength,
            )

        """ plotting Yobs, Ycal, and Yobs-Ycal data. """
        y = "Yobs"
        ax1 = df.plot(
            "2Theta",
            y,
            kind="scatter",
            s = dotsize,
            ax = ax1,
            fontsize = smaller_text,  # xtick and ytick labels
            label = y, # for legend
            c = "r",
            alpha=0.5,
            )
        df.plot(
            "2Theta",
            "Ycal",
            linewidth=linewidth,
            ax = ax1,
            alpha=0.8,
            )
        df.plot(
            "2Theta",
            "Yobs-Ycal",
            linewidth = linewidth,
            ax=ax1,
            alpha=0.3,
            )

        """ if not long refinement info text, aling text with bottom of graph """
        refinfo_pos = refinfo_pos_short_text if combined_text.count("\n") < 24 else refinfo_pos_long_text

        """ plotting refinement info on canvas"""
        ttt = ax1.text(
            refinfo_pos[0],
            refinfo_pos[1],
            combined_text,
            size=refsize_text,
            fontname = "monospace",
            picker=True,
            transform = ax1.transAxes,
            # zorder = 0,
            )

        """ making the refinement info have a semitransparent white background """
        # ttt.set_bbox(dict(facecolor='white', alpha=0.5, edgecolor='white'))

        """ changing the position of the legends to make Yobs appear at the top """
        handles,labels = ax1.get_legend_handles_labels()
        handles = [handles[2], handles[0], handles[1]]
        labels = [labels[2], labels[0], labels[1]]

        """ setting legend to top left corner """
        leg = plt.legend(handles,labels, loc="best", prop = {"size": micro_text})


        """ setting title to folder name """
        title = os.path.basename(folder)
        plt.title(title, size = medium_text)

        """ setting dummy y- and xlabel names. These are changed later
        this is done due to the effect of using plt.tight_layout()
        in combination with rotation and shifting of the text object"""
        ylabel = plt.ylabel("Counts", size = smaller_text)
        plt.xlabel(r"2$\theta$", size = smaller_text)

        """ repositioning and rotation the ylabel """
        ax1.yaxis.set_label_coords(*ylabelpos_pre)
        ylabel.set_rotation(0)

        """ Xlabel must be here otherwise plt.tight_layout is not given the
        additional white space for the ref_info text """
        ax1.xaxis.set_label_coords(*xlabelpos_pre)

        """ name of output file """
        figname = folder+".png"
        figname = os.path.join(path,figname)




        """ scientific notation of major ytick values """
        # import matplotlib.ticker as mtick
        # ax1.yaxis.set_major_formatter(mtick.FormatStrFormatter('%.0e'))
        """ above code is obsolete """

        """ set all yticks to 100 to tweak the right space for final ytick labels """
        myyticks = ax1.get_yticks()
        mynewyticks = [yticklabel_placeholder for x in myyticks]
        plt.yticks(myyticks, mynewyticks)

        """ ensure nothing is left outside the plot
        many elements are moved the following code to optimize the space """
        plt.tight_layout()
        """ everything from here is tweaking already existing plt objects! """

        """ showing only first and last ytick label """
        mynewyticks = ["" for x in myyticks]
        mynewyticks[-1] = "{:.1e}".format(myyticks[-1])
        mynewyticks[0] = "{:.1e}".format(myyticks[0])
        plt.yticks(myyticks, mynewyticks)

        """ setting padding of x and y tick labels """
        ax1.tick_params(pad=ticklabelpadding)

        """ repositioning and renaming xlabel and ylabel
        _after_ the use of plt.tight_layout()"""
        ylabel.set_rotation(90)
        ax1.yaxis.set_label_coords(*ylabelpos_post)
        ax1.xaxis.set_label_coords(*xlabelpos_post)
        plt.xlabel(r"scattering angle 2$\theta$ [$^o$]", size = smaller_text)
        ylabel = plt.ylabel("signal count [a.u.]", size = smaller_text)


        """ saving the figure in high resolution """
        plt.savefig(figname, dpi=500, format = "png")

        """ avoid memory leak """
        plt.close()

    """ normalizing the path """
    os.chdir(path)



""" below code was accidently called when importing script... """
# if __name__ == "__main__":
#     # import pdb; pdb.set_trace(); import time; time.sleep(1); print("sys.argv =\n",sys.argv,"\n")
#     if len(sys.argv) > 1:
#         plot_prf(path = sys.argv[1])
#     else:
#         plot_prf()
# else:
#     if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
#         plot_prf(path = sys.argv[1])









# print("\n\nEND_OF_SCRIPT")
# print(sys.version_info)
# print(sys.executable)
