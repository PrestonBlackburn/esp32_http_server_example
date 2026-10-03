# In charge of rendering any HTML Jinja

from jinja2 import Environment, FileSystemLoader


def get_jinja_env(template_dir:str) -> Environment:
    env = Environment(loader=FileSystemLoader(template_dir))
    return env


if __name__ == "__main__":
    template_dir = './templates'
    env = get_jinja_env(template_dir)

    root = env.get_template("pages/live_demo.html")
    context = {}
    output = root.render(context = context)
    print(output)