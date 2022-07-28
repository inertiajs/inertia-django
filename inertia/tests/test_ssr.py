from inertia.test import InertiaTestCase, inertia_page, inertia_div
from django.test import override_settings
from unittest.mock import patch, Mock
from requests.exceptions import RequestException

@override_settings(
  INERTIA_SSR_ENABLED=True,
  INERTIA_SSR_URL='ssr-url',
  INERTIA_VERSION='1.0',
)
class SSRTestCase(InertiaTestCase):

  @patch('inertia.http.requests')
  def test_it_returns_ssr_calls(self, mock_request):
    mock_response = Mock()
    mock_response.json.return_value = {
      'body': '<div>Body Works</div>',
      'head': '<title>Head works</title>',
    }

    mock_request.post.return_value = mock_response
    
    response = self.client.get('/props/')
    
    mock_request.post.assert_called_once_with(
      'ssr-url/render',
      json=inertia_page('props', props={'name': 'Brandon', 'sport': 'Hockey'}),
    )
    self.assertTemplateUsed('inertia_ssr.html')
    print(response.content)
    self.assertContains(response, '<div>Body Works</div>')
    self.assertContains(response, 'head--<title>Head works</title>--head')


  @patch('inertia.http.requests')
  def test_it_uses_inertia_if_inertia_requests_are_made(self, mock_requests):
    response = self.inertia.get('/props/')

    mock_requests.post.assert_not_called()
    self.assertJSONResponse(response, inertia_page('props', props={'name': 'Brandon', 'sport': 'Hockey'}))

  @patch('inertia.http.requests')
  def test_it_fallsback_on_failure(self, mock_requests):
    def uh_oh(*args, **kwargs):
      raise RequestException()

    mock_response = Mock()
    mock_response.raise_for_status.side_effect = uh_oh
    mock_requests.post.return_value = mock_response

    response = self.client.get('/props/')
    self.assertContains(response, inertia_div('props', props={'name': 'Brandon', 'sport': 'Hockey'}))
