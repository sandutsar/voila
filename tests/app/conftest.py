import os
import pytest
import voila.app
import asyncio

BASE_DIR = os.path.dirname(__file__)


class VoilaTest(voila.app.Voila):
    def listen(self):
        pass  # the ioloop is taken care of by the pytest-tornado framework


@pytest.fixture
def voila_config():
    return lambda app: None


@pytest.fixture
def voila_args_extra():
    return ['--VoilaExecutor.timeout=240']


@pytest.fixture
def voila_config_file_paths_arg():
    # we don't want the tests to use any configuration on the system
    return '--VoilaTest.config_file_paths=[]'


@pytest.fixture
def voila_args(voila_notebook, voila_args_extra, voila_config_file_paths_arg):
    debug_args = ['--VoilaTest.log_level=DEBUG'] if os.environ.get('VOILA_TEST_DEBUG', False) else []
    return [voila_notebook, voila_config_file_paths_arg] + voila_args_extra + debug_args


@pytest.fixture(params=[False, True])
def preheat_mode(request):
    """Fixture used to activate/deactivate pre-heat kernel mode.
    All tests will be executed in two modes automatically, override
    this fixture in test file if you want to run only one mode.
    """
    return request.param


@pytest.fixture
def preheat_config(preheat_mode):
    return f'--preheat_kernel={preheat_mode}'


@pytest.fixture
def voila_app(voila_args, voila_config, preheat_config):
    voila_app = VoilaTest.instance()
    voila_app.initialize(voila_args + ['--no-browser', preheat_config])
    voila_config(voila_app)
    voila_app.start()
    yield voila_app
    voila_app.stop()
    voila_app.clear_instance()


@pytest.fixture
def app(voila_app):
    return voila_app.app


@pytest.fixture
def wait_for_kernel(preheat_mode):
    """Wait for kernel be heated in case of `preheat_mode = True`"""
    async def inner(time=3):
        if preheat_mode:
            await asyncio.sleep(time)
    return inner
