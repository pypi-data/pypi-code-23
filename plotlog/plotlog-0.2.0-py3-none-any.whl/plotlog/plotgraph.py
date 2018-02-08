import matplotlib.pyplot as plt


class PlotGraph:
    def_style = ["-", "--", "-.", ":"]
    mm2inch = 1/25.4

    def __init__(self):
        pass

    def plot(self, p_path, g_path, st, gr, x, df):
        plt.figure(figsize=(st["graph_size"][0]*self.mm2inch,
                            st["graph_size"][1]*self.mm2inch))
        plt.rcParams["font.family"] = st["font_family"]
        plt.rcParams["font.size"] = st["font_size"]

        if "do_subplot" in gr:
            self.multi_plot(p_path, st, gr["do_subplot"], x, df)
        else:
            self.single_plot(p_path, st, gr, x, df)

        plt.savefig(g_path)
        plt.close()

    def multi_plot(self, p_path, st, gr, x, df):
        for g in gr:
            plt.subplot(g["subplot"][0], g["subplot"][1], g["subplot"][2])
            self.single_plot(p_path, st, g, x, df)

    def single_plot(self, p_path, st, gr, x, df):
        def_num = 0
        plt.xlabel(gr["xlabel"])
        plt.ylabel(gr["ylabel"])
        for grp in gr["plot"]:
            if grp["style"] == "order":
                grp["style"] = self.def_style[def_num]
                def_num = def_num + 1 if def_num < 3 else 0

            if not grp["col"] in df.columns and grp["col"] > len(df.columns):
                print("error: column '"+str(grp["col"])+"' is not exist in", p_path)
                continue

            plt.plot(
                x, df.ix[:, grp["col"]],
                label=grp["label"], color=grp["color"],
                linestyle=grp["style"], linewidth=grp["width"]
            )
        plt.xlim(st["xlim"])
        plt.ylim(gr["ylim"])

        if gr["legend"]["loc"] is not None:
            plt.legend(loc=gr["legend"]["loc"],
                       bbox_to_anchor=gr["legend"]["bbox_to_anchor"],
                       ncol=gr["legend"]["ncol"])
