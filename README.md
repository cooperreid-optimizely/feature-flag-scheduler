# Feature Flag Scheduler CLI for Optimizely
Schedule feature flag toggling using AWS Lambda &amp; CloudWatch. 

Overview: Run CLI command to create a CloudWatch cron-scheduled Event with a payload containing feature ID, toggle state (on/off), and environment name. When the scheduled Event is triggered, it will invoke a Lambda function and pass along the payload which will be used to toggle feature state via the Optimizely REST API.

![Solution Diagram](https://raw.githubusercontent.com/cooperreid-optimizely/feature-flag-scheduler/master/static/diagram.png)

---

## Functions

#### Schedule for Feature Flag to be enabled on March 1, 2019 @ 5:45pm UTC
```bash
$ python run.py schedule -feature 8930855000 -toggle on -date "3-1-2019 17:45:00" -env production
```

#### Schedule for Feature Flag to be disabled on March 20, 2019 @ 5:45pm UTC
```bash
$ python run.py schedule -feature 8930855000 -toggle off -date "3-20-2019 17:45:00" -env production
```

#### List all scheduled feature toggle jobs
```bash
$ python run.py list
```
will print out scheduled jobs and their 'job name'

```bash
Scheduled Jobs:
================
Feature ID	Toggle State	Date				Env		Job Name
8930855000	DISABLE		03-20-2019 17:45:00(UTC)	production	OPTLY_FLAG_8930855000_off_production
8930855000	ENABLE		03-1-2019  17:45:00(UTC)	production	OPTLY_FLAG_8930855000_on_production

```

#### Remove a scheduled job
```bash
$ python run.py delete -job OPTLY_FLAG_8930855000_on
```

---

## Configuration

Environments:
`>= Python 3.6`

#### Setting up the local CLI
* The AWS connectivity is handled by [named profiles](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-profiles.html)
* The named profile used by the CLI must be set as an environment variable `OPTLY_LAMBDA_AWS_PROFILE`
* The Lambda function ARN must be set as an environment variable `OPTLY_LAMBDA_FNC_ARN`
* The Lambda function ID must be set as an environment variable `OPTLY_LAMBDA_FNC_ID`

#### Setting up AWS Lambda function
The files contents of `lambda_function/lambda_function.py` can be placed directly within a Lambda function
* The Optimizely ["personal token"](https://developers.optimizely.com/x/rest/getting-started/) must be set as the `v2_token` environment variable in the Lambda function configuration screen within AWS

#### Setting up CloudWatch Events
Nothing needs to be done on the CloudWatch dashboard, but it helps troubleshoot by being able to refresh your list of scheduled jobs via the interface

---

## Features To come:
* Support for specifying rollout %
* Support for relative timezones (requires UTC time currently)
