"""Build the installable Sublime package from runtime files only."""
import json
from pathlib import Path
import zipfile


def main():
    root = Path(__file__).resolve().parent
    package = root / "package" / "SmartSoftWrap"
    files = (
        ".python-version",
        "LICENSE",
        "Default.sublime-commands",
        "SmartSoftWrap.sublime-settings",
        "Soft Wrap Characters.sublime-syntax",
        "Soft Wrap Words.sublime-syntax",
        "soft_wrap.py",
    )
    for name in files:
        path = package / name
        if not path.is_file():
            raise FileNotFoundError(path)
        if name.endswith((".sublime-settings", ".sublime-commands")):
            json.loads(path.read_text(encoding="utf-8"))
        elif name.endswith(".py"):
            compile(path.read_text(encoding="utf-8"), str(path), "exec")
    output = root / "dist" / "SmartSoftWrap.sublime-package"
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(".tmp")
    with zipfile.ZipFile(temporary, "w", zipfile.ZIP_DEFLATED) as archive:
        for name in files:
            archive.write(package / name, name)
    temporary.replace(output)
    print(output)


if __name__ == "__main__":
    main()
