import pytest
import responses

import recommendation


@pytest.fixture(scope='function', autouse=True)
def change_config_and_setup_responses(request):
    """
    This changes the config file that is loaded to test_recommendation.ini
     as well as (in a hack-y way) activating `responses` without having
     to apply a decorator to every test function
    """
    _config_name = recommendation.config_name
    recommendation.config_name = 'api/test/test_recommendation.ini'
    responses._default_mock.__enter__()

    def fin():
        recommendation.config_name = _config_name
        responses._default_mock.__exit__()

    request.addfinalizer(fin)
