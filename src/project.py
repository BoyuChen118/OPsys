import sys
import os
from typing import List
import algorithms
from process import Process
import math
import copy
import matplotlib.pyplot as plt


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
        self.srand48(seed)

    def srand48(self, seedval):
        self.Xn = (seedval << 16) + 0x330E

    def drand48(self):
        self.Xn = (0x5DEECE66D * self.Xn + 0xB) & (2 ** 48 - 1)
        return self.Xn / (2 ** 48)

    def next_exp(self):
        var = -math.log(self.drand48())/self.λ
        while var > self.upper_bound:
            var = -math.log(self.drand48())/self.λ
        return var

    def create_processes(self):
        tau = math.ceil(1/self.λ)
        self.processes = []
        for id in range(self.n):
            arrival_time = math.floor(self.next_exp())
            num_bursts = math.ceil(self.drand48()*100)
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
                f'Process {process.id} (arrival time {process.arrival_time} ms) {process.num_bursts} CPU burst{"s" if process.num_bursts != 1 else ""} (tau {tau}ms)')
    def question_two(self):
        self.create_processes()
        # algorithms.sjf, algorithms.srt, algorithms.rr):
        # for alg in [algorithms.fcfs]:
        x = []
        y = []
        y2 = []
        for i in range(100):
            self.α = i + 1
            x.append(self.α)
            for name, algorithm in (('SJF', algorithms.sjf), ('SRT', algorithms.srt)):
                p = copy.deepcopy(self.processes)
                sim = algorithm(p, self.context_switch_time,
                                self.α, self.time_slice)
                if name == 'SJF':
                    y.append(sim["avg_turnaround"])
                else:
                    y2.append(sim["avg_turnaround"])
        plt.plot(x,y, label = 'SJF')
        plt.plot(x,y2, label = 'SRT')
        plt.xlabel('α value')
        plt.ylabel('avg_turnaround_time (in milliseconds)')
        plt.title('Figure 2')
        plt.legend()
        plt.show()


    def question_one(self):
        # algorithms.sjf, algorithms.srt, algorithms.rr):
        # for alg in [algorithms.fcfs]:
        x = []
        y = []
        y2 = []
        y3 = []
        y4 = []
        for i in range(1,26):
            self.processes = i
            self.create_processes()
            x.append(i)
            for name, algorithm in (('FCFS', algorithms.fcfs), ('SJF', algorithms.sjf), ('SRT', algorithms.srt), ('RR', algorithms.rr)):
                p = copy.deepcopy(self.processes)
                sim = algorithm(p, self.context_switch_time,
                                self.α, self.time_slice)
                if name == 'FCFS':
                    y.append(sim["avg_turnaround"])
                elif name == 'SJF':
                    y2.append(sim["avg_turnaround"])
                elif name == 'SRT':
                    y3.append(sim["avg_turnaround"])
                else:  #RR 
                    y4.append(sim["avg_turnaround"])
        plt.plot(x,y, label = 'FCFS', color = 'k')
        plt.plot(x,y2, label = 'SJF', color = 'b')
        plt.plot(x,y3, label = 'SRT', color = 'r')
        plt.plot(x,y4, label = 'RR', color = 'y')
        plt.xlabel('processes')
        plt.ylabel('avg_turnaround_time (in milliseconds)')
        plt.title('Figure 1')
        plt.legend()
        plt.show()
                
    def run_simulation(self):
        self.create_processes()
        # algorithms.sjf, algorithms.srt, algorithms.rr):
        # for alg in [algorithms.fcfs]:

                
            

        with open('simout.txt', 'w+') as f:

            for name, algorithm in (('FCFS', algorithms.fcfs), ('SJF', algorithms.sjf), ('SRT', algorithms.srt), ('RR', algorithms.rr)):
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


if __name__ == '__main__':
    if len(sys.argv) != 8:
        print("ERROR: Its error", file=sys.stderr)
        sys.exit(1)
    _, n, seed, λ, upper_bound, context_switch_time, α, time_slice = sys.argv

    try:
        n, seed, λ, upper_bound, context_switch_time, α, time_slice = int(n), int(
            seed), float(λ), int(upper_bound), int(context_switch_time), float(α), int(time_slice)
    except:
        print("ERROR: Its except", file=sys.stderr)
        sys.exit(1)

    if n > 26 or n < 1:
        print("ERROR: Its error", file=sys.stderr)
        sys.exit(1)
    if λ <= 0:
        print("ERROR: Its error", file=sys.stderr)
        sys.exit(1)

    if upper_bound <= 0:
        print("ERROR: Its error", file=sys.stderr)
        sys.exit(1)

    if context_switch_time <= 0:
        print("ERROR: Its error", file=sys.stderr)
        sys.exit(1)

    if time_slice <= 0:
        print("ERROR: Its error", file=sys.stderr)
        sys.exit(1)

    if α <= 0:
        print("ERROR: Its error", file=sys.stderr)
        sys.exit(1)

    try:
        simulation = Simulation(n, seed, λ, upper_bound,
                                context_switch_time, α, time_slice)

        simulation.run_simulation()
        # simulation.question_one()
        # simulation.question_two()
    except:
        print("ERROR: Its except", file=sys.stderr)
        sys.exit(1)
