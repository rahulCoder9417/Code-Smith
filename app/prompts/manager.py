from pathlib import Path

class PromptManager:
    def __init__(self):
        self.template_dir = Path(__file__).parent / "templates"

    def render(self, template_name: str, **kwargs) -> str:
        """
        Load a prompt template and replace placeholders.

        Example:
            render(
                "explanation",
                topic="Binary Search",
                difficulty="Beginner"
            )
        """

        template_path = self.template_dir / f"{template_name}.txt"

        if not template_path.exists():
            raise FileNotFoundError(
                f"Template '{template_name}' not found."
            )

        template = template_path.read_text(encoding="utf-8")

        try:
            return template.format(**kwargs)
        except KeyError as e:
            raise ValueError(
                f"Missing template variable: {e.args[0]}"
            )