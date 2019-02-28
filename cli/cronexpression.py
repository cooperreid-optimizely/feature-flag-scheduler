import datetime
"""
Create a cron expression to schedule things in CloudWatch

https://docs.aws.amazon.com/AmazonCloudWatch/latest/events/ScheduledEvents.html#CronExpressions

Field         Values           Wildcards 
Minutes       0-59             , - * /  
Hours         0-23             , - * /  
Day-of-month  1-31             , - * ? / L W  
Month         1-12 or JAN-DEC  , - * /  
Day-of-week   1-7 or SUN-SAT   , - * ? L #  
Year          1970-2199        , - * /
"""

def get_expression(date_str_utc=0):
  date_str_format = "%m-%d-%Y %H:%M:%S"
  try:
    schedule_for = datetime.datetime.strptime(date_str_utc, date_str_format)
  except:
    raise('Unable to parse date, please use format: {}'.format(date_str_format))
  # utc_datetime = datetime.datetime.utcnow()
  # schedule_for = utc_datetime + datetime.timedelta(minutes=minute_from_now)
  return {
      'cron': '{} {} {} {} ? {}'.format(
        schedule_for.minute, 
        schedule_for.hour, 
        schedule_for.day,
        schedule_for.month,
        schedule_for.year),
      'human': schedule_for.strftime("%B %d, %Y, %H:%M:%S%z UTC")
  }

if __name__ == '__main__':
  expression = get_expression()
  print('Cron expression: {}'.format(expression))