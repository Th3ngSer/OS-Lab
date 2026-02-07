#include<iostream>
#include<vector>
#include<fstream>
#include<iomanip>
#include<limits>
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
    double totalWT = 0, totalTAT = 0;
    cout << "Process\tAT\tBT\tCT\tTAT\tWT\n";
    for (const auto& p : processes) {   
        totalWT += p.waitingTime;
        totalTAT += p.turnaroundTime;
        cout << p.id << "\t" << p.arrivalTime << "\t" << p.burstTime << "\t"
             << p.completionTime << "\t" << p.turnaroundTime << "\t" << p.waitingTime << "\n";
    }
    if (!processes.empty()) {
        cout << "\nAverage Waiting Time: " << fixed << setprecision(2) << (totalWT / processes.size()) << "\n";
        cout << "Average Turnaround Time: " << fixed << setprecision(2) << (totalTAT / processes.size()) << "\n";
    }
}

bool loadProcessesFromFile(const string& filePath, vector<Process>& processes) {
    ifstream inputFile(filePath);
    if (!inputFile) {
        return false;
    }

    vector<Process> temp;
    int id, at, bt;
    while (inputFile >> id >> at >> bt) {
        if (at < 0 || bt <= 0) {
            continue;
        }
        temp.push_back({id, at, bt, bt, 0, 0, 0});
    }

    if (temp.empty()) {
        return false;
    }

    processes = temp;
    return true;
}

void printProcesses(const vector<Process>& processes) {
    if (processes.empty()) {
        cout << "No processes loaded.\n";
        return;
    }
    cout << "ID\tAT\tBT\n";
    for (const auto& p : processes) {
        cout << p.id << "\t" << p.arrivalTime << "\t" << p.burstTime << "\n";
    }
}

void resetStats(vector<Process>& processes) {
    for (auto& p : processes) {
        p.remainingTime = p.burstTime;
        p.completionTime = 0;
        p.turnaroundTime = 0;
        p.waitingTime = 0;
    }
}

void enterProcessesManually(vector<Process>& processes) {
    int n = 0;
    cout << "Enter number of processes: ";
    while (!(cin >> n) || n <= 0) {
        cout << "Invalid number. Try again: ";
        cin.clear();
        cin.ignore(numeric_limits<streamsize>::max(), '\n');
    }

    vector<Process> temp;
    for (int i = 0; i < n; ++i) {
        int id, at, bt;
        cout << "Process " << (i + 1) << " ID: ";
        while (!(cin >> id)) {
            cout << "Invalid ID. Try again: ";
            cin.clear();
            cin.ignore(numeric_limits<streamsize>::max(), '\n');
        }
        cout << "Arrival Time: ";
        while (!(cin >> at) || at < 0) {
            cout << "Invalid Arrival Time. Try again: ";
            cin.clear();
            cin.ignore(numeric_limits<streamsize>::max(), '\n');
        }
        cout << "Burst Time: ";
        while (!(cin >> bt) || bt <= 0) {
            cout << "Invalid Burst Time. Try again: ";
            cin.clear();
            cin.ignore(numeric_limits<streamsize>::max(), '\n');
        }
        temp.push_back({id, at, bt, bt, 0, 0, 0});
    }

    processes = temp;
}

int main(){
    vector<Process> processes;
    const string defaultFile = "processes.txt";

    cout << "========================================\n";
    cout << "      CPU Scheduling Simulator (FCFS)   \n";
    cout << "========================================\n\n";

    if (loadProcessesFromFile(defaultFile, processes)) {
        cout << "Loaded processes from " << defaultFile << "\n\n";
    } else {
        cout << "No input file found or file is empty.\n";
        cout << "You can load a file or enter processes manually.\n\n";
    }

    int choice = 0;
    while (true) {
        cout << "Menu:\n";
        cout << "1) Load processes from file\n";
        cout << "2) Enter processes manually\n";
        cout << "3) Show current processes\n";
        cout << "4) Run FCFS simulation\n";
        cout << "5) Exit\n";
        cout << "Select an option: ";

        if (!(cin >> choice)) {
            cin.clear();
            cin.ignore(numeric_limits<streamsize>::max(), '\n');
            cout << "Invalid input. Try again.\n\n";
            continue;
        }

        if (choice == 1) {
            cout << "Enter file path (default: processes.txt): ";
            string filePath;
            cin >> filePath;
            if (filePath.empty()) filePath = defaultFile;

            if (loadProcessesFromFile(filePath, processes)) {
                cout << "Loaded processes from " << filePath << "\n\n";
            } else {
                cout << "Failed to load file or file is empty.\n\n";
            }
        } else if (choice == 2) {
            enterProcessesManually(processes);
            cout << "Processes saved.\n\n";
        } else if (choice == 3) {
            printProcesses(processes);
            cout << "\n";
        } else if (choice == 4) {
            if (processes.empty()) {
                cout << "No processes available. Load or enter processes first.\n\n";
                continue;
            }
            resetStats(processes);
            cout << "\n[FCFS Results]\n";
            simulateFCFS(processes);
            cout << "\n";
        } else if (choice == 5) {
            cout << "Goodbye!\n";
            break;
        } else {
            cout << "Invalid option. Try again.\n\n";
        }
    }

    return 0;
}