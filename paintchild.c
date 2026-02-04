#include <stdio.h>

int main() {
    STARTUPINFO si;
    PROCESS_INFORMATION pi;

    ZeroMemory(&si, sizeof(si));
    si.cb = sizeof(si);
    ZeroMemory(&pi, sizeof(pi));

    // Replace this path if needed
    // Default location for mspaint on Windows 10/11:
    // C:\\Windows\\System32\\mspaint.exe
    if (!CreateProcess(
            "C:\\Program Files\\WindowsApps\\Microsoft.Paint_11.2509.441.0_x64__8wekyb3d8bbwe\\PaintApp",   // application
            NULL, NULL, NULL, FALSE, 0, NULL, NULL,
            &si, &pi)) {
        printf("CreateProcess failed. Error: %d\n", GetLastError());
        return 1;
    }

    printf("Child process (mspaint.exe) started!\n");
    printf("PID: %ld\n", pi.dwProcessId);

    return 0;
}
