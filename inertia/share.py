__all__ = ['share']

class InertiaShare:
  def __init__(self):
    self.props = {}

  def set(self, **kwargs):
    self.props = {
      **self.props,
      **kwargs,
    }

  def all(self):
    return self.props


def share(request, **kwargs):
  if not hasattr(request, 'inertia'):
    request.inertia = InertiaShare()

  request.inertia.set(**kwargs)
