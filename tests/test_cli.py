from importlib import import_module


def test_cli_paths_lists_docs_path(capsys) -> None:
    main = import_module("requirement_insight_agent.cli").main
    exit_code = main(["paths"])

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "docs: docs" in captured.out


def test_cli_status_reports_package(capsys) -> None:
    main = import_module("requirement_insight_agent.cli").main
    exit_code = main(["status"])

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "package: present" in captured.out