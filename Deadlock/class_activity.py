import threading
import time


class BankAccount:
	def __init__(self, name: str, balance: int) -> None:
		self.name = name
		self.balance = balance
		# Semaphore used as a mutex lock (binary semaphore)
		self.mutex = threading.Semaphore(1)

	def __repr__(self) -> str:
		return f"BankAccount(name={self.name!r}, balance={self.balance})"


def transfer(src: BankAccount, dst: BankAccount, amount: int, start_barrier: threading.Barrier) -> None:
	"""Transfer money with a critical section protected by semaphore locks.

	This intentionally acquires locks in a fixed order (src then dst).
	When two threads call transfer() in opposite directions at the same time,
	they can deadlock: each holds one lock and waits forever on the other.
	"""
	start_barrier.wait()

	print(f"[{threading.current_thread().name}] wants {amount} from {src.name} -> {dst.name}", flush=True)

	print(f"[{threading.current_thread().name}] locking {src.name}", flush=True)
	src.mutex.acquire()
	try:
		print(f"[{threading.current_thread().name}] locked {src.name}", flush=True)
		# Give the other thread time to lock its own source account.
		time.sleep(0.2)

		print(f"[{threading.current_thread().name}] locking {dst.name}", flush=True)
		dst.mutex.acquire()
		try:
			print(f"[{threading.current_thread().name}] locked {dst.name}", flush=True)

			# ---- Critical section (both resources held) ----
			if src.balance < amount:
				print(f"[{threading.current_thread().name}] insufficient funds in {src.name}", flush=True)
				return

			src.balance -= amount
			dst.balance += amount
			print(
				f"[{threading.current_thread().name}] transferred {amount}: {src.name}={src.balance}, {dst.name}={dst.balance}",
				flush=True,
			)
			# ----------------------------------------------
		finally:
			dst.mutex.release()
			print(f"[{threading.current_thread().name}] released {dst.name}", flush=True)
	finally:
		src.mutex.release()
		print(f"[{threading.current_thread().name}] released {src.name}", flush=True)


def main() -> None:
	account1 = BankAccount("account1", 1000)
	account2 = BankAccount("account2", 1000)

	# Barrier to start both threads at the same time
	start_barrier = threading.Barrier(2)

	t1 = threading.Thread(
		target=transfer,
		name="T1",
		args=(account1, account2, 100, start_barrier),
		daemon=True,
	)
	t2 = threading.Thread(
		target=transfer,
		name="T2",
		args=(account2, account1, 200, start_barrier),
		daemon=True,
	)

	print("Starting threads...", flush=True)
	t1.start()
	t2.start()

	print("If it deadlocks, it will freeze after both threads lock one account.", flush=True)
	print("Press Ctrl+C to stop.", flush=True)

	try:
		t1.join()
		t2.join()
	except KeyboardInterrupt:
		print("\nStopped (likely deadlock occurred).", flush=True)

	print(f"Final: {account1} | {account2}", flush=True)


if __name__ == "__main__":
	main()
