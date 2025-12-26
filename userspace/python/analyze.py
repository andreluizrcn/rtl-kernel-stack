# userspace/python/analyze.py
import sys


path = "results/logs/fifo_test.log"

def analize_log(path):    
    try:
        with open(path, "r") as f:
            results = []
            for line in f:
                if not line.strip(): # pass empty lines 
                    continue

                parts = line.split()
                record = {}
         
            for part in parts:
                if '=' in part:
                    key, value = part.split('=')
                    record[key] = int (value) # convertion 
            all_results.append(record)
        return all_results 
    
    except FileNotFoundError:
        print("File {filepath} not found, run simulation first", file=sys.stderr) 
        sys.exit(1)

data = analize_log(path)
for d in data:
    print(f"Test: in={d['data_in']} out={d['data_out']}")

