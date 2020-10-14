from datetime import datetime

def date_to_timestamp(date):
    timestamp = datetime.combine(date, datetime.min.time()).timestamp() * 1000
    return timestamp