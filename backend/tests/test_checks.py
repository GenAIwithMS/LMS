import os
import subprocess
import sys

import pytest

# Each check script builds its own small database in memory and prints PASS / FAIL
# for every check. They run one at a time in a separate Python process, so they
# don't share a database.
CHECKS_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "checks")

CHECK_FILES = []
for file_name in sorted(os.listdir(CHECKS_FOLDER)):
    if file_name.startswith("check_") and file_name.endswith(".py"):
        CHECK_FILES.append(file_name)


@pytest.mark.parametrize("file_name", CHECK_FILES)
def test_check_script(file_name):
    result = subprocess.run(
        [sys.executable, os.path.join(CHECKS_FOLDER, file_name)],
        capture_output=True,
        text=True,
        timeout=600,
    )

    # Show only the lines that matter if something failed
    report = []
    for line in (result.stdout + result.stderr).splitlines():
        if line.startswith("FAIL") or "Error" in line or "Traceback" in line:
            report.append(line)

    assert result.returncode == 0, f"{file_name} failed:\n" + "\n".join(report)
