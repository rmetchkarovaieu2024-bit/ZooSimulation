import subprocess
import sys

RUNS = 5


for i in range(1, RUNS + 1):
    print(f"\n{'='*60}")
    print(f"  RUN {i} of {RUNS}")
    print(f"{'='*60}\n")
    result = subprocess.run([sys.executable, "main.py"])
    if result.returncode != 0:
        print(f" Run {i} exited with code {result.returncode}")

print(f"\n{'='*60}")
print(f"  BATCH COMPLETE — {RUNS} runs finished")
print(f"{'='*60}\n")

# in terminl, run this command to clear the database before running the batch again:
# python3 -c "import os; os.remove('zoo.db') if os.path.exists('zoo.db') else print('no db found')"
