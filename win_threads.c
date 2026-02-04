#include <stdio.h>

DWORD WINAPI worker(LPVOID p) {
    int id = (int)(SIZE_T)p;
    for (int i = 1; i <= 25; i++) {
        printf("Thread %d step %d\n", id, i);
        Sleep(200);
    }
    return 0;
}

int main() {
    const int N = 12;  // more threads
    HANDLE th[N];

    printf("PID: %lu\n", GetCurrentProcessId());

    for (int i = 0; i < N; i++) {
        th[i] = CreateThread(NULL, 0, worker, (LPVOID)(SIZE_T)i, 0, NULL);
    }

    WaitForMultipleObjects(N, th, TRUE, INFINITE);
    for (int i = 0; i < N; i++) CloseHandle(th[i]);

    printf("Done\n");
    return 0;
}
