# Feature Flag Scheduler CLI
Schedule feature flag toggling using AWS Lambda &amp; CloudWatch

---

## Functions

#### Schedule for Feature Flag to be enabled on March 1, 2019 @ 5:45pm UTC
```bash
$ python run.py schedule -feature 8930855000 -toggle on -date "3-1-2019 17:45:00"
```

#### Schedule for Feature Flag to be disabled on March 20, 2019 @ 5:45pm UTC
```bash
$ python run.py schedule -feature 8930855000 -toggle off -date "3-20-2019 17:45:00"
```

#### List all scheduled feature toggle jobs
```bash
$ python run.py list
```
will print out scheduled jobs and their 'job name'

```bash
Scheduled Jobs:
================
Feature ID	Toggle State	Date				Job Name
8930855048	ENABLE		03-01-2019 17:45:00(UTC)	OPTLY_FLAG_8930855000_on
8930855048	DISABLE		03-20-2019 17:45:00(UTC)	OPTLY_FLAG_8930855000_off
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
* The AWS connectivity is handled by named profiles
* The named profile used by the CLI must be set as an environment variable `OPTLY_LAMBDA_AWS_PROFILE`
* The Lambda function ARN must be set as an environment variable `OPTLY_LAMBDA_FNC_ARN`
* The Lambda function ID must be set as an environment variable `OPTLY_LAMBDA_FNC_ID`

#### Setting up AWS Lambda function
The files contents of `lambda_function/lambda_function.py` can be placed directly within a Lambda function

#### Setting up CloudWatch Events
Nothing needs to be done on the CloudWatch dashboard, but it helps troubleshoot by being able to refresh your list of scheduled jobs via the interface

---

## Features To come:
* Support for environments (right now, hardcoded to 'production')
* Support for specifying rollout %
