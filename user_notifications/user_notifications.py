import logging
import time
import boto3
import botocore.exceptions

class UserNotifications:
    
    def __init__(self, logger=logging.Logger, config=dict):
        
        self.logger = logger
        self.config = config
        self.user_notifications_client = boto3.client('notifications')
        
    def list_notification_hubs(self) -> list:
        
        # try:
        
        list_notification_hubs_response = self.user_notifications_client.list_notification_hubs(
            maxResults=3
        )
        
        # self.logger.debug('Notification Hubs: ' + str(list_notification_hubs_response))
        
        return list_notification_hubs_response.get('notificationHubs', [])
            
        # except self.user_notifications_client.exceptions.AccessDeniedException as AccessDeniedException:
        #     self.logger.error("Notification configuration already exists." + str(AccessDeniedException.stack))
        #     raise
        
    def register_notification_hub(self, region_name: str) -> list:

        register_notification_hub_response = self.user_notifications_client.register_notification_hub(
            notificationHubRegion=region_name
        )
        
        # self.logger.debug('New Notification Hubs: ' + str(register_notification_hub_response))
        
        active_notification_hub = False
        notification_hubs_status_list = []
        register_notification_hub_list = []
        
        while not active_notification_hub:
            
            notification_hubs_list = self.list_notification_hubs()
            
            for notification_hub in notification_hubs_list:
                
                notification_hubs_status_list.append(notification_hub.get('statusSummary')['status'])
                
                if notification_hub.get('notificationHubRegion') == region_name:
                    
                    register_notification_hub_list.append(notification_hub)
                
            if all(notification_hub_status == "ACTIVE" for notification_hub_status in notification_hubs_status_list):
                active_notification_hub = True
            else:
                time.sleep(5)
        
        return register_notification_hub_list
        
    def create_notification_configuration(self) -> str:
        
        try:
            create_notification_configuration_response = self.user_notifications_client.create_notification_configuration(
                name='Health-Service-Quotas',
                description='Health notifications created for Service Quotas',
                aggregationDuration='SHORT',  # ISO-8601 duration → 5 minutes
                tags={
                    'Owner': 'LZA',
                    'Usecase': 'Health notifications created for Service Quotas'
                }
            )

            self.logger.debug("Notification configuration created successfully")
            self.logger.debug(f"ARN: {create_notification_configuration_response['arn']}")
            
            return create_notification_configuration_response['arn']

        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "ResourceAlreadyExistsException":
                print("Notification configuration already exists.")
            else:
                raise
            
    def list_notification_configurations(self) -> dict:
        
        list_notification_configurations_response = self.user_notifications_client.list_notification_configurations()
        
        # self.logger.debug('list_notification_configurations_response: ' + str(list_notification_configurations_response))
        
        return list_notification_configurations_response
    
    def create_event_rule(self, notification_arn: str, region_list: list) -> dict:
        
        import json
        
        update_event_pattern = {
            'source': [
                'aws.health'
            ],
            'detail-type': [
                'AWS Health Event'
            ],
            'detail': {
                'service': [
                    'SERVICEQUOTAS'
                ],
                'eventTypeCode': [
                    'AWS_SERVICEQUOTAS_THRESHOLD_BREACH',
                    'AWS_SERVICEQUOTAS_INCREASE_REQUEST_FAILED',
                    'AWS_SERVICEQUOTAS_APPROACHING_THRESHOLD'
                ],
                'eventTypeCategory': [
                    'accountNotification'
                ]
            }
        }
    
        create_event_rule_response = self.user_notifications_client.create_event_rule(
            notificationConfigurationArn=notification_arn,
            source='aws.health',
            eventType='AWS Health Event',
            eventPattern=json.dumps(update_event_pattern),
            regions=region_list
        )
        
        self.logger.debug('create_event_rule_response: ' + str(create_event_rule_response))
        
        return create_event_rule_response
    
    def update_event_rule(self, notification_arn: str, update_event_pattern: dict, region_list: list) -> dict:
    
        import json
        
        update_event_rule_response = self.user_notifications_client.update_event_rule(
            arn=notification_arn,
            eventPattern=json.dumps(update_event_pattern),
            regions=region_list
        )
        
        self.logger.debug('update_event_rule_response: ' + str(update_event_rule_response))
        
        return update_event_rule_response
    
    def get_event_rule(self, notification_arn: str) -> dict:
        
        get_event_rule_response = self.user_notifications_client.get_event_rule(
            arn=notification_arn
        )
        
        self.logger.debug('get_event_rule_response: ' + str(get_event_rule_response))
        
        return get_event_rule_response
            
    def enable_notifications_access_for_organization(self) -> dict:
        
        return self.user_notifications_client.enable_notifications_access_for_organization()