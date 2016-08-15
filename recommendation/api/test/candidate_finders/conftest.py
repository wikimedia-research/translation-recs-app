import pytest

from recommendation.api import candidate_finders


@pytest.fixture(params=[
    candidate_finders.CandidateFinder,
    candidate_finders.PageviewCandidateFinder,
    candidate_finders.MorelikeCandidateFinder
])
def finder(request):
    return request.param()
