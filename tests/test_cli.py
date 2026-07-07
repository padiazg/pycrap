import os

from click.testing import CliRunner

from py_crap.cli.main import cli

TESTDATA_DIR = os.path.join(os.path.dirname(__file__), "testdata")


def test_version():
    runner = CliRunner()
    result = runner.invoke(cli, ["version"])
    assert result.exit_code == 0
    assert "py-crap" in result.output


def test_version_simple():
    runner = CliRunner()
    result = runner.invoke(cli, ["version", "--simple"])
    assert result.exit_code == 0
    assert "0.1" in result.output


def test_scan_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["scan", "--help"])
    assert result.exit_code == 0
    assert "threshold" in result.output
    assert "format" in result.output


def test_scan_table_output():
    runner = CliRunner()
    result = runner.invoke(cli, ["scan", TESTDATA_DIR])
    assert result.exit_code == 0
    assert "simple" in result.output
    assert "with_if" in result.output


def test_scan_top_filter():
    runner = CliRunner()
    result = runner.invoke(cli, ["scan", TESTDATA_DIR, "--top", "3"])
    assert result.exit_code == 0


def test_scan_min_filter():
    runner = CliRunner()
    result = runner.invoke(cli, ["scan", TESTDATA_DIR, "--min", "5"])
    assert result.exit_code == 0


def test_scan_json_output():
    runner = CliRunner()
    result = runner.invoke(cli, ["scan", TESTDATA_DIR, "-f", "json"])
    assert result.exit_code == 0
    assert '"function"' in result.output


def test_scan_fail_above():
    runner = CliRunner()
    result = runner.invoke(cli, ["scan", TESTDATA_DIR, "--fail-above", "--threshold", "1"])
    assert result.exit_code == 1


def test_scan_github_annotations():
    runner = CliRunner()
    result = runner.invoke(cli, ["scan", TESTDATA_DIR, "-f", "github"])
    assert result.exit_code == 0


def test_scan_sarif_output():
    runner = CliRunner()
    result = runner.invoke(cli, ["scan", TESTDATA_DIR, "-f", "sarif"])
    assert result.exit_code == 0
    assert "$schema" in result.output


def test_scan_pr_comment():
    runner = CliRunner()
    result = runner.invoke(cli, ["scan", TESTDATA_DIR, "-f", "pr-comment"])
    assert result.exit_code == 0


def test_scan_output_file():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ["scan", TESTDATA_DIR, "-o", "results.json"])
        assert result.exit_code == 0
        assert os.path.exists("results.json")
