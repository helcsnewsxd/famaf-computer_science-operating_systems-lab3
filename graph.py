from matplotlib import numpy as np
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import json, os

JSON_FILES = [
    "./experiments/i5_12400f/experiments_RR_escenario0.json",
    "./experiments/i5_12400f/experiments_RR_escenario1.json",
    "./experiments/i5_12400f/experiments_RR_escenario2.json",
    "./experiments/i5_12400f/experiments_RR_escenario3.json",
]

NAMES = [
    "Caso 0:",
    "Caso 1:",
    "Caso 2:",
    "Caso 3:",
    "Caso 4:",
    "Caso 5:",
    "Caso 6:",
    "Caso 7:",
]

OFFSETS = [-0.30, -0.10, 0.10, 0.30]


def draw_basic_plot(xs, ys, label, color=None):
    if color:
        plt.plot(xs, ys, label=label, color=color)
    else:
        plt.plot(xs, ys, label=label)


def draw_bar_plot(groups, data, start=0, color=None, label=""):
    bar = plt.barh(groups, data, left=start, height=0.15, color=color, label=label)
    plt.bar_label(bar, label_type="center", annotation_clip=True)


def change_plot_visuals():
    red_patch = mpatches.Patch(color="red", label="Proceso A")
    blue_patch = mpatches.Patch(color="blue", label="Proceso B")
    plt.legend(handles=[red_patch, blue_patch])
    plt.xscale("log")
    plt.grid()


def show_graph():
    change_plot_visuals()
    plt.show()
    plt.close()


def save_fig_to_path(path):
    change_plot_visuals()
    plt.savefig(path, dpi=100)
    plt.close()


def read_experiment_data_from_json(filename: str) -> list[dict]:
    with open(filename, "r") as json_file:
        file_contents = json_file.read()
        parsed_json = json.loads(file_contents)
        return parsed_json


def get_average(output):
    if output:
        values = [int(value["content"].split(" ")[1]) for value in output]
        return round(sum(values) / len(values), 2)


def get_averages(experiment_data, process_name):
    result = []
    for experiment in experiment_data:
        averages = [
            get_average(value)
            for process, value in experiment["output"].items()
            if process_name in process
        ]
        result.append(averages)
    return result


def graph_averages(case, averages):
    bottom = 0
    for average in averages:

        if bottom:
            color = "blue"
        else:
            color = "red"

        draw_bar_plot(case, average, bottom, color=color)
        bottom = average


def graph_process(data, process_name, offset):
    averages = get_averages(data, process_name)
    xs = np.arange(len(averages))
    plt.yticks(xs, NAMES)
    for x, averages in zip(xs, averages):
        graph_averages(x + offset, averages)


def graph_data_from_json(json_file, process, offset):
    data = read_experiment_data_from_json(json_file)
    os.makedirs("graphs", exist_ok=True)
    graph_process(data, process, offset)


if __name__ == "__main__":
    for json_file, offset in zip(JSON_FILES, OFFSETS):
        graph_data_from_json(json_file, "iobench", offset)

    plt.title("iobench")
    show_graph()

    for json_file, offset in zip(JSON_FILES, OFFSETS):
        graph_data_from_json(json_file, "cpubench", offset)

    plt.title("cpubench")
    show_graph()
