from django_1_4.settings import *
import warnings

USE_TZ = True

warnings.filterwarnings(
        'error', r"DateTimeField received a naive datetime",
        RuntimeWarning, r'django\.db\.models\.fields')
