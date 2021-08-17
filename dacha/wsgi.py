import os
from whitenoise import WhiteNoise
from django.conf import settings


from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dacha.settings')

application = get_wsgi_application()
application = WhiteNoise(application, root=settings.STATIC_ROOT)
application.add_files(settings.STATIC_ROOT, prefix="more-files/")
