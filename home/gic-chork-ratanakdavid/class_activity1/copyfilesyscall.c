#include <fcntl.h>
#include <unistd.h>    // For read(), write(), close()
#include <stdio.h>     // For perror()
#include <stdlib.h>    // For exit()

int main() {
    int src_fd, dest_fd;         // File descriptors
    ssize_t nread;               // Number of bytes read
    char buffer[1024];           // Temporary data buffer

    // 1️⃣ Open the source file for reading
    src_fd = open("result.txt", O_RDONLY);
    if (src_fd < 0) {
        perror("Error opening result.txt");
        exit(1);
    }

    // 2️⃣ Open or create the destination file for writing
    dest_fd = open("copyresult.txt", O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if (dest_fd < 0) {
        perror("Error opening copyresult.txt");
        close(src_fd);
        exit(1);
    }

    // 3️⃣ Read from source and write to destination
    while ((nread = read(src_fd, buffer, sizeof(buffer))) > 0) {
        if (write(dest_fd, buffer, nread) != nread) {
            perror("Error writing to copyresult.txt");
            close(src_fd);
            close(dest_fd);
            exit(1);
        }
    }

    if (nread < 0)
        perror("Error reading result.txt");

    // 4️⃣ Close both files
    close(src_fd);
    close(dest_fd);

    printf("✅ File copied successfully using system calls.\n");
    return 0;
}
