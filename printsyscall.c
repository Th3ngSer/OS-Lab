#include <unistd.h>
#include <string.h>

int main() {
    const char *msg = "Hello from system call write()!\n";
    write(STDOUT_FILENO, msg, strlen(msg));
    return 0;
}
