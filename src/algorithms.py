from typing import List
from process import Process, State
import math


class CPU:
    inUse = False
    contextInTimer = 0
    contextOutTimer = 0
    burstTimer = 0


# Predict next cpu burst time based on most recent burst time
def predict_tau(process: Process, α, timer: int, queue: str, sjf: bool):
    prevTau = process.tau
    process.tau = math.ceil(
        (process.previousBurstTime if sjf else process.originalBurstTime) * α + (1-α)*process.tau)
    process.tauRemaining = process.tau
    if timer < 1000:
        print(
            f'time {timer}ms: Recalculated tau from {prevTau}ms to {process.tau}ms for process {process.id} {queue}')


def queue_to_string(ready_queue: List[Process]):
    if not ready_queue:
        return "[Q empty]"
    return f'[Q {"".join([x.id for x in ready_queue])}]'


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
    completed_processes: List[Process] = []

    total_burst_time = 0
    num_preemptions = 0
    num_context_switches = 0

    timer = 0

    cpu = CPU()
    cpu_process = None
    print(f"time {timer}ms: Simulator started for FCFS [Q empty]")

    while len(completed_processes) != n:
        # cpu burst
        if not cpu.inUse and cpu.contextOutTimer == 0:
            if ready_queue:  # if in ready queue, it def has a burst
                cpu_process = ready_queue.pop(0)
                cpu_process.state = State.RUNNING
                cpu.contextInTimer = (context_switch_time // 2) - 1
                cpu_process.num_context_switches += 1
                num_context_switches += 1  # increment context switch
                cpu.burstTimer = cpu_process.cpu_bursts.pop(0)
                cpu.inUse = True
        else:
            # if in use, count down context timer, then count down burst timer
            # handle context switch timer into of cpu
            if cpu.contextInTimer != 0:
                cpu.contextInTimer -= 1
                if cpu.contextInTimer == 0:
                    if timer < 1000:
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
                    total_burst_time += 1
                    if cpu.burstTimer == 0:
                        cpu.contextOutTimer = (context_switch_time // 2)
                        if cpu_process.io_bursts[0] != None:
                            if timer < 1000:
                                print(
                                    f'time {timer}ms: Process {cpu_process.id} completed a CPU burst; {len(cpu_process.cpu_bursts)} burst{"s" if len(cpu_process.cpu_bursts) != 1 else ""} to go {queue_to_string(ready_queue)}')
                            # sum = current io burst timer + iterate through waiting queue and get their burst times + this process's io burst time
                            added_time = cpu_process.io_bursts.pop(0)
                            waiting_queue.append(
                                (cpu_process, timer + added_time + context_switch_time // 2))
                            if timer < 1000:
                                print(
                                    f'time {timer}ms: Process {cpu_process.id} switching out of CPU; will block on I/O until time {timer + added_time + context_switch_time // 2}ms {queue_to_string(ready_queue)}')
                            waiting_queue = sorted(
                                waiting_queue, key=lambda x: (x[1], x[0].id))
                        else:
                            print(
                                f'time {timer}ms: Process {cpu_process.id} terminated {queue_to_string(ready_queue)}')
                            completed_processes.append(cpu_process)
                        # if no io burst, terminate

        # increment wait time for processses in ready queue
        for process in ready_queue:
            process.wait_time += 1
        # io burst
        while waiting_queue and waiting_queue[0][1] == timer:
            io_process = waiting_queue.pop(0)[0]
            ready_queue.append(io_process)
            if timer < 1000:
                print(
                    f'time {timer}ms: Process {io_process.id} completed I/O; added to ready queue {queue_to_string(ready_queue)}')

        # new arrival
        while processes and processes[0].arrival_time == timer:
            process = processes.pop(0)
            ready_queue.append(process)
            if timer < 1000:
                print(
                    f'time {process.arrival_time}ms: Process {process.id} arrived; added to ready queue {queue_to_string(ready_queue)}')

        # increment turnaround time for our current cpu_process
        if cpu_process is not None:
            cpu_process.turnaround_time += 1

        timer += 1

    total_sim_time = timer + (context_switch_time // 2)-1

    print(f'time {total_sim_time}ms: Simulator ended for FCFS [Q empty]')

    avg_burst = sum([x.burst_time for x in completed_processes]) / \
        sum([x.num_bursts for x in completed_processes])
    avg_turnaround = sum([(x.burst_time + x.num_bursts*context_switch_time + x.wait_time)
                         for x in completed_processes])/sum([x.num_bursts for x in completed_processes])
    avg_wait = sum([x.wait_time for x in completed_processes]) / \
        sum([x.num_bursts for x in completed_processes])
    cpu_utilization = total_burst_time/total_sim_time
    print()
    return {'avg_burst': avg_burst, 'avg_turnaround': avg_turnaround,
            'avg_wait': avg_wait, 'num_preemptions': num_preemptions,
            'num_context_switches': num_context_switches, 'cpu_utilization': cpu_utilization*100}


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
    completed_processes: List[Process] = []

    total_burst_time = 0
    num_preemptions = 0
    num_context_switches = 0

    timer = 0

    cpu = CPU()
    cpu_process = None
    print(f"time {timer}ms: Simulator started for SJF [Q empty]")

    while len(completed_processes) != n:

        # cpu burst
        # shortest job first:
        #  1. select the process with the lowest tau (if 2 process have same tau favor one that arrived first)
        if not cpu.inUse and cpu.contextOutTimer == 0:
            if ready_queue:  # if in ready queue, it def has a burst
                cpu_process = ready_queue.pop(0)
                cpu_process.state = State.RUNNING
                cpu.contextInTimer = (context_switch_time // 2) - 1
                num_context_switches += 1
                nextBurst = cpu_process.cpu_bursts.pop(0)
                cpu.burstTimer = nextBurst
                cpu_process.previousBurstTime = nextBurst  # update prev burst
                cpu.inUse = True
        else:
            # if in use, count down context timer, then count down burst timer
            # handle context switch timer into of cpu
            if cpu.contextInTimer != 0:
                cpu.contextInTimer -= 1
                if cpu.contextInTimer == 0:
                    if timer < 1000:
                        print(
                            f'time {timer}ms: Process {cpu_process.id} (tau {cpu_process.tau}ms) started using the CPU for {cpu.burstTimer}ms burst {queue_to_string(ready_queue)}')
            # handle context switch timer out of cpu
            elif cpu.contextOutTimer != 0:
                cpu.contextOutTimer -= 1
                if cpu.contextOutTimer == 0:
                    cpu.inUse = False
            # handle cpu burst timer
            else:
                if cpu.burstTimer != 0:
                    cpu.burstTimer -= 1
                    total_burst_time += 1
                    if cpu.burstTimer == 0:
                        cpu.contextOutTimer = (context_switch_time // 2)
                        # if no io burst, terminate
                        if cpu_process.io_bursts[0] != None:
                            if timer < 1000:
                                print(
                                    f'time {timer}ms: Process {cpu_process.id} (tau {cpu_process.tau}ms) completed a CPU burst; {len(cpu_process.cpu_bursts)} burst{"s" if len(cpu_process.cpu_bursts) != 1 else ""} to go {queue_to_string(ready_queue)}')
                            # sum = current io burst timer + iterate through waiting queue and get their burst times + this process's io burst time
                            added_time = cpu_process.io_bursts.pop(0)
                            waiting_queue.append(
                                (cpu_process, timer + added_time + context_switch_time // 2))
                            predict_tau(cpu_process, α, timer,
                                        queue_to_string(ready_queue), True)
                            if timer < 1000:
                                print(
                                    f'time {timer}ms: Process {cpu_process.id} switching out of CPU; will block on I/O until time {timer + added_time + context_switch_time // 2}ms {queue_to_string(ready_queue)}')
                            waiting_queue = sorted(
                                waiting_queue, key=lambda x: (x[1], x[0].id))
                        else:
                            print(
                                f'time {timer}ms: Process {cpu_process.id} terminated {queue_to_string(ready_queue)}')
                            completed_processes.append(cpu_process)
        # increment wait time for processses in ready queue
        for process in ready_queue:
            process.wait_time += 1
        # io burst
        while waiting_queue and waiting_queue[0][1] == timer:
            io_process = waiting_queue.pop(0)[0]
            ready_queue.append(io_process)
            ready_queue = sorted(ready_queue, key=lambda process: (
                process.tau, process.id, process.arrival_time
            ))
            if timer < 1000:
                print(
                    f'time {timer}ms: Process {io_process.id} (tau {io_process.tau}ms) completed I/O; added to ready queue {queue_to_string(ready_queue)}')

        # new arrival
        while processes and processes[0].arrival_time == timer:
            process = processes.pop(0)
            ready_queue.append(process)
            ready_queue = sorted(ready_queue, key=lambda process: (
                process.tau, process.id, process.arrival_time
            ))
            if timer < 1000:
                print(

                    f'time {process.arrival_time}ms: Process {process.id} (tau {process.tau}ms) arrived; added to ready queue {queue_to_string(ready_queue)}')
        # increment turnaround time for our current cpu_process
        if cpu_process is not None:
            cpu_process.turnaround_time += 1

        timer += 1

    total_sim_time = timer + (context_switch_time // 2)-1
    print(f'time {total_sim_time}ms: Simulator ended for SJF [Q empty]')

    avg_burst = sum([x.burst_time for x in completed_processes]) / \
        sum([x.num_bursts for x in completed_processes])
    avg_turnaround = sum([(x.burst_time + x.num_bursts*context_switch_time + x.wait_time)
                         for x in completed_processes])/sum([x.num_bursts for x in completed_processes])
    avg_wait = sum([x.wait_time for x in completed_processes]) / \
        sum([x.num_bursts for x in completed_processes])
    cpu_utilization = total_burst_time/total_sim_time
    print()
    return {'avg_burst': avg_burst, 'avg_turnaround': avg_turnaround,
            'avg_wait': avg_wait, 'num_preemptions': num_preemptions,
            'num_context_switches': num_context_switches, 'cpu_utilization': cpu_utilization*100}


# Shortest remaining time
def srt(processes: List[Process], context_switch_time: int, α, _):
    n = len(processes)
    # ready queue has to be empty at first
    # start the timer
    # once the timer reaches the arrival time of a process in the process list, we add it to the ready queue
    processes = sorted(processes, key=lambda process: (
        process.arrival_time, process.id)
    )

    ready_queue: List[Process] = []
    waiting_queue: List[(Process, int)] = []
    completed_processes: List[Process] = []

    timer = 0

    total_burst_time = 0
    num_preemptions = 0
    num_context_switches = 0

    cpu = CPU()
    print(f"time {timer}ms: Simulator started for SRT [Q empty]")
    while len(completed_processes) != n:

        if not cpu.inUse and cpu.contextOutTimer == 0:
            if ready_queue:  # if in ready queue, it def has a burst

                ready_queue = sorted(ready_queue, key=lambda process: (
                    process.tauRemaining, process.id, process.arrival_time
                ))
                cpu_process = ready_queue.pop(0)
                cpu_process.state = State.RUNNING
                cpu.contextInTimer = (context_switch_time // 2) - 1
                num_context_switches += 1
                cpu_process.num_context_switches += 1
                nextBurst = cpu_process.cpu_bursts.pop(0)
                cpu.burstTimer = nextBurst
                cpu_process.previousBurstTime = nextBurst  # update prev burst
                cpu.inUse = True
        else:
            # if in use, count down context timer, then count down burst timer
            # handle context switch timer into of cpu
            if cpu.contextInTimer != 0:
                cpu.contextInTimer -= 1
                if cpu.contextInTimer == 0:
                    if not cpu_process.interrupted:
                        if timer < 1000:
                            print(
                                f'time {timer}ms: Process {cpu_process.id} (tau {cpu_process.tau}ms) started using the CPU for {cpu.burstTimer}ms burst {queue_to_string(ready_queue)}')
                        cpu_process.originalBurstTime = cpu.burstTimer
                    else:
                        if timer < 1000:
                            print(
                                f'time {timer}ms: Process {cpu_process.id} (tau {cpu_process.tau}ms) started using the CPU for remaining {cpu.burstTimer}ms of {cpu_process.originalBurstTime}ms burst {queue_to_string(ready_queue)}')
                    # if current process has longer remaining than any in ready queue (rare case: only happens when a process with shorter tau in ready q when cpu still context switching)
                    if any(p.tauRemaining < cpu_process.tauRemaining for p in ready_queue):
                        cpu_process.interrupted = True
                        cpu.contextOutTimer = (context_switch_time // 2)
                        cpu_process.cpu_bursts.insert(0, cpu.burstTimer)
                        replacement = next(
                            p for p in ready_queue if p.tauRemaining < cpu_process.tauRemaining)
                        cpu.burstTimer = 0
                        if timer < 1000:
                            print(
                                f'time {timer}ms: Process {replacement.id} (tau {replacement.tau}ms) will preempt {cpu_process.id} {queue_to_string(ready_queue)}')
                        num_preemptions += 1
                        ready_queue.append(cpu_process)
                        cpu_process.wait_time -= 1 + (context_switch_time//2)
            # handle context switch timer out of cpu
            elif cpu.contextOutTimer != 0:
                cpu.contextOutTimer -= 1
                if cpu.contextOutTimer == 0:
                    cpu.inUse = False
            # handle cpu burst timer
            else:
                if cpu.burstTimer != 0:
                    cpu.burstTimer -= 1
                    total_burst_time += 1
                    cpu_process.tauRemaining -= 1
                    if cpu.burstTimer == 0:
                        cpu.contextOutTimer = (context_switch_time // 2)
                        # if no io burst, terminate
                        if cpu_process.io_bursts[0] != None:
                            if timer < 1000:
                                print(
                                    f'time {timer}ms: Process {cpu_process.id} (tau {cpu_process.tau}ms) completed a CPU burst; {len(cpu_process.cpu_bursts)} burst{"s" if len(cpu_process.cpu_bursts) != 1 else ""} to go {queue_to_string(ready_queue)}')
                            # sum = current io burst timer + iterate through waiting queue and get their burst times + this process's io burst time
                            added_time = cpu_process.io_bursts.pop(0)
                            waiting_queue.append(
                                (cpu_process, timer + added_time + context_switch_time // 2))
                            predict_tau(cpu_process, α, timer,
                                        queue_to_string(ready_queue), False)
                            if timer < 1000:
                                print(
                                    f'time {timer}ms: Process {cpu_process.id} switching out of CPU; will block on I/O until time {timer + added_time + context_switch_time // 2}ms {queue_to_string(ready_queue)}')
                            cpu_process.interrupted = False
                            waiting_queue = sorted(
                                waiting_queue, key=lambda x: (x[1], x[0].id))
                        else:
                            ready_queue = sorted(ready_queue, key=lambda process: (
                                process.tau, process.id, process.arrival_time
                            ))
                            print(
                                f'time {timer}ms: Process {cpu_process.id} terminated {queue_to_string(ready_queue)}')
                            completed_processes.append(cpu_process)
        for process in ready_queue:
            process.wait_time += 1
        # io burst
        while waiting_queue and waiting_queue[0][1] == timer:
            io_process = waiting_queue.pop(0)[0]
            # if process that finished io has shorter tau than current running process
            if (cpu_process.tauRemaining > io_process.tauRemaining) and (cpu.contextInTimer == 0) and (cpu.contextOutTimer == 0) and cpu.inUse:
                cpu_process.interrupted = True
                cpu.contextOutTimer = (context_switch_time // 2)
                cpu_process.cpu_bursts.insert(0, cpu.burstTimer)
                cpu.burstTimer = 0
                ready_queue.append(io_process)
                # io_process.wait_time -=1
                ready_queue = sorted(ready_queue, key=lambda process: (
                    process.tau, process.id, process.arrival_time
                ))
                if timer < 1000:

                    print(
                        f'time {timer}ms: Process {io_process.id} (tau {io_process.tau}ms) completed I/O; preempting {cpu_process.id} {queue_to_string(ready_queue)}')
                ready_queue.append(cpu_process)
                num_preemptions += 1
                cpu_process.wait_time -= context_switch_time//2
            else:
                ready_queue.append(io_process)
                if timer < 1000:
                    print(
                        f'time {timer}ms: Process {io_process.id} (tau {io_process.tau}ms) completed I/O; added to ready queue {queue_to_string(ready_queue)}')
                # increment wait time for processses in ready queue

        # new arrival
        while processes and processes[0].arrival_time == timer:
            process = processes.pop(0)
            ready_queue.append(process)
            # process.wait_time -=1
            ready_queue = sorted(ready_queue, key=lambda process: (
                process.tau, process.id, process.arrival_time
            ))
            if timer < 1000:
                print(

                    f'time {process.arrival_time}ms: Process {process.id} (tau {process.tau}ms) arrived; added to ready queue {queue_to_string(ready_queue)}')

        timer += 1
                # increment wait time for processses in ready queue

                # # increment wait time for processses in ready queue


    total_sim_time = timer + (context_switch_time // 2)-1

    print(f'time {total_sim_time}ms: Simulator ended for SRT [Q empty]\n')

    avg_burst = sum([x.burst_time for x in completed_processes]) / \
        sum([x.num_bursts for x in completed_processes])
    avg_turnaround = sum([(x.burst_time + x.num_context_switches*context_switch_time + x.wait_time)
                         for x in completed_processes])/sum([x.num_bursts for x in completed_processes])
    avg_wait = sum([x.wait_time for x in completed_processes]) / \
        sum([x.num_bursts for x in completed_processes]) 
        # - \
        # 2/sum([x.num_bursts for x in completed_processes])
    cpu_utilization = total_burst_time/total_sim_time

    return {'avg_burst': avg_burst, 'avg_turnaround': avg_turnaround,
            'avg_wait': avg_wait, 'num_preemptions': num_preemptions,
            'num_context_switches': num_context_switches, 'cpu_utilization': cpu_utilization*100}


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
    completed_processes: List[Process] = []

    total_burst_time = 0
    num_preemptions = 0
    num_context_switches = 0

    timer = 0

    cpu = CPU()
    cpu_process = None

    timer = 0
    if timer < 1000:
        print(
            f"time {timer}ms: Simulator started for RR with time slice {time_slice}ms [Q empty]")
    sigma_time_slice = 0

    while len(completed_processes) != n:
        # cpu burst
        if not cpu.inUse and cpu.contextOutTimer == 0:
            if ready_queue:
                # if in ready queue, it def has a burst
                cpu_process = ready_queue.pop(0)
                cpu_process.state = State.RUNNING
                cpu.contextInTimer = (context_switch_time // 2) - 1
                num_context_switches += 1
                cpu_process.num_context_switches += 1
                cpu.burstTimer = cpu_process.cpu_bursts.pop(0)
                cpu.inUse = True
        else:
            # if in use, count down context timer, then count down burst timer
            # handle context switch timer into of cpu
            if cpu.contextInTimer != 0:
                cpu.contextInTimer -= 1
                if cpu.contextInTimer == 0:
                    if not cpu_process.interrupted:
                        if timer < 1000:
                            print(
                                f'time {timer}ms: Process {cpu_process.id} started using the CPU for {cpu.burstTimer}ms burst {queue_to_string(ready_queue)}')
                        cpu_process.previousBurstTime = cpu.burstTimer
                    else:
                        cpu_process.interrupted = False
                        if timer < 1000:
                            print(
                                f'time {timer}ms: Process {cpu_process.id} started using the CPU for remaining {cpu.burstTimer}ms of {cpu_process.previousBurstTime} burst {queue_to_string(ready_queue)}')
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
                    total_burst_time += 1
                    sigma_time_slice -= 1
                    if cpu.burstTimer == 0:
                        cpu.contextOutTimer = (context_switch_time // 2)
                        # if no io burst, terminate
                        if cpu_process.io_bursts[0] != None:
                            if timer < 1000:
                                print(
                                    f'time {timer}ms: Process {cpu_process.id} completed a CPU burst; {len(cpu_process.cpu_bursts)} burst{"s" if len(cpu_process.cpu_bursts) != 1 else ""} to go {queue_to_string(ready_queue)}')
                            # sum = current io burst timer + iterate through waiting queue and get their burst times + this process's io burst time
                            added_time = cpu_process.io_bursts.pop(0)
                            waiting_queue.append(
                                (cpu_process, timer + added_time + context_switch_time // 2))
                            if timer < 1000:
                                print(
                                    f'time {timer}ms: Process {cpu_process.id} switching out of CPU; will block on I/O until time {timer + added_time + context_switch_time // 2}ms {queue_to_string(ready_queue)}')
                            cpu_process.interrupted = False
                            waiting_queue = sorted(
                                waiting_queue, key=lambda x: (x[1], x[0].id))
                        else:
                            print(
                                f'time {timer}ms: Process {cpu_process.id} terminated {queue_to_string(ready_queue)}')
                            completed_processes.append(cpu_process)

                    elif sigma_time_slice == 0:
                        if not ready_queue:
                            sigma_time_slice = time_slice
                            if timer < 1000:
                                print(
                                    f'time {timer}ms: Time slice expired; no preemption because ready queue is empty [Q empty]')
                        else:
                            cpu.contextOutTimer = (context_switch_time // 2)
                            num_preemptions += 1
                            if timer < 1000:
                                print(
                                    f'time {timer}ms: Time slice expired; process {cpu_process.id} preempted with {cpu.burstTimer}ms to go {queue_to_string(ready_queue)}')
                            cpu_process.cpu_bursts.insert(0, cpu.burstTimer)
                            cpu_process.interrupted = True
                            cpu.burstTimer = 0
                            ready_queue.append(cpu_process)
                            cpu_process.wait_time -= 1 + context_switch_time // 2 
        # increment wait time for processses in ready queue
        for process in ready_queue:
            process.wait_time += 1
        # io burst
        while waiting_queue and waiting_queue[0][1] == timer:
            io_process = waiting_queue.pop(0)[0]
            ready_queue.append(io_process)
            if timer < 1000:
                print(
                    f'time {timer}ms: Process {io_process.id} completed I/O; added to ready queue {queue_to_string(ready_queue)}')

        # new arrival
        while processes and processes[0].arrival_time == timer:
            process = processes.pop(0)
            ready_queue.append(process)
            if timer < 1000:
                print(
                    f'time {process.arrival_time}ms: Process {process.id} arrived; added to ready queue {queue_to_string(ready_queue)}')

        # increment turnaround time for our current cpu_process
        if cpu_process is not None:
            cpu_process.turnaround_time += 1

        timer += 1

    total_sim_time = timer + (context_switch_time // 2)-1
    print(f'time {total_sim_time}ms: Simulator ended for RR [Q empty]')

    avg_burst = sum([x.burst_time for x in completed_processes]) / \
        sum([x.num_bursts for x in completed_processes])
    avg_turnaround = sum([(x.burst_time + x.num_context_switches*context_switch_time + x.wait_time)
                         for x in completed_processes])/sum([x.num_bursts for x in completed_processes])
    avg_wait = sum([x.wait_time for x in completed_processes]) / \
        sum([x.num_bursts for x in completed_processes]) 
    cpu_utilization = total_burst_time/total_sim_time

    return {'avg_burst': avg_burst, 'avg_turnaround': avg_turnaround,
            'avg_wait': avg_wait, 'num_preemptions': num_preemptions,
            'num_context_switches': num_context_switches, 'cpu_utilization': cpu_utilization*100}
