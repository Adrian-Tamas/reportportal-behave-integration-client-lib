import traceback

from mss import mss

from reportportal_behave.entities.feature import Feature
from reportportal_behave.entities.scenario import Scenario
from reportportal_behave.entities.step import Step
from reportportal_behave.reportportal_service import *


class BehaveIntegrationService:

    def __init__(self,
                 rp_endpoint,
                 rp_project,
                 rp_token,
                 rp_launch_name,
                 rp_launch_description,
                 rp_enable=True,
                 step_based=False,
                 add_screenshot=False,
                 verify_ssl=False):
        self.rp_endpoint = rp_endpoint
        self.rp_project = rp_project
        self.rp_token = rp_token
        self.rp_launch_name = rp_launch_name
        self.rp_launch_description = rp_launch_description
        self.rp_enable = rp_enable
        self.step_based = step_based
        self.add_screenshot = add_screenshot
        self.service = IntegrationService(rp_endpoint=rp_endpoint,
                                          rp_project=rp_project,
                                          rp_token=rp_token,
                                          rp_launch_name=rp_launch_name,
                                          rp_launch_description=rp_launch_description,
                                          verify_ssl=verify_ssl)

    def log_step_error_result(self, step_name, item_id, error_msg=None):
        """
        Log errors in steps if it happens
        :param step_name: the name of the step
        :param item_id: the id of the step execution
        :param error_msg: the error message
        :return: None
        """
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
                                         },
                                         item_id=item_id
                                         )
        else:
            self.service.log_step_result(end_time=timestamp(),
                                         message=error_msg,
                                         level='ERROR',
                                         item_id=item_id)

    def launch_service(self, attributes=None, tags=None):
        """
        Start the service that will communicate results to ReportPortal
        :param attributes: the attributes to label the launch with
        :param tags: the tags the test execution was triggered with
        :return: the id of the launch required to mark it complete
        """
        if self.rp_enable:
            return self.service.start_launcher(name=self.rp_launch_name,
                                               start_time=timestamp(),
                                               description=self.rp_launch_description,
                                               attributes=attributes,
                                               tags=tags)

    def before_feature(self, feature, attributes=None):
        """
        Log the start of a feature execution
        :param feature: the feature passed from behave
        :param attributes: the attributes to label the feature with
        :return: the id of the feature execution required to mark it complete
        """
        if self.rp_enable:
            feature_info = Feature(feature)
            return self.service.start_feature_test(name=feature_info.name,
                                                   description=feature_info.description,
                                                   attributes=attributes,
                                                   tags=feature_info.tags,
                                                   start_time=timestamp(),
                                                   item_type=feature_info.item_type,
                                                   parent_item_id=None)

    def before_scenario(self, scenario, feature_id, attributes=None):
        """
        Log the start of a scenario execution
        :param scenario: the behave scenario
        :param feature_id: the id of the feature execution
        :param attributes: the attributes to label the scenario with
        :return: the id of te scenario execution required to mark it complete
        """
        if self.rp_enable:
            scenario_info = Scenario(scenario, feature_id=feature_id)
            return self.service.start_scenario_test(name=scenario_info.name,
                                                    description=scenario_info.description,
                                                    attributes=attributes,
                                                    tags=scenario_info.tags,
                                                    start_time=timestamp(),
                                                    item_type=scenario_info.item_type,
                                                    parent_item_id=scenario_info.feature_id)

    def before_step(self, step, scenario_id, attributes=None):
        """
        Logs the start of a step execution.
        This method is ran only if step_based logging is enabled
        :param step: the behave step
        :param scenario_id: the id of the scenario execution the step belongs to
        :param attributes: the attributes to label the step with
        :return: the id of the step execution required to mark it complete
        """
        if self.rp_enable and self.step_based:
            step_info = Step(step, scenario_id=scenario_id)

            return self.service.start_step_test(name=f"{step_info.keyword} {step_info.name}",
                                                start_time=timestamp(),
                                                item_type=step_info.item_type,
                                                description=step_info.description,
                                                attributes=attributes,
                                                parent_item_id=step_info.scenario_id)

    def after_step(self, step, step_id):
        """
        Mark the step as complete and set the status for it
        :param step: the behave step
        :param step_id: the id of the step execution received from the before_step
        :return: response of the step completion if available
        """
        step_info = Step(step, step_id=step_id)
        if self.rp_enable and self.step_based:
            # Finishes step
            if step.status == 'failed':
                # Takes a demo screenshot of desktop (can be removed)

                self.log_step_error_result(error_msg=f"{step.exception}",
                                           step_name=step_info.name,
                                           item_id=step_info.step_id)
                self.log_step_error_result(error_msg=u"".join(traceback.format_tb(step.exc_traceback)),
                                           step_name=step_info.name,
                                           item_id=step_info.step_id)
                return self.service.finish_step_test(end_time=timestamp(),
                                                     status='FAILED',
                                                     item_id=step_info.step_id)
            else:
                return self.service.finish_step_test(end_time=timestamp(),
                                                     status='PASSED',
                                                     item_id=step_info.step_id)

        # Else SCENARIO based logging will be used
        elif self.rp_enable:
            # Creates text log message with INFO level.
            if step.table:
                message = '%s %s\n~~~~~~~~~~~~~~~~~~~~~~~~~\nStep data table:\n%s' % (
                    step_info.keyword,
                    step_info.name,
                    step_info.description)
            elif step.text:
                message = '%s %s\n~~~~~~~~~~~~~~~~~~~~~~~~~\nStep data text:\n%s' % (
                    step_info.keyword,
                    step_info.name,
                    step_info.description)
            else:
                message = step_info.description
            self.service.log_step_result(end_time=timestamp(),
                                         message=message,
                                         level='INFO',
                                         item_id=step_info.step_id)

            if step.status == 'failed':
                # Logs assertion message with attachment and ERROR level it step was failed.
                self.log_step_error_result(error_msg=f"{step.exception}",
                                           step_name=step_info.name,
                                           item_id=step_info.step_id)
                self.log_step_error_result(error_msg=u"".join(traceback.format_tb(step.exc_traceback)),
                                           step_name=step_info.name,
                                           item_id=step_info.step_id)

    def after_scenario(self, scenario, scenario_id):
        """
        Mark scenario as complete and set the status accordingly
        :param scenario: the behave scenario
        :param scenario_id: the id of the scenario execution received from before scenario
        :return: response of the scenario completion if available
        """
        if self.rp_enable:
            scenario_info = Scenario(scenario, scenario_id=scenario_id)
            for step in scenario.steps:
                if step.status.name == 'undefined':
                    # Logs scenario if it is undefined
                    self.service.log_step_result(end_time=timestamp(),
                                                 message='%s %s - step is undefined.\n' % (
                                                     step.keyword, step.name),
                                                 level='WARN',
                                                 item_id=scenario_info.scenario_id)
                    # Logs scenario as skipped if it is marked for skip
                    # For example scenario marked by @skip tag and --tags=~@skip specified in params of run
                elif step.status.name == 'skipped':
                    self.service.log_step_result(end_time=timestamp(),
                                                 message='%s %s - %s' % (
                                                     step.keyword, step.name, step.status.name.capitalize()),
                                                 level='TRACE',
                                                 item_id=scenario_info.scenario_id)
            #   Finishes scenario
            if scenario.status == 'failed':
                status = "FAILED"
            else:
                status = "PASSED"
            return self.service.finish_scenario_test(end_time=timestamp(),
                                                     status=status,
                                                     item_id=scenario_info.scenario_id)

    def after_feature(self, feature, feature_id, attributes=None):
        """
        Mark the feature as complete and set the status accordingly
        :param feature: the behave feature
        :param feature_id: the id of the feature execution in order to mark it complete
        :param attributes: the attributes to label the feature with
        :return: response of the feature completion if available
        """
        if self.rp_enable:
            feature_info = Feature(feature, feature_id=feature_id)
            for scenario in feature.scenarios:
                try:
                    if 'skip' in scenario.tags:
                        scenario_id = self.service.start_scenario_test(name='Scenario: %s' % scenario.name,
                                                                       description=scenario.description,
                                                                       attributes=attributes,
                                                                       tags=feature_info.tags,
                                                                       start_time=timestamp(),
                                                                       item_type='SCENARIO',
                                                                       parent_item_id=feature_info.feature_id)
                        self.service.finish_scenario_test(end_time=timestamp(),
                                                          status='SKIPPED',
                                                          item_id=scenario_id)
                except IndexError:
                    pass
            #   Finishes feature
            if feature.status == 'failed':
                status = "FAILED"
            else:
                status = "PASSED"
            return self.service.finish_feature(end_time=timestamp(),
                                               status=status,
                                               item_id=feature_info.feature_id)

    def after_all(self, launch_id):
        """
        Finish the test execution and terminate the RP service
        :param launch_id: the id of the execution
        :return: response of the test execution completion if available
        """
        if self.rp_enable:
            launch_completion = self.service.finish_launcher(end_time=timestamp(), launch_id=launch_id)
            self.service.terminate_service()
            return launch_completion
