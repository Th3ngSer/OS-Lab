import java.util.concurrent.CyclicBarrier;
import java.util.concurrent.Semaphore;

public class DeadlockFreeSimulation {
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

    /**
     * Deadlock-free transfer:
     * We still use semaphore mutex locks, but we ALWAYS acquire the two account locks
     * in a consistent global order (by account name).
     */
    static void transfer(BankAccount src, BankAccount dst, int amount, CyclicBarrier startBarrier) {
        try {
            startBarrier.await();

            System.out.println("[" + Thread.currentThread().getName() + "] wants " + amount + " from " + src.name + " -> " + dst.name);

            BankAccount first = src;
            BankAccount second = dst;
            if (first.name.compareTo(second.name) > 0) {
                first = dst;
                second = src;
            }

            System.out.println("[" + Thread.currentThread().getName() + "] locking " + first.name);
            first.mutex.acquire();
            try {
                System.out.println("[" + Thread.currentThread().getName() + "] locked " + first.name);

                // Small delay just to prove it still won't deadlock.
                Thread.sleep(200);

                System.out.println("[" + Thread.currentThread().getName() + "] locking " + second.name);
                second.mutex.acquire();
                try {
                    System.out.println("[" + Thread.currentThread().getName() + "] locked " + second.name);

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
                    second.mutex.release();
                    System.out.println("[" + Thread.currentThread().getName() + "] released " + second.name);
                }
            } finally {
                first.mutex.release();
                System.out.println("[" + Thread.currentThread().getName() + "] released " + first.name);
            }
        } catch (Exception e) {
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

        try {
            t1.join();
            t2.join();
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }

        System.out.println("Completed without deadlock.");
        System.out.println("Final: " + account1 + " | " + account2);
    }
}
