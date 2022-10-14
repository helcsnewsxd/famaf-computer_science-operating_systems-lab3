from io import FileIO
from subprocess import Popen, PIPE
import time, sys, json
from typing import Union

# HOW TO RUN
#   python run_experiments.py

# Constants
DURATION = 10
COMMANDS = [
    "iobench",
    "cpubench",
    "iobench &\n cpubench &",
    "iobench &\n iobench &",
    "cpubench &\n cpubench &",
]

XV6_CMD = ["make", "CPUS=1", "qemu"]
INITIAL_WAIT = 2


def skip_xv6_init_messages(stdout: FileIO) -> None:
    """Skips compiling commands and xv6 init messages

    It skips everything until it reaches a line that contains 'starting sh'
    """
    print("Skipping xv6 init messages...")
    while b"starting sh" not in stdout.readline():
        next(stdout)


def get_experiment_data(command: str, duration: Union[int, float]):
    """Executes command inside xv6 and keeps storing output for the specified duration

    :command: string of text containing the command to be executed
    :duration: ammount of time in minutes
    """

    result = {
        "command": command,
        "duration": duration,
        "output": [],
    }

    qemu = Popen(XV6_CMD, stdout=PIPE, stdin=PIPE)
    skip_xv6_init_messages(qemu.stdout)
    time.sleep(INITIAL_WAIT)

    duration_in_secs = duration * 60
    end_time = time.time() + duration_in_secs

    qemu.stdin.write(f"{command}\n".encode())
    qemu.stdin.close()

    start_time = time.time()
    current_time = time.time()
    while current_time < end_time:
        line = qemu.stdout.readline()
        if not line:
            break
        output = line.decode().strip()
        print(output)
        completion_percetage = (current_time - start_time) * 100 / duration_in_secs
        print(f"Progress: {round(completion_percetage, 2)}%, ", end="")
        result["output"].append(output)
        current_time = time.time()

    print("DONE")
    qemu.terminate()
    qemu.wait()
    print()
    return result


def write_json(data: list[dict], filename: str) -> None:
    """jsonify data and append it to filename

    Adds an empty line at the end when appending data
    """
    with open(filename, "a") as output_file:
        formatted_data = json.dumps(data, indent=4)
        output_file.write(formatted_data)
        output_file.write("\n\n")


def main():
    results = [get_experiment_data(command, DURATION) for command in COMMANDS]
    write_json(results, "experiments.json")
    print(results)


if __name__ == "__main__":
    main()
