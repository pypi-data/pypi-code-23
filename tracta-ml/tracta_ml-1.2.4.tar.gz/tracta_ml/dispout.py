import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

def iter_disp(gen_cnt,best_mod_fit,best_stdev_fit,best_feat_fit):

    print("Iteration -",gen_cnt+1,"complete","......",\
                  "best_score: {:.4f}, score_stdev: {:.4f}, feat_fitness: {:.4f}".\
                  format(best_mod_fit[-1], best_stdev_fit[-1], best_feat_fit[-1]))

def sol_disp(sol):
    print(sol)


def graph_disp(self,metric):
    fig, ax = plt.subplots()
    plt.plot(self.monitor[metric])
    plt.title(str(metric) + str(" vs Iterations"))
    plt.xlabel("Iterations")
    plt.ylabel(metric)
    ax.set_xlim(xmin=0)
    tick_space = round(len(self.monitor[metric]) / 15)
    ax.xaxis.set_major_locator(ticker.MultipleLocator(tick_space))
    plt.xticks(rotation=45)
    plt.show()
    return