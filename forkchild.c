#include <stdio.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/wait.h>

int main() {
    pid_t pid;

    printf("Parent process started (PID: %d)\n", getpid());

    pid = fork();  // create child process

    if (pid < 0) {
        perror("fork failed");
        return 1;
    }
    else if (pid == 0) {
        // Child process
        printf("Child process running (PID: %d)\n", getpid());
        execlp("ls", "ls", NULL);

        // exec only returns if it fails
        perror("exec failed");
        return 1;
    }
    else {
        // Parent process
        wait(NULL);  // wait for child to finish
        printf("Child process completed\n");
    }

    return 0;
}
