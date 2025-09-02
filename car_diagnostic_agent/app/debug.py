import sys
import site

print("--- sys.path ---")
for p in sys.path:
    print(p)

print("\n--- site packages ---")
print(site.getsitepackages())
