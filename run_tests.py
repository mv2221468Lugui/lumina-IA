import sys
import unittest
from pathlib import Path

root = Path(__file__).resolve().parent
suite = unittest.defaultTestLoader.discover(str(root / "tests"), pattern="test_*.py")
if suite.countTestCases() == 0:
    print("ERRO: nenhum teste encontrado", file=sys.stderr)
    sys.exit(2)
result = unittest.TextTestRunner(verbosity=2).run(suite)
sys.exit(0 if result.wasSuccessful() else 1)
