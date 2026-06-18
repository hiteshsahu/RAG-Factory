"""Launches the FastAPI bridge (api/main.py) via uvicorn.

Run as a plain script (`python scripts/serve_api.py`), never `python -m
scripts.serve_api` -- this needs Python's default behavior of putting the
*script's own directory* on sys.path[0], not the cwd. Repo root contains a
literal `raginator/` dir (one folder per stage, none with content directly
inside -- the real code is nested under each stage's src/), and if cwd were
on sys.path when `raginator.*` is first imported, PathFinder would find that
empty namespace portion before the editable-install finder gets a turn,
breaking `from raginator.chunk import FixedSizeChunker` and friends -- the
same collision class as the `python -m`/`-c` gotcha documented in README.md.

So: pre-import every raginator.<stage> subpackage here, while sys.path is
still just [scripts/, ...site-packages] -- this resolves and caches them
correctly. *Then* add repo root to sys.path so `api.main` (which lives
there) can be found -- safe at this point, since raginator.* is already
cached in sys.modules and won't be re-resolved.
"""

import sys
from pathlib import Path

import raginator.chunk  # noqa: F401
import raginator.core  # noqa: F401
import raginator.embed  # noqa: F401
import raginator.evaluate  # noqa: F401
import raginator.generate  # noqa: F401
import raginator.ingest  # noqa: F401
import raginator.observe  # noqa: F401
import raginator.pipeline  # noqa: F401
import raginator.rerank  # noqa: F401
import raginator.retrieve  # noqa: F401
import raginator.store  # noqa: F401
import uvicorn

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Single source of truth for where this binds -- the printed URLs below are
# built from these, not separately hardcoded, so they can't drift out of
# sync with the actual uvicorn.run() call.
HOST = "127.0.0.1"
PORT = 8001

if __name__ == "__main__":
    base_url = f"http://{HOST}:{PORT}"
    print(f"📖 API docs:  {base_url}/docs")
    print(f"📖 Route map: {base_url}/")
    # No reload=True: uvicorn's reloader respawns the worker via
    # multiprocessing's "spawn" start method, which re-launches a fresh
    # interpreter the same way `python -c` does -- cwd lands back on
    # sys.path[0] in that fresh process, before any of this module's code
    # (and its careful sys.path ordering) gets a chance to run again,
    # reintroducing the exact collision this script exists to avoid.
    # Restart `./go api` manually after editing api/ instead.
    uvicorn.run("api.main:app", host=HOST, port=PORT)
