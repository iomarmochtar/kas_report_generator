from pathlib import Path, PosixPath

CUR_DIR: PosixPath = Path(__file__).resolve().parent
TEMPLATE_DIR: PosixPath = CUR_DIR.joinpath('templates')