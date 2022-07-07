from datetime import timedelta
from dateutil.relativedelta import relativedelta

FREQUENCY_TO_DAYS = {
    "daily": timedelta(days=1),
    "weekly": timedelta(days=7),
    "biweekly": timedelta(days=14),
    "monthly": relativedelta(months=1)
    }
