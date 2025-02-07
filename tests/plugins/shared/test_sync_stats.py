from connect.cli.plugins.shared.sync_stats import SynchronizerStats, SynchronizerStatsSingleModule


def test_synchronizer_stats_module_get_counts():
    stats = SynchronizerStats()
    stats['module 1'].updated()
    stats['module 1'].created()
    stats['module 1'].deleted()
    stats['module 1'].skipped()
    stats['module 1'].error('error message', 5)

    assert stats['module 1'].get_counts_as_dict() == {
        'processed': 5, 'created': 1, 'updated': 1, 'deleted': 1, 'skipped': 1, 'errors': 1,
    }


def test_synchronizer_stats_print(capsys, mocker):
    mocker.patch('builtins.input', lambda *args: 'y')
    mocked_table = mocker.patch(
        'connect.cli.plugins.shared.sync_stats.console.table',
    )
    mocked_header = mocker.patch(
        'connect.cli.plugins.shared.sync_stats.console.header',
    )

    stats = SynchronizerStats()
    stats['module 1'].updated()
    stats['module 1'].created()
    stats['module 2'].deleted()
    stats['module 2'].skipped()
    stats['module 2'].error('error message', 3)
    stats.print()

    mocked_header.assert_called_once_with('Results of synchronization')

    mocked_table.assert_called_once_with(
        columns=SynchronizerStats.COLUMNS,
        rows=[
            ('module 1', 2, 1, 1, 0, 0, 0),
            ('module 2', 3, 0, 0, 1, 1, 1),
        ],
        expand=True,
    )

    captured = capsys.readouterr()

    assert 'Sync operation had 1 errors, do you want to see them?' in captured.out
    assert """
Module module 2:

  Errors at row #3
    - error message
""" in captured.out


def test_synchronizer_stats_print_no_errors(capsys, mocker):
    mocked_table = mocker.patch(
        'connect.cli.plugins.shared.sync_stats.console.table',
    )
    mocked_header = mocker.patch(
        'connect.cli.plugins.shared.sync_stats.console.header',
    )

    stats = SynchronizerStats()
    stats['module 1'].updated()
    stats['module 1'].created()
    stats['module 2'].deleted()
    stats['module 2'].skipped()
    stats.print()

    mocked_header.assert_called_once_with('Results of synchronization')

    mocked_table.assert_called_once_with(
        columns=SynchronizerStats.COLUMNS,
        rows=[
            ('module 1', 2, 1, 1, 0, 0, 0),
            ('module 2', 2, 0, 0, 1, 1, 0),
        ],
        expand=True,
    )

    captured = capsys.readouterr()
    assert captured.out == ''


def test_synchronizer_stats_print_multi_errors(capsys, mocker):
    mocker.patch('builtins.input', lambda *args: 'y')
    mocked_table = mocker.patch(
        'connect.cli.plugins.shared.sync_stats.console.table',
    )
    mocked_header = mocker.patch(
        'connect.cli.plugins.shared.sync_stats.console.header',
    )

    stats = SynchronizerStats()
    stats['module 1'].error('first error', 1)
    stats['module 1'].error(['second error', 'third error'], 1)
    stats['module 1'].error('another error', 2)
    stats['module 2'].error('an error')
    stats['module 2'].error('row error', 1)
    stats['module 3'].error('the only error')
    stats.print()

    mocked_header.assert_called_once_with('Results of synchronization')

    mocked_table.assert_called_once_with(
        columns=SynchronizerStats.COLUMNS,
        rows=[
            ('module 1', 2, 0, 0, 0, 0, 2),
            ('module 2', 2, 0, 0, 0, 0, 2),
            ('module 3', 1, 0, 0, 0, 0, 1),
        ],
        expand=True,
    )

    captured = capsys.readouterr()

    assert 'Sync operation had 5 errors, do you want to see them?' in captured.out

    assert """
Module module 1:

  Errors at row #1
    - first error
    - second error
    - third error

  Errors at row #2
    - another error

Module module 2:

  Errors
    - an error

  Errors at row #1
    - row error

Module module 3:

  Errors
    - the only error

""" in captured.out


def test_synchronizer_stats_print_repeated_errors(capsys, console_80_columns, mocker):
    mocker.patch('builtins.input', lambda *args: 'y')
    mocked_table = mocker.patch(
        'connect.cli.plugins.shared.sync_stats.console.table',
    )
    mocked_header = mocker.patch(
        'connect.cli.plugins.shared.sync_stats.console.header',
    )

    stats = SynchronizerStats()
    stats['module 1'].error(['first error', 'second error'], [1, 2])
    stats.print()

    mocked_header.assert_called_once_with('Results of synchronization')

    mocked_table.assert_called_once_with(
        columns=SynchronizerStats.COLUMNS,
        rows=[
            ('module 1', 2, 0, 0, 0, 0, 2),
        ],
        expand=True,
    )

    captured = capsys.readouterr()

    assert 'Sync operation had 2 errors, do you want to see them?' in captured.out

    assert """
Module module 1:

  Errors at rows #1 to #2
    - first error
    - second error

""" in captured.out


def test_synchronizer_stats_initial_modules_reset():
    stats = SynchronizerStats('module 1', 'module 2')
    stats['module 1'].updated()
    stats['module 2'].deleted()
    stats['module 3'].skipped()

    stats.reset()

    assert list(stats) == ['module 1', 'module 2']


def test_synchronizer_stats_single_module_print(capsys, mocker):
    mocker.patch('builtins.input', lambda *args: 'y')
    mocked_table = mocker.patch(
        'connect.cli.plugins.shared.sync_stats.console.table',
    )
    mocked_header = mocker.patch(
        'connect.cli.plugins.shared.sync_stats.console.header',
    )

    stats = SynchronizerStatsSingleModule('module A')
    stats.updated()
    stats.error('error message', 2)
    stats.print()

    mocked_header.assert_called_once_with('Results of synchronization')

    mocked_table.assert_called_once_with(
        columns=SynchronizerStats.COLUMNS,
        rows=[
            ('module A', 2, 0, 1, 0, 0, 1),
        ],
        expand=True,
    )

    captured = capsys.readouterr()

    assert 'Sync operation had 1 errors, do you want to see them?' in captured.out

    assert """
Module module A:

  Errors at row #2
    - error message

""" in captured.out
