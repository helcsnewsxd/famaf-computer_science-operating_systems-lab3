import matplotlib.pyplot as plt
import json, os

JSON_FILE = "experiments.json"


def draw_basic_plot(xs, ys, label, color=None):
    if color:
        plt.plot(xs, ys, label=label, color=color)
    else:
        plt.plot(xs, ys, label=label)


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


def get_value_from_content(content):
    return int(content.split(" ")[1])


def get_experiment_data(values):
    xs = [value["time"] for value in values]
    ys = [get_value_from_content(value["content"]) for value in values]
    return xs, ys


def main():
    data = read_experiment_data_from_json(JSON_FILE)
    os.makedirs("graphs", exist_ok=True)
    for index, experiment in enumerate(data):
        for process, values in experiment["output"].items():
            if not values:
                continue
            xs, ys = get_experiment_data(values)
            draw_basic_plot(xs, ys, process)
        save_fig_to_path(f"graphs/graph{index}.png")


if __name__ == "__main__":
    main()
