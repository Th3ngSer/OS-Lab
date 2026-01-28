#include<iostream>
#include<vector>
using namespace std;

struct Process {
    int id;
    int arrivalTime;
    int burstTime;
    int remainingTime;
    int completionTime;
    int turnaroundTime; // CT - AT
    int waitingTime;    // TAT - BT
};

void simulateFCFS(vector<Process>& processes) {
    int currentTime = 0;
    for (auto& p : processes) {
        if (currentTime < p.arrivalTime) {
            currentTime = p.arrivalTime; // CPU waits if no one is here
        }
        p.waitingTime = currentTime - p.arrivalTime;
        currentTime += p.burstTime;
        p.turnaroundTime = p.waitingTime + p.burstTime;
        p.completionTime = currentTime;
    }
    cout << "Process\tAT\tBT\tCT\tTAT\tWT\n";
    for (const auto& p : processes) {   
        cout << p.id << "\t" << p.arrivalTime << "\t" << p.burstTime << "\t"
             << p.completionTime << "\t" << p.turnaroundTime << "\t" << p.waitingTime << "\n";
    }
}

int main(){
    // cout << "Hello, CPU Scheduling Simulator!" << endl;
    vector<Process> processes = {
        {1, 0, 5, 5, 0, 0, 0},
        {2, 1, 3, 3, 0, 0, 0},
        {3, 2, 8, 8, 0, 0, 0},
        {4, 3, 6, 6, 0, 0, 0}
    };

    simulateFCFS(processes);

    return 0;
}