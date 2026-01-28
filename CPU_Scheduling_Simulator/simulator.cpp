#include <iostream>
#include <vector>
#include <algorithm>
#include <iomanip>
#include <fstream>
#include <queue>



// The Process structure to hold process details
struct Process {
    int id;
    int arrivalTime;
    int burstTime;
    int remainingTime;
    int completionTime;
    int turnaroundTime; // CT - AT
    int waitingTime;    // TAT - BT
};


// Function to simulate Shortest Remaining Time First (SRTF) scheduling

void simulateSRTF(std::vector<Process>& proc) {
    int n = proc.size();
    int completed = 0, currentTime = 0, minRemaining = 1e9;
    int shortest = 0;
    bool found = false;

    while (completed != n) {
        // Find process with minimum remaining time that has arrived
        for (int i = 0; i < n; i++) {
            if ((proc[i].arrivalTime <= currentTime) && (proc[i].remainingTime < minRemaining) && proc[i].remainingTime > 0) {
                minRemaining = proc[i].remainingTime;
                shortest = i;
                found = true;
            }
        }

        if (!found) {
            currentTime++;
            continue;
        }

        // Reduce remaining time by 1ms (the "tick")
        proc[shortest].remainingTime--;
        minRemaining = proc[shortest].remainingTime;
        if (minRemaining == 0) minRemaining = 1e9;

        if (proc[shortest].remainingTime == 0) {
            completed++;
            found = false;
            proc[shortest].completionTime = currentTime + 1;
            proc[shortest].turnaroundTime = proc[shortest].completionTime - proc[shortest].arrivalTime;
            proc[shortest].waitingTime = proc[shortest].turnaroundTime - proc[shortest].burstTime;
        }
        currentTime++;
    }
}


// Function to simulate Round Robin (RR) scheduling

void simulateRR(std::vector<Process>& proc, int quantum) {
    int n = proc.size();
    std::vector<int> rem_bt(n);
    for (int i = 0; i < n; i++) rem_bt[i] = proc[i].burstTime;

    std::queue<int> q;
    int currentTime = 0;
    int completed = 0;
    int i = 0; // index for newly arriving processes (proc must be sorted by AT)

    // push processes that arrive at time 0
    while (i < n && proc[i].arrivalTime <= currentTime) {
        q.push(i);
        i++;
    }

    while (completed < n) {
        if (q.empty()) {
            // CPU idle -> jump to next arrival
            currentTime = std::max(currentTime, proc[i].arrivalTime);
            while (i < n && proc[i].arrivalTime <= currentTime) {
                q.push(i);
                i++;
            }
            continue;
        }

        int idx = q.front();
        q.pop();

        int run = std::min(quantum, rem_bt[idx]);
        rem_bt[idx] -= run;
        currentTime += run;

        // push any processes that arrived during this time slice
        while (i < n && proc[i].arrivalTime <= currentTime) {
            q.push(i);
            i++;
        }

        if (rem_bt[idx] > 0) {
            q.push(idx); // not finished, go back to queue
        } else {
            completed++;
            proc[idx].completionTime = currentTime;
            proc[idx].turnaroundTime = proc[idx].completionTime - proc[idx].arrivalTime;
            proc[idx].waitingTime = proc[idx].turnaroundTime - proc[idx].burstTime;
        }
    }
}


// Function to print the results

void printResults(std::vector<Process>& proc) {
    double totalWT = 0, totalTAT = 0;
    std::cout << "ID\tAT\tBT\tCT\tTAT\tWT\n";
    for (const auto& p : proc) {
        totalWT += p.waitingTime;
        totalTAT += p.turnaroundTime;
        std::cout << p.id << "\t" << p.arrivalTime << "\t" << p.burstTime << "\t" 
                  << p.completionTime << "\t" << p.turnaroundTime << "\t" << p.waitingTime << "\n";
    }
    std::cout << "\nAverage Waiting Time: " << totalWT / proc.size();
    std::cout << "\nAverage Turnaround Time: " << totalTAT / proc.size() << "\n";
}

int main() {
    std::vector<Process> processes;
    std::ifstream inputFile("processes.txt");

    if (!inputFile) {
        std::cerr << "Error: Could not open processes.txt" << std::endl;
        return 1;
    }

    int id, at, bt;
    while (inputFile >> id >> at >> bt) {
        processes.push_back({id, at, bt, bt, 0, 0, 0});
    }
    inputFile.close();

    // Sort by arrival time
    std::sort(processes.begin(), processes.end(), [](const Process& a, const Process& b) {
        if (a.arrivalTime != b.arrivalTime) return a.arrivalTime < b.arrivalTime;
        return a.id < b.id;
    });

    std::cout << "--- CPU Scheduling Simulator ---\n";

    // ---- SRTF ----
    auto srtf = processes; // copy
    for (auto &p : srtf) {
        p.remainingTime = p.burstTime;
        p.completionTime = p.turnaroundTime = p.waitingTime = 0;
    }
    simulateSRTF(srtf);
    std::cout << "\n[SRTF Results]\n";
    printResults(srtf);

    // ---- RR ----
    auto rr = processes; // copy
    for (auto &p : rr) {
        p.remainingTime = p.burstTime;
        p.completionTime = p.turnaroundTime = p.waitingTime = 0;
    }

    int quantum = 2; // change as needed
    simulateRR(rr, quantum);
    std::cout << "\n[RR Results] (Quantum = " << quantum << ")\n";
    printResults(rr);

    return 0;
}
