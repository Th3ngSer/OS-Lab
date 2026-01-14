import java.util.concurrent.CyclicBarrier;
import java.util.concurrent.Semaphore;

public class DeadlockSimulation {
    static final class BankAccount {
        final String name;
        int balance;
        final Semaphore mutex = new Semaphore(1);

        BankAccount(String name, int balance) {
            this.name = name;
            this.balance = balance;
        }

        @Override
        public String toString() {
            return "BankAccount{name='" + name + "', balance=" + balance + "}";
        }
    }

    static void transfer(BankAccount src, BankAccount dst, int amount, CyclicBarrier startBarrier) {
        try {
            startBarrier.await();

            System.out.println("[" + Thread.currentThread().getName() + "] wants " + amount + " from " + src.name + " -> " + dst.name);

            System.out.println("[" + Thread.currentThread().getName() + "] locking " + src.name);
            src.mutex.acquire();
            try {
                System.out.println("[" + Thread.currentThread().getName() + "] locked " + src.name);

                // Give the other thread time to lock its own source account.
                Thread.sleep(200);

                System.out.println("[" + Thread.currentThread().getName() + "] locking " + dst.name);
                dst.mutex.acquire();
                try {
                    System.out.println("[" + Thread.currentThread().getName() + "] locked " + dst.name);

                    // ---- Critical section (both resources held) ----
                    if (src.balance < amount) {
                        System.out.println("[" + Thread.currentThread().getName() + "] insufficient funds in " + src.name);
                        return;
                    }

                    src.balance -= amount;
                    dst.balance += amount;
                    System.out.println("[" + Thread.currentThread().getName() + "] transferred " + amount
                            + ": " + src.name + "=" + src.balance + ", " + dst.name + "=" + dst.balance);
                    // ----------------------------------------------
                } finally {
                    dst.mutex.release();
                    System.out.println("[" + Thread.currentThread().getName() + "] released " + dst.name);
                }
            } finally {
                src.mutex.release();
                System.out.println("[" + Thread.currentThread().getName() + "] released " + src.name);
            }
        } catch (Exception e) {
            // In a deadlock, you typically won't reach here.
            e.printStackTrace();
        }
    }

    public static void main(String[] args) {
        BankAccount account1 = new BankAccount("account1", 1000);
        BankAccount account2 = new BankAccount("account2", 1000);

        CyclicBarrier startBarrier = new CyclicBarrier(2);

        Thread t1 = new Thread(() -> transfer(account1, account2, 100, startBarrier), "T1");
        Thread t2 = new Thread(() -> transfer(account2, account1, 200, startBarrier), "T2");

        System.out.println("Starting threads...");
        t1.start();
        t2.start();

        System.out.println("If it deadlocks, it will freeze after both threads lock one account.");
        System.out.println("Use Ctrl+C to stop.");

        try {
            t1.join();
            t2.join();
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }

        System.out.println("Final: " + account1 + " | " + account2);
    }
}
