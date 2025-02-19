from connect.cli.plugins.shared.sync_stats import SynchronizerStats
from connect.cli.plugins.product.sync.actions import ActionsSynchronizer
from connect.client import ConnectClient


def test_skipped(mocker, get_sync_actions_env):
    stats = SynchronizerStats()
    synchronizer = ActionsSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        progress=mocker.MagicMock(),
        stats=stats,
    )

    synchronizer.open('./tests/fixtures/actions_sync.xlsx', 'Actions')
    synchronizer.sync()

    assert stats['Actions'].get_counts_as_dict() == {
        'processed': 1, 'created': 0, 'updated': 0,
        'deleted': 0, 'skipped': 1, 'errors': 0,
    }


def test_validate_wrong_action(mocker, fs, get_sync_actions_env):
    get_sync_actions_env['Actions']['C2'] = 'test'
    get_sync_actions_env.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = ActionsSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        progress=mocker.MagicMock(),
        stats=stats,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Actions')
    synchronizer.sync()

    assert stats['Actions'].get_counts_as_dict() == {
        'processed': 1, 'created': 0, 'updated': 0,
        'deleted': 0, 'skipped': 0, 'errors': 1,
    }
    assert stats['Actions']._row_errors == {
        2: ['Allowed action values are `-`, `create`, `update` or `delete`. test is not valid '
            'action.'],
    }


def test_validate_no_verbose_id(mocker, fs, get_sync_actions_env):
    get_sync_actions_env['Actions']['A2'] = None
    get_sync_actions_env['Actions']['C2'] = 'update'
    get_sync_actions_env.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = ActionsSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        progress=mocker.MagicMock(),
        stats=stats,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Actions')
    synchronizer.sync()

    assert stats['Actions'].get_counts_as_dict() == {
        'processed': 1, 'created': 0, 'updated': 0,
        'deleted': 0, 'skipped': 0, 'errors': 1,
    }
    assert stats['Actions']._row_errors == {2: ['Verbose ID is required for update action.']}


def test_validate_wrong_id(mocker, fs, get_sync_actions_env):
    get_sync_actions_env['Actions']['B2'] = 'wrong id'
    get_sync_actions_env['Actions']['C2'] = 'update'
    get_sync_actions_env.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = ActionsSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        progress=mocker.MagicMock(),
        stats=stats,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Actions')
    synchronizer.sync()

    assert stats['Actions'].get_counts_as_dict() == {
        'processed': 1, 'created': 0, 'updated': 0,
        'deleted': 0, 'skipped': 0, 'errors': 1,
    }
    assert stats['Actions']._row_errors == {
        2: ['Actions ID must contain only letters, numbers and `_`, provided wrong id'],
    }


def test_validate_wrong_scope(mocker, fs, get_sync_actions_env):
    get_sync_actions_env['Actions']['C2'] = 'update'
    get_sync_actions_env['Actions']['G2'] = 'tier3'
    get_sync_actions_env.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = ActionsSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        progress=mocker.MagicMock(),
        stats=stats,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Actions')
    synchronizer.sync()

    assert stats['Actions'].get_counts_as_dict() == {
        'processed': 1, 'created': 0, 'updated': 0,
        'deleted': 0, 'skipped': 0, 'errors': 1,
    }
    assert stats['Actions']._row_errors == {
        2: ['Action scope must be one of `asset`, `tier1` or `tier2`. Provided tier3'],
    }


def test_delete(mocker, fs, get_sync_actions_env, mocked_responses):
    get_sync_actions_env['Actions']['C2'] = 'delete'
    get_sync_actions_env.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = ActionsSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        progress=mocker.MagicMock(),
        stats=stats,
    )

    mocked_responses.add(
        method='DELETE',
        url='https://localhost/public/v1/products/PRD-276-377-545/actions/ACT-276-377-545-001',
        status=204,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Actions')
    synchronizer.sync()

    assert stats['Actions'].get_counts_as_dict() == {
        'processed': 1, 'created': 0, 'updated': 0,
        'deleted': 1, 'skipped': 0, 'errors': 0,
    }


def test_delete_404(mocker, fs, get_sync_actions_env, mocked_responses):
    get_sync_actions_env['Actions']['C2'] = 'delete'
    get_sync_actions_env.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = ActionsSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        progress=mocker.MagicMock(),
        stats=stats,
    )

    mocked_responses.add(
        method='DELETE',
        url='https://localhost/public/v1/products/PRD-276-377-545/actions/ACT-276-377-545-001',
        status=404,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Actions')
    synchronizer.sync()

    assert stats['Actions'].get_counts_as_dict() == {
        'processed': 1, 'created': 0, 'updated': 0,
        'deleted': 1, 'skipped': 0, 'errors': 0,
    }


def test_delete_500(mocker, fs, get_sync_actions_env, mocked_responses):
    get_sync_actions_env['Actions']['C2'] = 'delete'
    get_sync_actions_env.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = ActionsSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        progress=mocker.MagicMock(),
        stats=stats,
    )

    mocked_responses.add(
        method='DELETE',
        url='https://localhost/public/v1/products/PRD-276-377-545/actions/ACT-276-377-545-001',
        status=500,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Actions')
    synchronizer.sync()

    assert stats['Actions'].get_counts_as_dict() == {
        'processed': 1, 'created': 0, 'updated': 0,
        'deleted': 0, 'skipped': 0, 'errors': 1,
    }
    assert stats['Actions']._row_errors == {2: ['500 Internal Server Error']}


def test_update(mocker, fs, get_sync_actions_env, mocked_responses, mocked_actions_response):
    get_sync_actions_env['Actions']['C2'] = 'update'

    response = mocked_actions_response[0]

    get_sync_actions_env.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = ActionsSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        progress=mocker.MagicMock(),
        stats=stats,
    )

    mocked_responses.add(
        method='PUT',
        url='https://localhost/public/v1/products/PRD-276-377-545/actions/ACT-276-377-545-001',
        json=response,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Actions')
    synchronizer.sync()

    assert stats['Actions'].get_counts_as_dict() == {
        'processed': 1, 'created': 0, 'updated': 1,
        'deleted': 0, 'skipped': 0, 'errors': 0,
    }


def test_update_500(mocker, fs, get_sync_actions_env, mocked_responses, mocked_actions_response):
    get_sync_actions_env['Actions']['C2'] = 'update'

    get_sync_actions_env.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = ActionsSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        progress=mocker.MagicMock(),
        stats=stats,
    )

    mocked_responses.add(
        method='PUT',
        url='https://localhost/public/v1/products/PRD-276-377-545/actions/ACT-276-377-545-001',
        status=500,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Actions')
    synchronizer.sync()

    assert stats['Actions'].get_counts_as_dict() == {
        'processed': 1, 'created': 0, 'updated': 0,
        'deleted': 0, 'skipped': 0, 'errors': 1,
    }
    assert stats['Actions']._row_errors == {2: ['500 Internal Server Error']}


def test_create(mocker, fs, get_sync_actions_env, mocked_responses, mocked_actions_response):
    get_sync_actions_env['Actions']['A2'] = None
    get_sync_actions_env['Actions']['C2'] = 'create'
    get_sync_actions_env['Actions']['B2'] = 'test_id'

    response = mocked_actions_response[0]

    get_sync_actions_env.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = ActionsSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        progress=mocker.MagicMock(),
        stats=stats,
    )

    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/products/PRD-276-377-545/actions',
        headers={
            'Content-Range': 'items 0-3/4',
        },
        json=mocked_actions_response,
    )
    mocked_responses.add(
        method='POST',
        url='https://localhost/public/v1/products/PRD-276-377-545/actions',
        json=response,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Actions')
    synchronizer.sync()

    assert stats['Actions'].get_counts_as_dict() == {
        'processed': 1, 'created': 1, 'updated': 0,
        'deleted': 0, 'skipped': 0, 'errors': 0,
    }


def test_create_500(mocker, fs, get_sync_actions_env, mocked_responses, mocked_actions_response):
    get_sync_actions_env['Actions']['A2'] = None
    get_sync_actions_env['Actions']['C2'] = 'create'
    get_sync_actions_env['Actions']['B2'] = 'test_id'

    get_sync_actions_env.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = ActionsSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        progress=mocker.MagicMock(),
        stats=stats,
    )

    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/products/PRD-276-377-545/actions',
        headers={
            'Content-Range': 'items 0-3/4',
        },
        json=mocked_actions_response,
    )
    mocked_responses.add(
        method='POST',
        url='https://localhost/public/v1/products/PRD-276-377-545/actions',
        status=500,
    )

    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Actions')
    synchronizer.sync()

    assert stats['Actions'].get_counts_as_dict() == {
        'processed': 1, 'created': 0, 'updated': 0,
        'deleted': 0, 'skipped': 0, 'errors': 1,
    }
    assert stats['Actions']._row_errors == {2: ['500 Internal Server Error']}


def test_create_skip_if_action_id_already_exists(
    mocker, fs, get_sync_actions_env, mocked_responses, mocked_actions_response,
):
    get_sync_actions_env['Actions']['A2'] = None
    get_sync_actions_env['Actions']['C2'] = 'create'

    get_sync_actions_env.save(f'{fs.root_path}/test.xlsx')

    stats = SynchronizerStats()
    synchronizer = ActionsSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        progress=mocker.MagicMock(),
        stats=stats,
    )

    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/products/PRD-276-377-545/actions',
        headers={
            'Content-Range': 'items 0-3/4',
        },
        json=mocked_actions_response,
    )
    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Actions')
    synchronizer.sync()

    assert stats['Actions'].get_counts_as_dict() == {
        'processed': 1, 'created': 0, 'updated': 0,
        'deleted': 0, 'skipped': 1, 'errors': 0,
    }


def test_skip_create_if_action_id_exists_but_update_if_differs_from_source(
    mocker, fs, get_sync_actions_env, mocked_responses, mocked_actions_response,
):
    get_sync_actions_env['Actions']['A2'] = None
    get_sync_actions_env['Actions']['C2'] = 'create'
    get_sync_actions_env['Actions']['F2'] = 'New Test Description'

    get_sync_actions_env.save(f'{fs.root_path}/test.xlsx')

    response = mocked_actions_response[0]

    stats = SynchronizerStats()
    synchronizer = ActionsSynchronizer(
        client=ConnectClient(
            use_specs=False,
            api_key='ApiKey SU:123',
            endpoint='https://localhost/public/v1',
        ),
        progress=mocker.MagicMock(),
        stats=stats,
    )

    mocked_responses.add(
        method='GET',
        url='https://localhost/public/v1/products/PRD-276-377-545/actions',
        headers={
            'Content-Range': 'items 0-3/4',
        },
        json=mocked_actions_response,
    )
    mocked_responses.add(
        method='PUT',
        url='https://localhost/public/v1/products/PRD-276-377-545/actions/ACT-276-377-545-001',
        json=response,
    )
    synchronizer.open(f'{fs.root_path}/test.xlsx', 'Actions')
    synchronizer.sync()

    assert stats['Actions'].get_counts_as_dict() == {
        'processed': 1, 'created': 0, 'updated': 1,
        'deleted': 0, 'skipped': 0, 'errors': 0,
    }
