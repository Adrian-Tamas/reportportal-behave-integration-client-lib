# Description

This library is Report Portal connector that allows you to integrate Report Portal with your Python Behave BDD testing framework

Your automation framework will run just as it does now unless you choose to run with Report Portal Integration

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
    rp_enable = context.config.userdata.getbool('rp_enable', False)
    step_based = context.config.userdata.getbool('step_based', False)
    add_screenshot = context.config.userdata.getbool('add_screenshot', False)
    launch_name = f"Execution using tags: {context.config.tags.ands[0]}"
    launch_description = f"BDD Tests for: {', '.join(tag for tag in context.config.tags.ands[0])}"
    context.behave_integration_service = BehaveIntegrationService(rp_endpoint=rp_endpoint,
                                                                  rp_project=rp_project,
                                                                  rp_token=rp_token,
                                                                  rp_launch_name=launch_name,
                                                                  rp_launch_description=launch_description,
                                                                  rp_enable=rp_enable,
                                                                  step_based=step_based,
                                                                  add_screenshot=add_screenshot)
    context.behave_integration_service.launch_service(context.config.tags.ands[0])


def before_feature(context, feature):
    context.behave_integration_service.before_feature(feature)


def before_scenario(context, scenario):
    context.behave_integration_service.before_feature(scenario)


def before_step(context, step):
    context.behave_integration_service.before_step(step)


def after_step(context, step):
    context.behave_integration_service.after_step(step)


def after_scenario(context, scenario):
    context.behave_integration_service.after_scenario(scenario)


def after_feature(context, feature):
    context.behave_integration_service.after_feature(feature)


def after_all(context):
    context.behave_integration_service.after_all()
```
