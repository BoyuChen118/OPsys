import sys
import os
import random
from typing import List
import algorithms
from process import Process
import math
import copy


class Simulation:
    def __init__(self, n, seed, λ, upper_bound, context_switch_time, α, time_slice):
        self.n = n
        self.seed = seed
        self.λ = λ
        self.upper_bound = upper_bound
        self.context_switch_time = context_switch_time
        self.α = α
        self.time_slice = time_slice
        self.processes: List[Process] = []

        random.seed(seed)

    def next_exp(self):
        var = random.expovariate(self.λ)
        while var > self.upper_bound:
            var = random.expovariate(self.λ)
        return var

    def create_processes(self):
        tau = math.ceil(1/self.λ)
        self.processes = []
        for id in range(self.n):
            arrival_time = math.floor(self.next_exp())
            num_bursts = 5  # math.ceil(random.random()*100)
            bursts = []
            for _ in range(num_bursts-1):
                cpu_burst_time = math.ceil(self.next_exp())
                io_burst_time = math.ceil(self.next_exp())*10
                bursts.append((cpu_burst_time, io_burst_time))
            # last burst doesn't have io
            bursts.append((math.ceil(self.next_exp()), None))
            self.processes.append(
                Process(id, arrival_time, num_bursts, bursts, tau)
            )
        for process in self.processes:
            print(
                f'Process {process.id} (arrival time {process.arrival_time} ms) {process.num_bursts} CPU bursts (tau {tau}ms)')

    def run_simulation(self):
        self.create_processes()
        # algorithms.sjf, algorithms.srt, algorithms.rr):
        # for alg in [algorithms.fcfs]:
        with open('simout.txt', 'w+') as f:
            for name, algorithm in (('FCFS', algorithms.fcfs), ('SJF', algorithms.sjf),('SRT',algorithms.srt), ('RR', algorithms.rr)):
                p = copy.deepcopy(self.processes)
                sim = algorithm(p, self.context_switch_time,
                                self.α, self.time_slice)
                output_lines = [
                    f'Algorithm {name}\n',
                    f'-- average CPU burst time: {sim["avg_burst"]:.3f} ms\n',
                    f'-- average wait time: {sim["avg_wait"]:.3f} ms\n',
                    f'-- average turnaround time: {sim["avg_turnaround"]:.3f} ms\n',
                    f'-- total number of context switches: {sim["num_context_switches"]}\n',
                    f'-- total number of preemptions: {sim["num_preemptions"]}\n',
                    f'-- CPU utilization: {sim["cpu_utilization"]:.3f}%\n',
                ]
                f.writelines(output_lines)
            print()


if __name__ == '__main__':
    _, n, seed, λ, upper_bound, context_switch_time, α, time_slice = sys.argv
    simulation = Simulation(int(n), int(seed), float(λ), int(upper_bound),
                            int(context_switch_time), float(α), int(time_slice))

    simulation.run_simulation()
