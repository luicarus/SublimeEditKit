"""Install a temporary test helper, run in Sublime, and remove the helper."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import time
import uuid


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sublime", required=True, help="Path to subl.exe")
    parser.add_argument("--packages", help="Sublime Packages directory (Windows default if omitted)")
    parser.add_argument("--output", default=str(Path(__file__).resolve().parents[1] / "dist" / "integration-results.json"))
    parser.add_argument("--baseline", action="store_true", help="Characterize ordinary plain-text wrapping")
    args = parser.parse_args()
    if args.packages:
        packages = Path(args.packages).resolve()
    elif os.name == "nt":
        packages = (Path(os.environ["APPDATA"]) / "Sublime Text" / "Packages").resolve()
    else:
        parser.error("--packages is required outside Windows")
    if not packages.is_dir():
        parser.error("Packages directory does not exist: {}".format(packages))
    helper_name = "SmartSoftWrapTests_" + uuid.uuid4().hex
    helper = packages / helper_name
    output = Path(args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    # An existing report must not be mistaken for the result of this run.
    unique_output = output.with_name(output.stem + "-" + uuid.uuid4().hex + ".json")
    helper.mkdir()
    try:
        source = Path(__file__).with_name("sublime_integration.py")
        shutil.copy2(source, helper / "sublime_integration.py")
        shutil.copy2(source.with_name("Custom Plain Text.sublime-syntax"), helper / "Custom Plain Text.sublime-syntax")
        (helper / ".python-version").write_text("3.14\n", encoding="ascii")
        time.sleep(2)
        command = "smart_soft_wrap_run_tests " + json.dumps({"output": str(unique_output), "baseline": args.baseline})
        subprocess.run([args.sublime, "--background", "--command", command], check=True)
        deadline = time.monotonic() + 45
        while not unique_output.exists():
            if time.monotonic() > deadline:
                raise RuntimeError("Sublime produced no report within 45 seconds")
            time.sleep(0.25)
        data = json.loads(unique_output.read_text(encoding="utf-8"))
        unique_output.replace(output)
        failed = [item for item in data["results"] if not item["passed"]]
        for item in data["results"]:
            print("{}: {}".format("PASS" if item["passed"] else "FAIL", item["name"]))
            if not item["passed"]:
                print(item["error"])
        print("Sublime {}: {}/{} passed; {}".format(data["build"], len(data["results"]) - len(failed), len(data["results"]), output))
        return 1 if failed else 0
    finally:
        # Only remove the exact package directory created by this invocation.
        target = helper.resolve()
        if target.parent != packages or target.name != helper_name:
            raise RuntimeError("Unsafe helper cleanup path: {}".format(target))
        shutil.rmtree(target)


if __name__ == "__main__":
    raise SystemExit(main())
