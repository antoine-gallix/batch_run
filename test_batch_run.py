from pathlib import Path

from click.testing import CliRunner
from pytest import fixture

from batch_run import escape, run, substitute_dir


@fixture
def test_files(monkeypatch, tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    (source / "file_1.ext").touch()
    (source / "file_2.ext").touch()
    (source / "file_3.ext").touch()
    (tmp_path / "destination").mkdir()
    monkeypatch.chdir(tmp_path)


# -----------------------------------------------


def test_escape():
    assert (
        escape("path/to/dir/filename with spaces.ext")
        == '"path/to/dir/filename with spaces.ext"'
    )


def test_substitute_dir():
    assert substitute_dir(
        Path("an/other/dir"), Path("path/to/dir/filename.ext")
    ) == Path("an/other/dir/filename.ext")


# -----------------------------------------------



def test_input_dir_only_no_command(test_files):
    runner = CliRunner()
    result = runner.invoke(run, ["source"])
    assert result.exit_code == 0
    assert set(result.output.strip().split("\n")) == set(
        ["source/file_2.ext", "source/file_1.ext", "source/file_3.ext"]
    )


def test_input_dir_only(test_files):
    runner = CliRunner()
    result = runner.invoke(
        run, ["source", "--command", "process-files --option value {}"]
    )
    assert result.exit_code == 0
    assert set(result.output.strip().split("\n")) == set(
        [
            'process-files --option value "source/file_1.ext"',
            'process-files --option value "source/file_2.ext"',
            'process-files --option value "source/file_3.ext"',
        ]
    )


def test_with_output_dir_no_command(test_files):
    runner = CliRunner()
    result = runner.invoke(run, ["source", "--dest", "destination"])
    assert result.exit_code == 0
    assert set(result.output.strip().split("\n")) == set(
        [
            "source/file_2.ext destination/file_2.ext",
            "source/file_1.ext destination/file_1.ext",
            "source/file_3.ext destination/file_3.ext",
        ]
    )


def test_with_output_dir(test_files):
    runner = CliRunner()
    result = runner.invoke(
        run,
        [
            "source",
            "--dest",
            "destination",
            "--command",
            'process-files --option value --to {} {}',
        ],
    )
    assert result.exit_code == 0
    assert set(result.output.strip().split("\n")) == set(
        [
            'process-files --option value --to "source/file_2.ext" "destination/file_2.ext"',
            'process-files --option value --to "source/file_1.ext" "destination/file_1.ext"',
            'process-files --option value --to "source/file_3.ext" "destination/file_3.ext"',
        ]
    )
