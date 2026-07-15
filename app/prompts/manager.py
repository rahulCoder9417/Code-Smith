from pathlib import Path


class PromptManager:

    def __init__(self):
        base = Path(__file__).parent

        self.system_dir = base / "system"
        self.user_dir = base / "user"

    def load_system(self, name: str) -> str:

        path = self.system_dir / f"{name}.txt"

        if not path.exists():
            raise FileNotFoundError(
                f"System prompt '{name}' not found."
            )

        return path.read_text(encoding="utf-8")

    def render_user(self, template_name: str, **kwargs):

        path = self.user_dir / f"{template_name}.txt"

        if not path.exists():
            raise FileNotFoundError(
                f"User template '{template_name}' not found."
            )

        template = path.read_text(encoding="utf-8")

        try:
            return template.format(**kwargs)

        except KeyError as e:
            raise ValueError(
                f"Missing variable '{e.args[0]}'"
            )