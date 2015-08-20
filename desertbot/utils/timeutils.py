from datetime import datetime, timedelta


def now():
    return datetime.utcnow().replace(microsecond=0)

def timestamp(time):
    unixEpoch = datetime.utcfromtimestamp(0)
    return int((time - unixEpoch).total_seconds())

def timeDeltaString(date1, date2):
    delta = date1 - date2
    dayString = "{} day{}".format(delta.days, "" if delta.days == 1 else "s")
    hours = delta.seconds // 3600
    hourString = "{} hour{}".format(hours, "" if hours == 1 else "s")
    minutes = (delta.seconds // 60) % 60
    minuteString = "{} minute{}".format(minutes, "" if minutes == 1 else "s")
    if delta.days == 0 and hours == 0 and minutes == 0:
        return "less than a minute"
    return "{}, {} and {}".format(dayString, hourString, minuteString)

def durationToTimedelta(durStr):
    try: # If it's just a number, assume it's seconds.
        return timedelta(0, int(durStr))
    except ValueError:
        pass

    units = {
        "y": 31557600,
        "w": 604800,
		"d": 86400,
		"h": 3600,
		"m": 60
	}
    seconds = 0
    count = []
    for char in durStr:
        if char.isdigit():
            count.append(char)
        else:
            if not count:
                continue
            newSeconds = int("".join(count))
            if char in units:
                newSeconds *= units[char]
            seconds += newSeconds
            count = []
    return timedelta(0, seconds)

def strftimeWithTimezone(date):
    return date.strftime("%Y-%m-%d %H:%M UTC")
