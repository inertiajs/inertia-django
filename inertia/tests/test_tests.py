from inertia.test import InertiaTestCase

class TestTestCase(InertiaTestCase):

  def test_include_props(self):
    response = self.client.get('/props/')

    self.assertIncludesProps({'name': 'Brandon'})

  def test_has_exact_props(self):
    response = self.client.get('/props/')

    self.assertHasExactProps({'name': 'Brandon', 'sport': 'Hockey'})

  def test_has_template_data(self):
    response = self.client.get('/template_data/')

    self.assertIncludesTemplateData({'name': 'Brian'})

  def test_has_exact_template_data(self):
    response = self.client.get('/template_data/')

    self.assertHasExactTemplateData({'name': 'Brian', 'sport': 'Basketball'})

  def test_component_name(self):
    response = self.client.get('/props/')

    self.assertComponentUsed('TestComponent')

