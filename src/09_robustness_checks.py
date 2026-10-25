"""Execute the reproducible Week 4 statistical diagnostics and sensitivities.

This replaces the original synopsis-stage *description-only* placeholder.
The two-way cluster tests are EXPLORATORY and not finite-cluster calibrated.
"""
from pathlib import Path
import subprocess
import sys
HERE = Path(__file__).resolve().parent
for name in ['week4_model_diagnostics.py','week4_cluster_sensitivity.py']:
    print(f'Running {name}',flush=True)
    subprocess.run([sys.executable,str(HERE/name)], check=True)
print('Verified Week 4 modelling diagnostics and exploratory clustered sensitivity completed.')
