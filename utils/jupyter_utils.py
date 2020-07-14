import os
import sys
import time
import shutil
from pathlib import Path
from IPython.core.magic import register_cell_magic
from IPython.display import clear_output


LOG_DIR = "./jupyter_logs"


class MultiOutputStream:
    def __init__(self, *streams):
        self.streams = streams

    def write(self, data):
        for stream in self.streams:
            stream.write(data)

    def flush(self):
        for stream in self.streams:
            stream.flush()


class Tee:
    def __init__(self, stdout, stderr):
        self.stdout = stdout
        self.stderr = stderr

    def start(self):
        self._old_stdout = sys.stdout
        self._old_stderr = sys.stderr

        sys.stdout = MultiOutputStream(self._old_stdout, self.stdout)
        sys.stderr = MultiOutputStream(self._old_stderr, self.stderr)

    def stop(self):
        sys.stdout = self._old_stdout
        sys.stderr = self._old_stderr

    def __enter__(self):
        self.start()

    def __exit__(self, exc_type, exc_value, traceback):
        self.stop()


@register_cell_magic
def log_cell(line, cell):
    execution_count = get_ipython().execution_count

    base_dir = LOG_DIR
    name = f"{execution_count}"

    Path(base_dir).mkdir(parents=True, exist_ok=True)
    stdout = open(f"{base_dir}/{name}_stdout.log", 'w')
    stderr = open(f"{base_dir}/{name}_stderr.log", 'w')

    with Tee(stdout=stdout, stderr=stderr):
        get_ipython().run_cell(cell)

    stdout.close()
    stderr.close()


def get_last_log(suffix):
    path = LOG_DIR

    files = os.listdir(path)
    files = list(filter(lambda f: f.endswith(suffix), files))
    files.sort()
    last_file = files[-1]
    
    if last_file:
        return f"{path}/{last_file}"
    else:
        return None


def watch(filename, interval=1):
    while True:
        clear_output(wait=True)
        with open(filename, 'rb') as f:
            print(f.read().decode())
        time.sleep(interval)


def watch_last_stdout(interval=1):
    watch(get_last_log("_stdout.log"), interval=interval)


def watch_last_stderr(interval=1):
    watch(get_last_log("_stderr.log"), interval=interval)


def clear_logs():
    try:
        shutil.rmtree(LOG_DIR)
    except:
        pass
