import pytest
import responses

from recommendation.utils import configuration
from recommendation.utils import logger
import recommendation


@pytest.fixture(scope='function', autouse=True)
def change_config_and_setup_responses(request):
    """
    This changes the config file that is loaded to test_recommendation.ini
     as well as (in a hack-y way) activating `responses` without having
     to apply a decorator to every test function
    """
    configuration._config = configuration.get_configuration('', recommendation.__name__,
                                                            'api/test/test_recommendation.ini')
    logger.initialize_logging()
    responses._default_mock.__enter__()

    def fin():
        responses._default_mock.__exit__()

    request.addfinalizer(fin)
