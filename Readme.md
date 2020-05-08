# Description

This library is Report Portal connector that allows you to integrate Report Portal with your Python Behave BDD testing framework

Your automation framework will run just as it does now unless you choose to run with Report Portal Integration

The library was updated to work with Report Portal API v5+ and the reportportal-client lib v5

# Installation

## Manual
1. Clone the repository
2. Enter the folder and run `pip install .`

## Using pip and pypi.org
```bash
pip install reportportal-behave-client
```
**NOTE: Use version >= 1.0.3 for ReportPortal v5**

# Sending reports to Report Portal

In order to enable the Report Portal Integration add the  `-D rp_enable=True`:
```bash
behave -D rp_enable=True
```

For step based reporting you need to also add the step based flag `-D step_based=True`:
```bash
behave -D rp_enable=True -D step_based=True
```

# Integrating the lib in your framework

In your environments.py file add the service in each method. For e.g.:

```python

def before_all(context):
    tags = ', '.join([tag for tags in context.config.tags.ands for tag in tags])
    rp_enable = context.config.userdata.getbool('rp_enable', False)
    step_based = context.config.userdata.getbool('step_based', True)
    context.requested_browser = context.config.userdata.get('browser', "chrome")
    rp_token = os.environ.get("RP_TOKEN")
    add_screenshot = context.config.userdata.getbool('add_screenshot', False)
    launch_name = f"Execution using tags: {tags}"
    launch_description = f"BDD Tests for: {tags}"
    context.behave_integration_service = BehaveIntegrationService(rp_endpoint=rp_endpoint,
                                                                  rp_project=rp_project,
                                                                  rp_token=rp_token,
                                                                  rp_launch_name=launch_name,
                                                                  rp_launch_description=launch_description,
                                                                  rp_enable=rp_enable,
                                                                  step_based=step_based,
                                                                  add_screenshot=add_screenshot,
                                                                  verify_ssl=False)
    context.launch_id = context.behave_integration_service.launch_service(tags=tags)


def before_feature(context, feature):
    context.feature_id = context.behave_integration_service.before_feature(feature)


def before_scenario(context, scenario):
    context.scenario_id = context.behave_integration_service.before_scenario(scenario,
                                                                             feature_id=context.feature_id)


def before_step(context, step):
    context.step_id = context.behave_integration_service.before_step(step, scenario_id=context.scenario_id)


def after_step(context, step):
    context.behave_integration_service.after_step(step, context.step_id)


def after_scenario(context, scenario):
    context.behave_integration_service.after_scenario(scenario, context.scenario_id)


def after_feature(context, feature):
    context.behave_integration_service.after_feature(feature, context.feature_id)


def after_all(context):
    context.behave_integration_service.after_all(context.launch_id)

```
