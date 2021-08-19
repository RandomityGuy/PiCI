from io import FileIO
import subprocess
import threading
import select
import time
from dataclasses import dataclass

@dataclass
class StreamProcess:
    process: subprocess.Popen
    out: FileIO
    err: FileIO

class Stream:
    processes: list[StreamProcess]
    _thread: threading.Thread
    _iomap: dict[FileIO, FileIO]

    _tailprocess: StreamProcess


    def __init__(self):
        self.processes = []
        self._iomap = {}
        self._thread = None
        self._tailprocess = None
    
    def append_process(self, process: subprocess.Popen, out: FileIO, err: FileIO):
        self.processes.append(StreamProcess(process, out, err))
        self._iomap[process.stdout] = out
        self._iomap[process.stderr] = err
        if self._thread == None or not self._thread.is_alive():
            self._thread = threading.Thread(target=lambda: self.process_thread())
            self._thread.daemon = True
            self._thread.start()

    def process_thread(self):
        while True:
            rstreams, _, _ = select.select(self._iomap.keys(), [], [])
            for stream in rstreams:
                line = stream.readline()
                self._iomap[stream].write(time.strftime("[ %Y-%m-%d %H:%M:%S ]: ", time.localtime()).encode())
                self._iomap[stream].write(line)
                if self._tailprocess != None:
                    if self._tailprocess.out == self._iomap[stream] or self._tailprocess.err == self._iomap[stream]:
                        print(time.strftime("[ %Y-%m-%d %H:%M:%S ]: ", time.localtime()) + line.decode(), end="")
            if all(proc.process.poll() is not None for proc in self.processes):
                break
        self._iomap.clear()
        self.processes.clear()

    def tail_process(self, process: subprocess.Popen):
        for proc in self.processes:
            if proc.process == process:
                self._tailprocess = proc
                break

    def remove_tail_process(self):
        self._tailprocess = None
