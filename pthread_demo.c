#include <pthread.h>
#include <stdio.h>
#include <unistd.h>

#define N 8

void* worker(void* arg) {
    long id = (long)arg;
    printf("Thread %ld started | pthread_self=%lu\n", id, (unsigned long)pthread_self());
    for (int i = 1; i <= 6; i++) {
        printf("Thread %ld -> step %d\n", id, i);
        usleep(200000);
    }
    printf("Thread %ld finished\n", id);
    return NULL;
}

int main() {
    pthread_t t[N];

    printf("Main started\n");
    for (long i = 0; i < N; i++) {
        pthread_create(&t[i], NULL, worker, (void*)i);
    }
    for (int i = 0; i < N; i++) {
        pthread_join(t[i], NULL);
    }
    printf("Main finished\n");
    return 0;
}
