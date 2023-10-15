import datetime

datetime_to_date = lambda x: datetime.datetime.strptime(x, "%Y-%m-%dT%H:%M:%SZ").date() if x else None