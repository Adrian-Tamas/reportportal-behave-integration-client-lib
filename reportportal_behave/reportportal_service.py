import logging

from reportportal_client import ReportPortalService
from time import time

logger = logging.getLogger(__name__)


def reportportal_error_handler(exc_info):
    """
    This callback function will be called by async service client when error occurs.
    Return True if error is not critical and you want to continue work.
    :param exc_info: result of sys.exc_info() -> (type, value, traceback)
    :return:
    """
    logger.error(*exc_info, exc_info=True)


def timestamp():
    return str(int(time() * 1000))


class IntegrationService:

    def __init__(self, rp_endpoint, rp_project, rp_token, rp_launch_name, rp_launch_description, verify_ssl=False):
        self.rp_endpoint = rp_endpoint
        self.rp_project = rp_project
        self.rp_token = rp_token
        self.rp_launch_name = rp_launch_name
        self.rp_launch_description = rp_launch_description
        self.rp_async_service = ReportPortalService(endpoint=self.rp_endpoint,
                                                    project=self.rp_project,
                                                    token=self.rp_token,
                                                    verify_ssl=verify_ssl)

    def start_launcher(self, name, start_time, description=None, tags=None):
        return self.rp_async_service.start_launch(name=name,
                                                  start_time=start_time,
                                                  description=description,
                                                  tags=tags)

    def start_feature_test(self, **kwargs):
        return self._start_test(**kwargs)

    def start_scenario_test(self, **kwargs):
        return self._start_test(**kwargs)

    def start_step_test(self, **kwargs):
        return self._start_test(**kwargs)

    def finish_step_test(self, **kwargs):
        return self._finish_test(**kwargs)

    def finish_scenario_test(self, **kwargs):
        return self._finish_test(**kwargs)

    def finish_feature(self, **kwargs):
        return self._finish_test(**kwargs)

    def finish_launcher(self, end_time, launch_id, status=None):
        return self.rp_async_service.finish_launch(end_time=end_time, status=status, launch_id=launch_id)

    def log_step_result(self, end_time, message, level='INFO', attachment=None, item_id=None):
        self.rp_async_service.log(time=end_time,
                                  message=message,
                                  level=level,
                                  attachment=attachment,
                                  item_id=item_id)

    def terminate_service(self):
        self.rp_async_service.terminate()

    def _start_test(self, name, start_time, item_type, description=None, tags=None, parent_item_id=None):
        """
        item_type can be (SUITE, STORY, TEST, SCENARIO, STEP, BEFORE_CLASS,
        BEFORE_GROUPS, BEFORE_METHOD, BEFORE_SUITE, BEFORE_TEST, AFTER_CLASS,
        AFTER_GROUPS, AFTER_METHOD, AFTER_SUITE, AFTER_TEST)
        Types taken from report_portal/service.py
        Mark item as started
        """
        return self.rp_async_service.start_test_item(name=name,
                                                     description=description,
                                                     tags=tags,
                                                     start_time=start_time,
                                                     item_type=item_type,
                                                     parent_item_id=parent_item_id)

    def _finish_test(self, end_time, status, item_id, issue=None):
        """
        Mark item as completed and set the status accordingly
        :param end_time: the end time of the execution
        :param status: the status
        :param item_id: the id of the execution to mark as complete
        :param issue: associate existing issue with the failure
        :return: the response of the
        """
        return self.rp_async_service.finish_test_item(end_time=end_time,
                                               status=status,
                                               issue=issue,
                                               item_id=item_id)

