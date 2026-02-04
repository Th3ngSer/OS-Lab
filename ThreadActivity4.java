import java.util.concurrent.*;
import java.util.*;

public class ThreadActivity4 {

    static void runExecutor(String title, ExecutorService exec) throws InterruptedException {
        System.out.println("\n=== " + title + " ===");
        for (int i = 1; i <= 10; i++) {
            final int id = i;
            exec.submit(() -> {
                String t = Thread.currentThread().getName();
                System.out.println("Task " + id + " running on " + t);
                try { Thread.sleep(300); } catch (InterruptedException ignored) {}
            });
        }
        exec.shutdown();
        exec.awaitTermination(10, TimeUnit.SECONDS);
        System.out.println(title + " finished.");
    }

    // ForkJoin demo
    static class SumTask extends RecursiveTask<Long> {
        int[] arr; int lo, hi;
        static final int THRESHOLD = 20000;

        SumTask(int[] arr, int lo, int hi) { this.arr = arr; this.lo = lo; this.hi = hi; }

        @Override
        protected Long compute() {
            if (hi - lo <= THRESHOLD) {
                long sum = 0;
                for (int i = lo; i < hi; i++) sum += arr[i];
                System.out.println("Computed [" + lo + "," + hi + ") by " + Thread.currentThread().getName());
                return sum;
            }
            int mid = (lo + hi) / 2;
            SumTask left = new SumTask(arr, lo, mid);
            SumTask right = new SumTask(arr, mid, hi);
            left.fork();
            long r = right.compute();
            long l = left.join();
            return l + r;
        }
    }

    public static void main(String[] args) throws Exception {
        runExecutor("SingleThreadExecutor", Executors.newSingleThreadExecutor());
        runExecutor("CachedThreadPool", Executors.newCachedThreadPool());

        System.out.println("\n=== ForkJoinPool Demo ===");
        int[] arr = new int[100000];
        Arrays.fill(arr, 1);

        ForkJoinPool pool = new ForkJoinPool(); // parallelism = CPU cores
        long result = pool.invoke(new SumTask(arr, 0, arr.length));
        pool.shutdown();

        System.out.println("Result = " + result);
        System.out.println("Parallelism = " + ForkJoinPool.commonPool().getParallelism());
    }
}
