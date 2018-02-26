#!/usr/bin/env python3

import matplotlib.pyplot as plt


class Chart2D():
    """
    Base class for any 2-dimensional chart.

    Args:
        title (str): The title of the chart
        x_axis_name (str): The name of the x-axis
        y_axis_name (str): The name of the y-axis
        data (array): An array of numerical values
        labels (array): An array of strings with the name of the labels along the x-axis
        label_positions (array):
    """
    title = None
    x_axis_name = None
    y_axis_name = None
    data = None
    labels = None
    x_label_spacing = None
    size = None

    def __init__(self,
                 title,
                 x_axis_name,
                 y_axis_name,
                 data,
                 labels,
                 x_label_spacing=0,
                 size=(10, 10),
                 xlabel_rotation_limit=10,
                 xlabel_rotation_rotation=45
                 ):
        self.title = title
        self.x_axis_name = x_axis_name
        self.y_axis_name = y_axis_name
        self.data = data
        self.labels = labels
        self.x_label_spacing = x_label_spacing
        self.size = size
        self.xlabel_rotation_limit = xlabel_rotation_limit
        self.xlabel_rotation_rotation = xlabel_rotation_rotation

        self.label_positions = self.get_x_label_positions(
            self.data,
            self.x_label_spacing
        )

        self.setup_xlabels()

    def initialize_chart_values(self):
        """ Initializes the default value of the chart """
        plt.title(self.title)
        plt.xlabel(self.x_axis_name)
        plt.ylabel(self.y_axis_name)
        plt.rcParams["figure.figsize"] = self.size

    def setup_xlabels(self):
        """
        Sets up the labels on the x-axis based on the amount of labels, and the
        value 'xlabel_rotation_limit'.
        """
        if len(self.data) > self.xlabel_rotation_limit:
            plt.xticks(self.label_positions,
                       self.labels,
                       rotation=self.xlabel_rotation_rotation,
                       ha='right')
        else:
            plt.xticks(self.label_positions, self.labels)

    def get_x_label_positions(self, data, label_spacing):
        """
        Returns the positions of the x labels based on the number
        of labels and the spacing between them.

        Returns:
            list

        Args:
            data (array): An array of numerical values
            label_spacing (int): The spacing between labels
        """
        result = list()
        for index in range(0, len(data)):
            result.append(index + label_spacing)
        return result


class BarChart(Chart2D):
    """
    Creates an 2D barchart object.

    Returns:
        None

    Args:
        title (str): The title of the chart
        x_axis_name (str): The name of the x-axis
        y_axis_name (str): The name of the y-axis
        data (array): An array of numerical values
        labels (array): An array of strings with the name of the labels along the x-axis
        bar_width (int): The width of the bars, default = 1
        bar_spacing (int): The space between the bars, default = 2
        xlabel_rotation_limit (int): The minimum amount of x-axis labels before rotating the label, default = 10
        xlabel_rotation_degrees (int): The amount of degrees labels on the x-axis should rotate by, default = 45
    """

    bar_width = None
    bar_spacing = None
    bar_positions = None
    xlabel_rotation_limit = None

    def __init__(self, bar_width=1.5, bar_spacing=0.2, *args, **kwargs):
        super(BarChart, self).__init__(*args, **kwargs)
        self.bar_width = bar_width
        self.bar_spacing = bar_spacing + bar_width
        self.bar_positions = self.get_bar_positions(
            self.data,
            self.bar_width,
            self.bar_spacing
        )
        print(self.labels)

    def get_bar_positions(self, data, bar_width, bar_spacing):
        """
        Returns a list with the position for the bars in a barchart.

        Returns:
            list

        Args:
            data (list)
            bar_width (int)
            bar_spacing (int)

        """
        result = list()
        for data_point in range(0, len(self.data)):
            result.append(data_point * bar_spacing + bar_width * 10)
        return result

    def show(self):
        """
        Initializes the graph with the specified options and renders it.

        Returns:
            None

        """
        super().initialize_chart_values()
        plt.bar(self.bar_positions, self.data, width=self.bar_width)
        plt.xticks(self.bar_positions, self.labels)
        plt.show()

    def render(self, output_file):
        """
        Renders the graph to a file

        Returns:
            None

        Args:
            output_file (str): Path to the output file
        """
        super().initialize_chart_values()
        plt.bar(self.bar_positions, self.data, width=self.bar_width)
        plt.xticks(self.bar_positions, self.labels)
        plt.savefig(output_file)


class LineChart(Chart2D):
    """
    Creates a linechart object.

    Args:
        title (str): The title of the chart
        x_axis_name (str): The name of the x-axis
        y_axis_name (str): The name of the y-axis
        data (array): An array of numerical values
        labels (array): An array of strings with the name of the labels along the x-axis
    """

    def __init__(self, *args, **kwargs):
        super(LineChart, self).__init__(*args, **kwargs)

    def show(self):
        super().initialize_chart_values()
        self.setup_xlabels()
        plt.plot(self.data)
        plt.show()
