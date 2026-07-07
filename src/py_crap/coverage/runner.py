from __future__ import annotations

import os
import subprocess
import sys
import tempfile


class CoverageRunner:
    def __init__(self, target_dir: str, timeout: int = 600, verbose: bool = False):
        self.target_dir = target_dir
        self.timeout = timeout
        self.verbose = verbose

    def _log(self, msg: str) -> None:
        if self.verbose:
            print(f"[debug] CoverageRunner: {msg}", file=sys.stderr)

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
            if os.path.exists(xml_path):
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

        r1 = subprocess.run(
            cmd,
            cwd=self.target_dir,
            env=env,
            capture_output=True,
            timeout=self.timeout,
            check=False,
        )
        if r1.returncode != 0:
            self._log(f"coverage run failed (exit {r1.returncode})")
            if r1.stderr:
                self._log(f"stderr: {r1.stderr.decode().strip()}")
            if r1.stdout:
                self._log(f"stdout: {r1.stdout.decode().strip()}")

        xml_cmd = [
            sys.executable,
            "-m",
            "coverage",
            "xml",
            "-o", xml_path,
        ]
        r2 = subprocess.run(
            xml_cmd,
            cwd=self.target_dir,
            env=env,
            capture_output=True,
            timeout=60,
            check=False,
        )
        if r2.returncode != 0:
            msg = f"coverage xml failed (exit {r2.returncode})"
            if r2.stderr:
                msg += f": {r2.stderr.decode().strip()}"
            self._log(msg)
            raise subprocess.CalledProcessError(
                r2.returncode, xml_cmd, output=r2.stdout, stderr=r2.stderr
            )
