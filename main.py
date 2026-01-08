import json
import logging
from os import environ

# Setting up the logging level from the environment variable `LOGLEVEL`.
if 'LOG_FILENAME' in environ.keys():
    logging.basicConfig(
        filename=environ['LOG_FILENAME'],
        filemode='a',
        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
        datefmt='%H:%M:%S'
    )
    logger = logging.getLogger(__name__)
else:
    logging.basicConfig()
    logger = logging.getLogger(__name__)

logger.setLevel(environ['LOG_LEVEL'] if 'LOG_LEVEL' in environ.keys() else 'INFO')

try:
    from pydantic import ValidationError
    from config.data_model import Config
    
    _config_model = Config()
    with open('config.json', 'r') as config_file:
        config = json.loads(config_file.read())
        
        _config_model = Config(
            level=config['level'],
            services=config['services']
        )
        
    # logger.debug(type(_config_model))
    # logger.debug(_config_model)
    
    from service_quota.service_quota import ServiceQuota
    service_quota = ServiceQuota(
        logger=logger,
        config=config
    )
    
    service_names_codes_list = service_quota.list_services()
    
    quota_requirements_list = service_quota.build_quota_requirements_list(
        service_names_codes_list=service_names_codes_list
    )
    
    logger.debug(len(quota_requirements_list))
    
    service_quotas_list = service_quota.list_service_quotas(
        quota_requirements_list=quota_requirements_list
    )
    
    logger.debug('Service Quota List: ' + str(service_quotas_list))
    
    default_service_quotas_list = service_quota.list_aws_default_service_quotas(
        quota_requirements_list=quota_requirements_list
    )
    
    logger.debug('Default Service Quota List: ' + str(default_service_quotas_list))
    
    combined_service_quota_list = service_quota.combine_quotas(
        default_service_quotas_list=default_service_quotas_list,
        service_quotas_list=service_quotas_list
    )
    
    logger.debug('Combined Quotas List: ' + str(combined_service_quota_list))
    
    quota_change_list = service_quota.compare_quota_requirements_with_actuals(
        combined_service_quota_list=combined_service_quota_list,
        quota_requirements_list=quota_requirements_list
    )
    
    logger.debug('Quota Change List: ' + str(quota_change_list))
    
    from user_notifications.user_notifications import UserNotifications
    user_notifications = UserNotifications(
        logger=logger,
        config=config
    )
    
    list_notification_hubs_response = user_notifications.list_notification_hubs()
    
    if not list_notification_hubs_response:
        
        list_notification_hubs_response = user_notifications.register_notification_hub(
            region_name='us-east-1'
        )
    
    list_notification_configurations_response = user_notifications.list_notification_configurations()
    
    user_notification_arn = ''
    
    for notification_config in list_notification_configurations_response.get('notificationConfigurations', []):
        
        user_notification_arn = notification_config.get('arn', '')
        
    if not user_notification_arn:
    
        user_notification_arn = user_notifications.create_notification_configuration()
        
    # user_notifications.get_event_rule(
    #     arn='arn:aws:events:us-east-1:637423271362:rule/AWSUserNotificationsManagedRule-a4rxgut'
    # )
        
    user_notifications.create_event_rule(
        notification_arn=user_notification_arn,
        region_list=['us-east-1', 'us-east-2']
    )
        
    changelog_list = []
    for quota_change_item in quota_change_list:
        
        request_service_quota_increase_response = service_quota.request_service_quota_increase(
            service_code=quota_change_item['service_code'],
            quota_code=quota_change_item['quota_code'],
            desired_value=quota_change_item['request_limit']
        )
        
        changelog_list.append(request_service_quota_increase_response)
        
    logger.debug('Changelog: ' + str(changelog_list))
        
    start_auto_management_response = service_quota.start_auto_management(
        notification_arn=user_notification_arn
    )
        
    if config['level'] == 'organization':
        
        user_notifications.enable_notifications_access_for_organization()
    
except ValidationError as validation_err:
    logger.error(validation_err)
    raise