import sys
import os
import src
print(f"DEBUG: src path is {src.__file__}")

# Add the current directory to sys.path so that 'src' is findable
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.main import main

if __name__ == "__main__":
    main()
