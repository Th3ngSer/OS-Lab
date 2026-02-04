#include <fcntl.h>
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>

int main() {
    const char *src = "result.txt";
    const char *dst = "copyresult.txt";

    int fd_in = open(src, O_RDONLY);
    if (fd_in < 0) {
        perror("open result.txt");
        return 1;
    }

    int fd_out = open(dst, O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if (fd_out < 0) {
        perror("open copyresult.txt");
        close(fd_in);
        return 1;
    }

    char buf[1024];
    ssize_t bytesRead;

    while ((bytesRead = read(fd_in, buf, sizeof(buf))) > 0) {
        ssize_t totalWritten = 0;
        while (totalWritten < bytesRead) {
            ssize_t bytesWritten = write(fd_out, buf + totalWritten, bytesRead - totalWritten);
            if (bytesWritten < 0) {
                perror("write");
                close(fd_in);
                close(fd_out);
                return 1;
            }
            totalWritten += bytesWritten;
        }
    }

    if (bytesRead < 0) {
        perror("read");
    }

    close(fd_in);
    close(fd_out);

    printf("✅ Copied '%s' to '%s'\n", src, dst);
    return 0;
}
# Class Activity 1
 Class Activity 1
