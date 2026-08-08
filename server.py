import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

from jelly_mcp.server import mcp

if __name__ == "__main__":
    mcp.run()
