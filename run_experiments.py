from io import FileIO
from subprocess import Popen, PIPE
import time, sys, json, os
from typing import Union

# HOW TO RUN
#   python run_experiments.py

# Constants
DURATION = 5
COMMANDS = [
    "iobench",
    "cpubench",
    "iobench &\n cpubench &",
    "iobench &\n iobench &",
    "cpubench &\n cpubench &",
    "iobench &\n cpubench &\n cpubench &",
    "cpubench &\n iobench &\n iobench &",
    "iobench &\n cpubench &\n cpubench & \n iobench &",
]

XV6_CMD = ["make", "CPUS=1", "qemu"]
INITIAL_WAIT = 2
PROCDUMP_INTERVAL = 15


def skip_xv6_init_messages(stdout: FileIO) -> None:
    """Skips compiling commands and xv6 init messages

    It skips everything until it reaches a line that contains 'starting sh'
    """
    print("Skipping xv6 init messages...")
    while b"starting sh" not in stdout.readline():
        next(stdout)


def clean_output(output):
    return output.decode().replace("$ ", "").strip()


def round_to_multiple(number, multiple):
    return multiple * round(number / multiple)


def get_experiment_data(command: str, duration: Union[int, float]):
    """Executes command inside xv6 and keeps storing output for the specified duration

    :command: string of text containing the command to be executed
    :duration: ammount of time in minutes
    """

    result = {"command": command, "output": {}}

    qemu = Popen(XV6_CMD, stdout=PIPE, stdin=PIPE)
    skip_xv6_init_messages(qemu.stdout)
    time.sleep(INITIAL_WAIT)

    duration_in_secs = duration * 60
    end_time = time.time() + duration_in_secs

    qemu.stdin.write(f"{command}\n".encode())
    qemu.stdin.flush()

    start_time = time.time()
    current_time = time.time()
    prev_procdump_time = 0
    while current_time < end_time:
        line = qemu.stdout.readline()
        if not line:
            break
        output = clean_output(line)
        print(output, end="")
        time_passed = round(current_time - start_time, 2)
        completion_percetage = time_passed * 100 / duration_in_secs
        term_size = os.get_terminal_size()
        print(
            f"{round(completion_percetage, 2)}%".rjust(
                term_size.columns - len(output) - 1
            )
            + " "
        )

        if time_passed >= prev_procdump_time + PROCDUMP_INTERVAL:
            qemu.stdout.flush()
            qemu.stdin.write(chr(16).encode())
            qemu.stdin.flush()
            prev_procdump_time = time_passed

        current_time = time.time()

        pid = output.split(":")[0]

        if "IOP" in output:
            destination = result["output"].setdefault(f"iobench{pid}", [])

        elif "KFLOP" in output:
            destination = result["output"].setdefault(f"cpubench{pid}", [])

        else:
            destination = result["output"].setdefault("other", [])

        destination.append({"time": time_passed, "content": output})

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
