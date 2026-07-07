import os
import subprocess
import sys
import tempfile


class CoverageRunner:
    def __init__(self, target_dir: str, timeout: int = 600):
        self.target_dir = target_dir
        self.timeout = timeout

    def run(self) -> str | None:
        if not os.path.isdir(self.target_dir):
            return None

        xml_path = os.path.join(self.target_dir, "coverage.xml")
        if os.path.exists(xml_path):
            return xml_path

        tmp = tempfile.NamedTemporaryFile(
            suffix=".xml", prefix="coverage-", delete=False, mode="w"
        )
        xml_path = tmp.name
        tmp.close()

        try:
            self._run_coverage(xml_path)
        except (subprocess.CalledProcessError, FileNotFoundError, OSError):
            os.unlink(xml_path)
            return None

        if os.path.exists(xml_path) and os.path.getsize(xml_path) > 0:
            return xml_path

        os.unlink(xml_path)
        return None

    def _run_coverage(self, xml_path: str) -> None:
        cmd = [
            sys.executable,
            "-m",
            "coverage",
            "run",
            "-m",
            "pytest",
            "--quiet",
        ]
        env = {**os.environ, "PYTHONWARNINGS": "ignore"}

        subprocess.run(
            cmd,
            cwd=self.target_dir,
            env=env,
            capture_output=True,
            timeout=self.timeout,
            check=False,
        )

        xml_cmd = [
            sys.executable,
            "-m",
            "coverage",
            "xml",
            "-o", xml_path,
        ]
        subprocess.run(
            xml_cmd,
            cwd=self.target_dir,
            env=env,
            capture_output=True,
            timeout=60,
            check=True,
        )
