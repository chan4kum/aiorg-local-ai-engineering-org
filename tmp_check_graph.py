import sys, traceback
# Ensure the project root is in sys.path for top-level packages
sys.path.append('.')
from orchestrator.graphs.full_build import create_full_build_graph
try:
    g = create_full_build_graph()
    print('Graph compiled successfully')
except Exception as e:
    print('Error during compilation:', e)
    traceback.print_exc()
