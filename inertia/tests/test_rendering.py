from inertia.test import InertiaTestCase, inertia_div, inertia_page

class FirstLoadTestCase(InertiaTestCase):
  def test_with_props(self):
    self.assertContains(
      self.client.get('/props/'),
      inertia_div('props', props={
        'name': 'Brandon',
        'sport': 'Hockey',
      })
    )

  def test_with_template_data(self):
    self.assertContains(
      self.client.get('/template_data/'),
      inertia_div('template_data', template_data={
        'name': 'Brian',
        'sport': 'Basketball',
      })
    )

  def test_with_no_data(self):
    self.assertContains(
      self.client.get('/empty/'),
      inertia_div('empty')
    )

  def test_proper_status_code(self):
    self.assertEqual(
      self.client.get('/empty/').status_code,
      200
    )

  def test_template_rendered(self):
    self.assertTemplateUsed(self.client.get('/empty/'), 'inertia.html')


class SubsequentLoadTestCase(InertiaTestCase):
  def test_with_props(self):
    self.assertJSONResponse(
      self.inertia.get('/props/'),
      inertia_page('props', props={
        'name': 'Brandon',
        'sport': 'Hockey',
      })
    )

  def test_with_template_data(self):
    self.assertJSONResponse(
      self.inertia.get('/template_data/'),
      inertia_page('template_data', template_data={
        'name': 'Brian',
        'sport': 'Basketball',
      })
    )

  def test_with_no_data(self):
    self.assertJSONResponse(
      self.inertia.get('/empty/'),
      inertia_page('empty')
    )

  def test_proper_status_code(self):
    self.assertEqual(
      self.inertia.get('/empty/').status_code,
      200
    )

  def test_redirects_from_inertia_views(self):
    self.assertEqual(
      self.inertia.get('/inertia-redirect/').status_code,
      302
    )

class LazyPropsTestCase(InertiaTestCase):
  def test_lazy_props_are_not_included(self):
    self.assertJSONResponse(
      self.inertia.get('/lazy/'),
      inertia_page('lazy', props={'name': 'Brian'})
    )

  def test_lazy_props_are_included_when_requested(self):
    self.assertJSONResponse(
      self.inertia.get('/lazy/', HTTP_X_INERTIA_PARTIAL_DATA='sport,grit', HTTP_X_INERTIA_PARTIAL_COMPONENT='TestComponent'),
      inertia_page('lazy', props={'sport': 'Basketball', 'grit': 'intense'})
    )

class ComplexPropsTestCase(InertiaTestCase):
  def test_nested_callable_props_work(self):
    self.assertJSONResponse(
      self.inertia.get('/complex-props/'),
      inertia_page('complex-props', props={'person': {'name': 'Brandon'}})
    )

class ShareTestCase(InertiaTestCase):
  def test_that_shared_props_are_merged(self):
    self.assertJSONResponse(
      self.inertia.get('/share/'),
      inertia_page('share', props={'name': 'Brandon', 'position': 'goalie', 'number': 29})
    )

class CSRFTestCase(InertiaTestCase):
  def test_that_csrf_inclusion_is_automatic(self):
    response = self.inertia.get('/props/')

    self.assertIsNotNone(response.cookies.get('csrftoken'))

  def test_that_csrf_is_included_even_on_initial_page_load(self):
    response = self.client.get('/props/')

    self.assertIsNotNone(response.cookies.get('csrftoken'))
