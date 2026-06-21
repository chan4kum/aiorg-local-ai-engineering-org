import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from orchestrator.graphs.full_build import create_full_build_graph


def test_compile():
    print("Initializing OpenClaw Graph Compilation...")
    try:
        app = create_full_build_graph()
        print("\n✔ Success: LangGraph compiled completely with 0 missing node definitions.")
        print("\n--- Visualizing Graph Topology ---")

        # Prints ASCII structure to console
        app.get_graph().print_ascii()

    except Exception as e:
        print(f"\n❌ Compilation Failed: {e!s}")
        sys.exit(1)

if __name__ == "__main__":
    test_compile()
