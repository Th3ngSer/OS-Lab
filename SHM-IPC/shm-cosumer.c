#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <unistd.h>

#define SHM_NAME "/myshm"
#define SHM_SIZE 1024

int main() {
    int shm_fd;
    char *ptr;

    // Open shared memory
    shm_fd = shm_open(SHM_NAME, O_RDONLY, 0666);
    if (shm_fd == -1) {
        perror("shm_open");
        exit(1);
    }

    // Map shared memory
    ptr = mmap(0, SHM_SIZE, PROT_READ, MAP_SHARED, shm_fd, 0);
    if (ptr == MAP_FAILED) {
        perror("mmap");
        exit(1);
    }

    // Read message
    printf("Consumer: %s\n", ptr);

    // Remove shared memory (cleanup)
    shm_unlink(SHM_NAME);

    return 0;
}
