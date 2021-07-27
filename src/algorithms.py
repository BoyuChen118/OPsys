from typing import List
from process import Process, State
import time,math
from threading import Thread


class CPU:
    inUse = False
    contextInTimer = 0
    contextOutTimer = 0
    burstTimer = 0


class IO:
    inUse = False
    burstTimer = 0

# adds in processes to the ready queue as their arrival time comes

# Predict next cpu burst time based on most recent burst time
def predict_tau(process: Process, α, timer: int, queue: str):
    prevTau = process.tau
    process.tau = math.ceil(process.previousBurstTime * α + (1-α)*process.tau)
    print(f'time {timer}ms: Recalculated tau from {prevTau}ms to {process.tau}ms for process {process.id} {queue}')

def cumtrickle(start, processes: List[Process], ready_queue: List[Process]):
    trickle = 0
    for process in processes:
        time.sleep((process.arrival_time - trickle)//1000)
        trickle += (process.arrival_time-trickle)
        ready_queue.append(process)
        print(
            f'time {process.arrival_time}ms: Process {process.id} arrived; added to ready queue [Q {" ".join([x.id for x in ready_queue])}]')


def queue_to_string(ready_queue: List[Process]):
    if not ready_queue:
        return "[Q empty]"
    return f'[Q {" ".join([x.id for x in ready_queue])}]'

# First-come-first-served


def fcfs(processes: List[Process], context_switch_time: int, _, __):
    print()
    n = len(processes)
    # ready queue has to be empty at first
    # start the timer
    # once the timer reaches the arrival time of a process in the process list, we add it to the ready queue
    processes = sorted(processes, key=lambda process: (
        process.arrival_time, process.id)
    )

    ready_queue: List[Process] = []
    waiting_queue: List[(Process, int)] = []

    timer = 0

    cpu = CPU()
    print(f"time {timer}ms: Simulator started for FCFS [Q empty]")

    completed_processes = 0
    while completed_processes != n:
        # cpu burst
        if not cpu.inUse and cpu.contextOutTimer == 0:
            if ready_queue:  # if in ready queue, it def has a burst
                cpu_process = ready_queue.pop(0)
                cpu_process.state = State.RUNNING
                cpu.contextInTimer = (context_switch_time // 2) - 1
                cpu.burstTimer = cpu_process.cpu_bursts.pop(0)
                cpu.inUse = True
        else:
            # if in use, count down context timer, then count down burst timer
            # handle context switch timer into of cpu
            if cpu.contextInTimer != 0:
                cpu.contextInTimer -= 1
                if cpu.contextInTimer == 0:
                    print(
                        f'time {timer}ms: Process {cpu_process.id} started using the CPU for {cpu.burstTimer}ms burst {queue_to_string(ready_queue)}')
            # handle context switch timer out of cpu
            elif cpu.contextOutTimer != 0:
                cpu.contextOutTimer -= 1
                if cpu.contextOutTimer == 0:
                    cpu.inUse = False
            # handle cpu burst timer
            else:
                if cpu.burstTimer != 0:
                    cpu.burstTimer -= 1
                    if cpu.burstTimer == 0:
                        cpu.contextOutTimer = (context_switch_time // 2) - 1
                        # if no io burst, terminate
                        if cpu_process.io_bursts[0] != None:
                            print(
                                f'time {timer}ms: Process {cpu_process.id} completed a CPU burst; {len(cpu_process.cpu_bursts)} bursts to go {queue_to_string(ready_queue)}')
                            # sum = current io burst timer + iterate through waiting queue and get their burst times + this process's io burst time
                            added_time = cpu_process.io_bursts.pop(0)
                            waiting_queue.append((cpu_process, timer + added_time))
                            print(
                                f'time {timer}ms: Process {cpu_process.id} switching out of CPU; will block on I/O until time {timer + added_time}ms {queue_to_string(ready_queue)}')
                            waiting_queue = sorted(waiting_queue, key = lambda x : (x[1], x[0].id))
                        else:
                            print(
                                f'time {timer}ms: Process {cpu_process.id} terminated {queue_to_string(ready_queue)}')
                            completed_processes += 1

        # io burst
        while waiting_queue and waiting_queue[0][1] == timer:
            io_process = waiting_queue.pop(0)[0]
            print(
             f'time {timer}ms: Process {io_process.id} completed I/O; added to ready queue {queue_to_string(ready_queue)}')
            ready_queue.append(io_process)

        # new arrival
        while processes and processes[0].arrival_time == timer:
            process = processes.pop(0)
            ready_queue.append(process)
            print(
                f'time {process.arrival_time}ms: Process {process.id} arrived; added to ready queue {queue_to_string(ready_queue)}')

        timer += 1

    print(
        f'time {timer +(context_switch_time // 2)-1}ms: Simulator ended for FCFS [Q empty]')


# Shortest job first


def sjf(processes: List[Process], context_switch_time: int, α, _):
    n = len(processes)
    # ready queue has to be empty at first
    # start the timer
    # once the timer reaches the arrival time of a process in the process list, we add it to the ready queue
    processes = sorted(processes, key=lambda process: (
        process.arrival_time, process.id)
    )

    ready_queue: List[Process] = []
    waiting_queue: List[(Process, int)] = []

    timer = 0

    cpu = CPU()
    print(f"time {timer}ms: Simulator started for SJF [Q empty]")

    completed_processes = 0
    while completed_processes != n:
        # cpu burst
        # shortest job first:
        #  1. select the process with the lowest tau (if 2 process have same tau favor one that arrived first)
        if not cpu.inUse and cpu.contextOutTimer == 0:
            if ready_queue:  # if in ready queue, it def has a burst
                
                ready_queue = sorted(ready_queue, key= lambda process:(
                   process.tau, process.arrival_time, process.id
                ))
                cpu_process = ready_queue.pop(0)
                cpu_process.state = State.RUNNING
                cpu.contextInTimer = (context_switch_time // 2) -1
                nextBurst = cpu_process.cpu_bursts.pop(0)
                cpu.burstTimer = nextBurst
                cpu_process.previousBurstTime = nextBurst # update prev burst
                cpu.inUse = True
        else:
            # if in use, count down context timer, then count down burst timer
            # handle context switch timer into of cpu
            if cpu.contextInTimer != 0:
                cpu.contextInTimer -= 1
                if cpu.contextInTimer == 0:
                    print(
                        f'time {timer}ms: Process {cpu_process.id} (tau {process.tau}ms) started using the CPU for {cpu.burstTimer}ms burst {queue_to_string(ready_queue)}')
            # handle context switch timer out of cpu
            elif cpu.contextOutTimer != 0:
                cpu.contextOutTimer -= 1
                if cpu.contextOutTimer == 0:
                    cpu.inUse = False
            # handle cpu burst timer
            else:
                if cpu.burstTimer != 0:
                    cpu.burstTimer -= 1
                    if cpu.burstTimer == 0:
                        cpu.contextOutTimer = (context_switch_time // 2) - 1
                        # if no io burst, terminate
                        if cpu_process.io_bursts[0] != None:
                            print(
                                f'time {timer}ms: Process {cpu_process.id} (tau {process.tau}ms) completed a CPU burst; {len(cpu_process.cpu_bursts)} bursts to go {queue_to_string(ready_queue)}')
                            # sum = current io burst timer + iterate through waiting queue and get their burst times + this process's io burst time
                            added_time = cpu_process.io_bursts.pop(0)
                            waiting_queue.append((cpu_process, timer + added_time))
                            predict_tau(cpu_process, α,timer, queue_to_string(ready_queue))
                            print(
                                f'time {timer}ms: Process {cpu_process.id} switching out of CPU; will block on I/O until time {timer + added_time}ms {queue_to_string(ready_queue)}')
                            waiting_queue = sorted(waiting_queue, key = lambda x : (x[1], x[0].id))
                        else:
                            print(
                                f'time {timer}ms: Process {cpu_process.id} terminated {queue_to_string(ready_queue)}')
                            completed_processes += 1

        # io burst
        while waiting_queue and waiting_queue[0][1] == timer:
            io_process = waiting_queue.pop(0)[0]
            print(
             f'time {timer}ms: Process {io_process.id} completed I/O; added to ready queue {queue_to_string(ready_queue)}')
            ready_queue.append(io_process)

        # new arrival
        while processes and processes[0].arrival_time == timer:
            process = processes.pop(0)
            ready_queue.append(process)
            print(
                
                f'time {process.arrival_time}ms: Process {process.id} (tau {process.tau}ms) arrived; added to ready queue {queue_to_string(ready_queue)}')

        timer += 1

    print(
        f'time {timer +(context_switch_time // 2)-1}ms: Simulator ended for SJF [Q empty]')

# Shortest remaining time


def srt(processes: List[Process], context_switch_time: int, α, _):
    pass

# Round robin


def rr(processes: List[Process], context_switch_time: int, _, time_slice):
    n = len(processes)
    # ready queue has to be empty at first
    # start the timer
    # once the timer reaches the arrival time of a process in the process list, we add it to the ready queue
    processes = sorted(processes, key=lambda process: (
        process.arrival_time, process.id)
    )

    ready_queue: List[Process] = []
    waiting_queue: List[(Process, int)] = []

    timer = 0
    print(f"time {timer}ms: Simulator started for RR with time slice {time_slice}ms [Q empty]")
    sigma_time_slice = 0
    cpu = CPU()
    completed_processes = 0
    while completed_processes != n:
        # cpu burst
        if not cpu.inUse and cpu.contextOutTimer == 0:
            if ready_queue:
                  # if in ready queue, it def has a burst
                cpu_process = ready_queue.pop(0)
                cpu_process.state = State.RUNNING
                cpu.contextInTimer = (context_switch_time // 2) - 1
                cpu.burstTimer = cpu_process.cpu_bursts.pop(0)
                cpu.inUse = True
        else:
            # if in use, count down context timer, then count down burst timer
            # handle context switch timer into of cpu
            if cpu.contextInTimer != 0:
                cpu.contextInTimer -= 1
                if cpu.contextInTimer == 0:
                    if not cpu_process.interrupted:
                        print(
                            f'time {timer}ms: Process {cpu_process.id} started using the CPU for {cpu.burstTimer}ms burst {queue_to_string(ready_queue)}')
                        cpu_process.previousBurstTime = cpu.burstTimer
                    else:
                        print(f'time {timer}ms: Process {cpu_process.id} started using the CPU for remaining {cpu.burstTimer}ms of {cpu_process.previousBurstTime} burst {queue_to_string(ready_queue)}')
                    sigma_time_slice = time_slice
            # handle context switch timer out of cpu
            elif cpu.contextOutTimer != 0:
                cpu.contextOutTimer -= 1
                if cpu.contextOutTimer == 0:
                    cpu.inUse = False
            # handle cpu burst timer
            else:
                if cpu.burstTimer != 0:
                    cpu.burstTimer -= 1
                    sigma_time_slice -= 1
                    if cpu.burstTimer == 0:
                        cpu.contextOutTimer = (context_switch_time // 2) - 1
                        # if no io burst, terminate
                        if cpu_process.io_bursts[0] != None:
                            print(
                                f'time {timer}ms: Process {cpu_process.id} completed a CPU burst; {len(cpu_process.cpu_bursts)} bursts to go {queue_to_string(ready_queue)}')
                            # sum = current io burst timer + iterate through waiting queue and get their burst times + this process's io burst time
                            added_time = cpu_process.io_bursts.pop(0)
                            waiting_queue.append((cpu_process, timer + added_time))
                            print(
                                f'time {timer}ms: Process {cpu_process.id} switching out of CPU; will block on I/O until time {timer + added_time}ms {queue_to_string(ready_queue)}')
                            cpu_process.interrupted = False
                            waiting_queue = sorted(waiting_queue, key = lambda x : (x[1], x[0].id))
                        else:
                            print(
                                f'time {timer}ms: Process {cpu_process.id} terminated {queue_to_string(ready_queue)}')
                            completed_processes += 1
                    elif sigma_time_slice == 0:
                        if not ready_queue:
                            print(f'time {timer}ms: Time slice expired; no preemption because ready queue is empty [Q empty]')
                        else:
                            cpu.contextOutTimer = (context_switch_time // 2)
                            print(f'time {timer}ms: Time slice expired; process {cpu_process.id} preempted with {cpu.burstTimer}ms to go {queue_to_string(ready_queue)}')
                            cpu_process.cpu_bursts.insert(0,cpu.burstTimer)
                            cpu_process.interrupted = True
                            cpu.burstTimer = 0
                            ready_queue.append(cpu_process)
        # io burst
        while waiting_queue and waiting_queue[0][1] == timer:
            io_process = waiting_queue.pop(0)[0]
            print(
             f'time {timer}ms: Process {io_process.id} completed I/O; added to ready queue {queue_to_string(ready_queue)}')
            ready_queue.append(io_process)

        # new arrival
        while processes and processes[0].arrival_time == timer:
            process = processes.pop(0)
            ready_queue.append(process)
            print(
                f'time {process.arrival_time}ms: Process {process.id} arrived; added to ready queue {queue_to_string(ready_queue)}')

        timer += 1

    print(
        f'time {timer +(context_switch_time // 2)-1}ms: Simulator ended for RR [Q empty]')
        
