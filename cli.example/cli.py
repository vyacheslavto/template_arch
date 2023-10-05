import sys
from pathlib import Path

sys.path.append(str(Path(".").absolute()))

module_name = sys.argv[1]
argv = " ".join(sys.argv[2:])

exec("import %s" % module_name)
exec(f"asyncio.run({module_name}.{argv})")
