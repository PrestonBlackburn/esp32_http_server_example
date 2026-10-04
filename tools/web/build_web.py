# In charge of rendering any HTML Jinja

from pathlib import Path
import gzip, shutil, sys
from jinja2 import Environment, FileSystemLoader

ROOT = Path(__file__).resolve().parents[2]
TEMPLATE_DIR = ROOT / "templates"
OUTPUT_DIR = ROOT / "renders"
STATIC_DIR = ROOT / "static"

def get_jinja_env(template_dir:str) -> Environment:
    env = Environment(loader=FileSystemLoader(template_dir))
    return env


def render_pages(template_dir: Path, static_dir: Path, output_dir: Path):
    env = get_jinja_env(template_dir)
    for tpl in template_dir.glob("*.html"):
        if tpl.name.startswith("_"):
            continue
        html = env.get_template(tpl.name).render()
        (output_dir / tpl.name).write_text(html, encoding="utf-8")

    for f in static_dir.iterdir():
        shutil.copy(f, output_dir / f.name)

    # C will send Gzip to frontend
    for f in list(output_dir.iterdir()):
        if f.suffix != ".gz":
            with open(f, "rb") as i, gzip.GzipFile(f"{f}.gz", "wb", mtime=0) as o:
                shutil.copyfileobj(i, o)


if __name__ == "__main__":
    # env = get_jinja_env(str(TEMPLATE_DIR))
    # root = env.get_template("pages/live_demo.html")
    # output = root.render()
    # print(output)
    render_pages(TEMPLATE_DIR, STATIC_DIR, OUTPUT_DIR)