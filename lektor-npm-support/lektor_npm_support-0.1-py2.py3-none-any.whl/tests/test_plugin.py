import py


def test_disabled_by_default(plugin):
    extra_flags = {}
    assert not plugin.is_enabled(extra_flags)


def test_enabled_with_npm_flag(plugin):
    extra_flags = {"npm": True}
    assert plugin.is_enabled(extra_flags)


def npm_call(mock_call, folder, npm, *args):
    return mock_call([npm] + list(args), cwd=folder)


def assert_exact_calls(mock, expected_calls, **kwargs):
    mock.assert_has_calls(expected_calls, any_order=True)
    assert mock.call_count == len(expected_calls), "wrong number of subprocesses"


def test_build(plugin, builder, env_path, mock_popen, mock_call):
    plugin.on_before_build_all(builder)
    assert_exact_calls(mock_popen, [
        npm_call(mock_call, env_path / 'webpack', 'npm', 'install'),
        npm_call(mock_call, env_path / 'webpack', 'npm', 'run', 'build'),
        npm_call(mock_call, env_path / 'parcel', 'yarn', 'install'),
        npm_call(mock_call, env_path / 'parcel', 'yarn', 'run', 'dummy_build')
        ])
    assert not plugin.proc


def test_watch(plugin, env_path, mock_popen, mock_call):
    plugin.on_server_spawn(extra_flags={"npm": True})
    assert_exact_calls(mock_popen, [
        npm_call(mock_call, env_path / 'webpack', 'npm', 'install'),
        npm_call(mock_call, env_path / 'webpack', 'npm', 'run', 'dummy_watch'),
        npm_call(mock_call, env_path / 'parcel', 'yarn', 'install'),
        npm_call(mock_call, env_path / 'parcel', 'yarn', 'run', 'watch')
        ])
    plugin.on_server_stop()
    assert not plugin.proc


def test_build_plugin_disabled(plugin, builder, mock_popen):
    builder.extra_flags={}
    plugin.on_before_build_all(builder)
    mock_popen.assert_not_called()
    
def test_watch_plugin_disabled(plugin, mock_popen):
    plugin.on_server_spawn(extra_flags={})
    mock_popen.assert_not_called()
