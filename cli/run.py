import boto3
import pprint
import json
import argparse
import re
import datetime
import os
from cronexpression import get_expression

RULE_NAME_PREFIX = 'OPTLY_FLAG'

class Scheduler():
  """
  https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/events.html#CloudWatchEvents.Client.put_events
  """

  def __init__(self):
    self.session = boto3.Session(profile_name=os.environ.get('OPTLY_LAMBDA_AWS_PROFILE'))
    self.client  = self.session.client('events')

  def invoke_lambda_directly(self, feature_id, environment, feature_setstate):
    lambda_client = self.session.client('lambda')    
    response = lambda_client.invoke(
      FunctionName=os.environ.get('OPTLY_LAMBDA_FNC_ARN'), # can be ARN
      InvocationType='Event',
      Payload=json.dumps({
        'feature_id': feature_id,
        'environment': environment,
        'state': feature_setstate,
      })
    )
    return response

  def configure_rule(self, environment, feature_id, feature_setstate, schedule_date):
    cron_schedule_datetime = get_expression(schedule_date)
    cron_expression        = cron_schedule_datetime.get('cron')
    cron_readable          = cron_schedule_datetime.get('human')
    rule_name              = '{}_{}_{}_{}'.format(RULE_NAME_PREFIX, feature_id, feature_setstate, environment)
    
    """
    Create an event that runs on a cron schedule
    """
    response = self.client.put_rule(
      Name=rule_name,
      ScheduleExpression='cron({})'.format(cron_expression),
      State='ENABLED',
      Description='[{}] Optimizely Feature Flag: "{}" @ {} [{}]'.format(
        'ENABLE' if feature_setstate == 'on' else 'DISABLE', 
        feature_id, 
        cron_readable,
        environment,
      ),
    )

    return rule_name

  def configure_target(self, rule_name, environment, feature_id, feature_setstate):
    """
    Add a target to our Rule
    """
    response = self.client.put_targets(
      Rule=rule_name,
      Targets=[
        {
          'Id': os.environ.get('OPTLY_LAMBDA_FNC_ID'),
          'Arn': os.environ.get('OPTLY_LAMBDA_FNC_ARN'),
          'Input': json.dumps({
            'feature_id': feature_id,
            'environment': environment,
            'state': feature_setstate,
          }),
        }
      ])

  def list_jobs(self):
    response = self.parse_all_jobs()
    schedule_data = []
    for rule in response.get('Rules', []):
      rule_data = {}
      description = rule.get('Description')
      """
      This will all break if we change the way that `description` in the `configure_rule` method.
      May want to rethin how this metadata is store. Didn't want to have to fetch all rules then targets
      in order to print this list      
      """
      rule_data['name']    = rule.get('Name')
      rule_data['state']   = re.search(r'^\[(\w+)\]', description).group(1)
      rule_data['feature'] = re.search(r'Feature Flag: "(\d+)"', description).group(1)
      rule_data['date']    = re.search(r'@ (.*) \[', description).group(1)
      rule_data['env']     = re.search(r'\[(\w+)\]$', description).group(1)
      rule_data['dt']      = datetime.datetime.strptime(rule_data.get('date'), "%B %d, %Y, %H:%M:%S UTC")
      schedule_data.append(rule_data)
    schedule_data.sort(key=lambda item:item['dt'], reverse=False)
    print('Scheduled Jobs:\n================')
    print('Feature ID\tToggle State\tDate\t\t\t\tEnv\t\tJob Name')
    for job in schedule_data:
      print('{}\t{}\t\t{}\t{}\t{}'.format(
        job.get('feature'), 
        job.get('state'), 
        job.get('dt').strftime("%m-%d-%Y %H:%M:%S(UTC)"),
        job.get('env'),
        job.get('name'),
      ))      

  def delete_job(self, name):
    """
    Delete targets before deleting rule
    """
    response = self.client.list_targets_by_rule(Rule=name)    
    target_ids = []
    for target in response.get('Targets', []):
      target_ids.append(target.get('Id'))
    delete_targets = self.client.remove_targets(
      Rule=name,
      Ids=target_ids,
      Force=True
    )
    delete_rule = self.client.delete_rule(Name=name,Force=True)
    return delete_rule

  def schedule_feature_toggle(self, feature_id, environment, feature_setstate, schedule_date):
    rule_name = self.configure_rule(environment, feature_id, feature_setstate, schedule_date)
    self.configure_target(rule_name, environment, feature_id, feature_setstate)

  def parse_all_jobs(self):
    response = self.client.list_rules(NamePrefix=RULE_NAME_PREFIX)
    return response

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Schedule a feature flag.')
  parser.add_argument('action')
  parser.add_argument('-feature', help='Feature ID', action="store", dest="feature")
  parser.add_argument('-toggle',  help='Set Feature State', action="store", dest="toggle", choices=['on', 'off'])
  parser.add_argument('-env',  help='Environment to toggle feature', action="store", dest="env")
  parser.add_argument('-job',  help='Specific Job Name when deleting', action="store", dest="job_name")  
  parser.add_argument('-date',  help='Schedule date', action="store", dest="date")  
  args = parser.parse_args()

  if args.action in ['schedule', 'flag']:
    if not args.feature:
      print('-feature [ID] required when action is "enable", "disable" or "flag"')
      exit()
    if not args.toggle:
      print('-toggle ["on", "off"] required when action is "enable", "disable" or "flag"')
      exit()
    if not args.env:
      print('-env [ENV NAME] required when action is "enable", "disable" or "flag"')    
      exit()      
    if args.action == 'schedule' and not args.date:
      print('-date required with format "%m-%d-%Y %H:%M:%S", e.g.: "3-23-2019 17:45:38"')
      exit()
  if args.action == 'delete' and not args.job_name:
    print('-job required when action is delete')
    exit()  
  if args.action == 'list':
    scheduler = Scheduler()
    scheduler.list_jobs()
  elif args.action == 'schedule':
    scheduler = Scheduler()
    scheduler.schedule_feature_toggle(args.feature, args.env, args.toggle, args.date)
  elif args.action == 'delete':
    scheduler = Scheduler()
    scheduler.delete_job(args.job_name) 
  elif args.action == 'flag':
    scheduler = Scheduler()
    scheduler.invoke_lambda_directly(args.feature, args.env, args.toggle)
  else:
    parser.print_help()
