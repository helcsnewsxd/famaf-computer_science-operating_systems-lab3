from matplotlib import numpy as np
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import json, os

SCHEDULERS = [
    [
        "./experiments/i5_12400f/experiments_RR_escenario0.json",
        "./experiments/i5_12400f/experiments_RR_escenario1.json",
        "./experiments/i5_12400f/experiments_RR_escenario2.json",
        "./experiments/i5_12400f/experiments_RR_escenario3.json",
    ],
    [
        "./experiments/i5_12400f/experiments_MLFQ_escenario0.json",
        "./experiments/i5_12400f/experiments_MLFQ_escenario1.json",
        "./experiments/i5_12400f/experiments_MLFQ_escenario2.json",
        "./experiments/i5_12400f/experiments_MLFQ_escenario3.json",
    ],
]

OFFSETS = [0.30, 0.10, -0.10, -0.30]

COLORS = ["teal", "green", "blue", "purple"]
LABELS = [
    "Quantum 100%",
    "Quantum 10%",
    "Quantum 1%",
    "Quantum 0.1%",
]

NAMES = [
    "iobench",
    "cpubench",
    "iobench,\n cpubench",
    "2 iobench",
    "2 cpubench",
    "1 cpubench,\n 2 iobench",
    "1 iobench,\n 2 cpubench",
    "2 iobench,\n 2 cpubench",
]


def draw_bar_plot(groups, data, start=0, color=None, label=""):
    bar = plt.barh(groups, data, left=start, height=0.15, color=color, label=label)
    plt.bar_label(bar, label_type="center", annotation_clip=True)


def change_plot_visuals():
    handles = [
        mpatches.Patch(color=color, label=label) for color, label in zip(COLORS, LABELS)
    ]
    plt.legend(handles=handles)
    plt.xscale("log")
    plt.grid()


def show_graph():
    change_plot_visuals()
    plt.show()
    plt.close()


def save_fig_to_path(path):
    change_plot_visuals()
    plt.savefig(path, dpi=100, bbox_inches="tight")
    plt.close()


def get_average(output):
    if output:
        values = [int(value["content"].split(" ")[1]) for value in output]
        return round(sum(values) / len(values), 2)


class ProcessPlotter:
    def __init__(self, json_file, process_name, offset, color):
        self.json_file = json_file
        self.process_name = process_name
        self.offset = offset
        self.color = color

        self.experiment_data = self.set_experiment_data_from_json()
        self.averages = self.get_averages()

    def set_experiment_data_from_json(self):
        with open(self.json_file, "r") as json_file:
            file_contents = json_file.read()
            parsed_json = json.loads(file_contents)
            return parsed_json

    def get_averages(self):
        result = []
        for experiment in self.experiment_data:
            average = None
            for process, value in experiment["output"].items():
                if self.process_name in process:
                    average = get_average(value)

            result.append(average)
        return result

    def graph_process(self):
        xs = np.arange(len(self.averages))
        plt.yticks(xs, NAMES)
        for x, average in zip(xs, self.averages):
            if average:
                draw_bar_plot(x + self.offset, average, color=self.color)


def main(process_name, json_files):
    for json_file, offset, color in zip(json_files, OFFSETS, COLORS):
        plotter = ProcessPlotter(json_file, process_name, offset, color)
        plotter.graph_process()

    title = f"{process_name} - {json_files[0].split('/')[2].replace('_', ' ')} - {json_files[0].split('_')[2]}"
    plt.title(title)
    save_fig_to_path(f"./graphs/{title.replace(' ', '')}")


if __name__ == "__main__":
    os.makedirs("graphs", exist_ok=True)
    for json_files in SCHEDULERS:
        main("iobench", json_files)
        main("cpubench", json_files)
