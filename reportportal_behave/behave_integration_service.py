from mss import mss

from reportportal.reportportal_service import *


class BehaveIntegrationService:

    def __init__(self,
                 rp_endpoint,
                 rp_project,
                 rp_token,
                 rp_launch_name,
                 rp_launch_description,
                 rp_enable=True,
                 step_based=False,
                 add_screenshot=False):
        self.rp_endpoint = rp_endpoint
        self.rp_project = rp_project
        self.rp_token = rp_token
        self.rp_launch_name = rp_launch_name
        self.rp_launch_description = rp_launch_description
        self.rp_enable = rp_enable
        self.step_based = step_based
        self.add_screenshot = add_screenshot
        self.service = ReportPortalService(rp_endpoint=rp_endpoint,
                                           rp_project=rp_project,
                                           rp_token=rp_token,
                                           rp_launch_name=rp_launch_name,
                                           rp_launch_description=rp_launch_description)

    def launch_service(self, tags):
        #   Starts Launcher
        if self.rp_enable:
            self.service.start_launcher(name=self.rp_launch_name,
                                        start_time=timestamp(),
                                        tags=tags,
                                        description=self.rp_launch_description)

    def before_feature(self, feature):
        #   Starts Feature
        if self.rp_enable:
            self.service.start_feature_test(name='Feature: %s' % feature.name,
                                            description='Feature description:\n%s' % '\n'.join(feature.description),
                                            tags=feature.tags,
                                            start_time=timestamp(),
                                            item_type='SUITE')

    def before_scenario(self, scenario):
        #   Starts scenario test item.
        if self.rp_enable:
            self.service.start_scenario_test(name='Scenario: %s' % scenario.name,
                                             description=scenario.name,
                                             tags=scenario.tags,
                                             start_time=timestamp(),
                                             item_type='SCENARIO')

    # This method executed in case when step_based ir True
    def before_step(self, step):
        if self.rp_enable and self.step_based:
            description = None
            if step.table:
                table_data = []
                for row in step.table.rows:
                    table_data.append('|'.join(row))
                description = "|%s|" % '|\n|'.join(table_data)
            elif step.text:
                # Logs step with text if it was provided
                description = step.text

            self.service.start_step_test(name='%s %s' % (step.keyword, step.name),
                                         start_time=timestamp(),
                                         item_type='STEP',
                                         description=description)

    def log_step_error_result(self, step_name, error_msg=None):
        if self.add_screenshot:
            with mss() as sct:
                screenshot_name = sct.shot()

            # Logs assertion message with attachment and ERROR level it step was failed.
            self.service.log_step_result(end_time=timestamp(),
                                         message=error_msg,
                                         level='ERROR',
                                         attachment={
                                             'name': step_name,
                                             'data': open(screenshot_name, 'rb'),
                                             'mime': 'application/octet-stream'
                                         }
                                         )
        else:
            self.service.log_step_result(end_time=timestamp(),
                                         message=error_msg,
                                         level='ERROR')

    def after_step(self, step):
        # If step_based parameter is True then STEP based logging will be used
        if self.rp_enable and self.step_based:
            # Finishes step
            if step.status == 'failed':
                # Takes a demo screenshot of desktop (can be removed)

                self.log_step_error_result(error_msg=f"{step.exception}", step_name=step.name)
                self.service.finish_step_test(end_time=timestamp(), status='FAILED')
            else:
                self.service.finish_step_test(end_time=timestamp(), status='PASSED')

        # Else SCENARIO based logging will be used
        elif self.rp_enable:
            # Creates text log message with INFO level.
            if step.table:
                # Logs step with data table if it was provided
                table_data = []
                for row in step.table.rows:
                    table_data.append('|'.join(row))
                table_result = "|%s|" % '|\n|'.join(table_data)
                self.service.log_step_result(end_time=timestamp(),
                                             message='%s %s\n~~~~~~~~~~~~~~~~~~~~~~~~~\nStep data table:\n%s' % (
                                                 step.keyword,
                                                 step.name,
                                                 table_result),
                                             level='INFO')
            elif step.text:
                # Logs step with text if it was provided
                self.service.log_step_result(end_time=timestamp(),
                                             message='%s %s\n~~~~~~~~~~~~~~~~~~~~~~~~~\nStep data text:\n%s' % (
                                                 step.keyword,
                                                 step.name,
                                                 step.text),
                                             level='INFO')
            else:
                # Logs step name if it is passed
                self.service.log_step_result(end_time=timestamp(), message='%s %s' % (step.keyword, step.name),
                                             level='INFO')

            if step.status == 'failed':
                # Logs assertion message with attachment and ERROR level it step was failed.
                self.log_step_error_result(error_msg=f"{step.exception}", step_name=step.name)

    def after_scenario(self, scenario):
        if self.rp_enable:
            for step in scenario.steps:
                if step.status.name == 'undefined':
                    # Logs scenario if it is undefined
                    self.service.log_step_result(end_time=timestamp(),
                                                 message='%s %s - step is undefined.\nPlease define step.' % (
                                                     step.keyword, step.name),
                                                 level='WARN')
                    # Logs scenario as skipped if it is marked for skip
                    # For example scenario marked by @skip tag and --tags=~@skip specified in params of run
                elif step.status.name == 'skipped':
                    self.service.log_step_result(end_time=timestamp(),
                                                 message='%s %s - %s' % (
                                                     step.keyword, step.name, step.status.name.capitalize()),
                                                 level='TRACE')
            #   Finishes scenario
            if scenario.status == 'failed':
                self.service.finish_scenario_test(end_time=timestamp(), status='FAILED')
            else:
                self.service.finish_scenario_test(end_time=timestamp(), status='PASSED')

    def after_feature(self, feature):
        if self.rp_enable:
            for i in feature.scenarios:
                try:
                    if i.tags[0] == 'skip':
                        self.service.start_scenario_test(name='Scenario: %s' % i.name,
                                                         description=i.description[0],
                                                         tags=feature.tags,
                                                         start_time=timestamp(),
                                                         item_type='SCENARIO')
                        self.service.finish_scenario_test(end_time=timestamp(), status='SKIPPED')
                except IndexError:
                    pass
            #   Finishes feature
            if feature.status == 'failed':
                self.service.finish_feature(end_time=timestamp(), status='FAILED')
            else:
                self.service.finish_feature(end_time=timestamp(), status='PASSED')

    def after_all(self):
        #   Finishes the launcher and terminates the service.
        if self.rp_enable:
            self.service.finish_launcher(end_time=timestamp())
            self.service.terminate_service()
