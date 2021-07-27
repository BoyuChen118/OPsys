from typing import List, Tuple
from enum import Enum

class State(Enum):
    READY = 0
    WAITING = 1
    RUNNING = 2

class Process:
    def __init__(self, id: int, arrival_time: int, num_bursts: int, bursts: List[Tuple[int, int]], tau: int):
        #number indicating the chronological order of processes
        self.id = chr(id+65)
        #number indicating the arrival time of the process
        self.arrival_time = arrival_time
        #number of bursts the process will take
        self.num_bursts = num_bursts
        #array of tuples of(cpu burst time, i/o burst time) for each burst
        # self.bursts = bursts

        self.tau = tau
        self.cpu_bursts = [burst[0] for burst in bursts]
        self.io_bursts = [burst[1] for burst in bursts]
        self.previousBurstTime = self.cpu_bursts[0]
        self.interrupted = False
        self.state = State.READY