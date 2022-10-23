import matplotlib.pyplot as plt
import json, os

JSON_FILE = "experiments.json"


def draw_basic_plot(xs, ys, label, color=None):
    if color:
        plt.plot(xs, ys, label=label, color=color)
    else:
        plt.plot(xs, ys, label=label)


def draw_bar_plot(groups, data):
    plt.bar(groups, data, width=0.25)


def change_plot_visuals():
    plt.legend()
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


def main():
    data = read_experiment_data_from_json(JSON_FILE)
    os.makedirs("graphs", exist_ok=True)
    iobench = get_averages(data, "iobench")
    cpubench = get_averages(data, "cpubench")


if __name__ == "__main__":
    main()
