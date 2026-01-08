import logging
import boto3
import time

class ServiceQuota:
    
    def __init__(self, logger=logging.Logger, config=dict):
        
        self.logger = logger
        self.config = config
        self.service_quota_client = boto3.client('service-quotas')
    
    def list_services(self) -> dict:
        
        service_names_codes_list = []
        list_services_response = self.service_quota_client.list_services(
            MaxResults=100
        )
        
        token = list_services_response.get("NextToken")
        
        while token:
                
            tempDict = self.service_quota_client.list_services(
                MaxResults=100,
                NextToken=token
            )
            
            # self.logger.debug(len(tempDict['Services']))
            list_services_response['Services'].extend(tempDict.get("Services", []))
            token = tempDict.get("NextToken")
            
            # self.logger.debug(len(list_services_response['Services']))
            # self.logger.debug(token)
            time.sleep(1)
                
        # self.logger.debug(len(list_services_response['Services']))
        
        if 'Services' in list_services_response:
            list_services_dict = list_services_response['Services']
        
        if list_services_dict:
            # self.logger.debug(list_services_dict)
            
            # self.logger.debug(self.config['services'])
            # self.logger.debug(self.config.items())
            
            for service_quota_item in self.config['services']:
                
                # self.logger.debug('Service: ' + str(service_quota_item))
                
                for list_service_item in list_services_dict:
                    
                    # self.logger.debug("\n\t" + str(service_quota_item['service_name']))
                    # self.logger.debug("\n\t" + str(list_service_item))
                    
                    if str(service_quota_item['service_name']) == str(list_service_item['ServiceName']):
                        
                        temp_dict = service_quota_item
                        temp_dict.update({'service_code': list_service_item['ServiceCode']})
                        
                        service_names_codes_list.append(temp_dict)
                        break

            # self.logger.debug(service_names_codes_list)
            
            return service_names_codes_list
        return {}
    
    def build_quota_requirements_list(self, service_names_codes_list: list) -> list:
        
        quota_requirements_list = []
        
        for service_item in service_names_codes_list:
            
            service_name = service_item['service_name']
            
            if 'quotas' in service_item:
                
                for quota in service_item['quotas']:
                    
                    temp_item = quota
                    temp_item.update({ 'service_name': service_name })
                    temp_item.update({ 'service_code': service_item['service_code'] })
                    
                    quota_requirements_list.append(temp_item)
                    
        self.logger.debug('Quota list: ' + str(quota_requirements_list))
        return quota_requirements_list
    
    def list_service_quotas(self, quota_requirements_list: list) -> dict:
        
        service_quota_codes_list = []
        
        if quota_requirements_list:
        
            for quota_item in quota_requirements_list:
                
                self.logger.debug('Quota Item: ' + str(quota_item))
                
                list_service_quotas_response = self.service_quota_client.list_service_quotas(
                    ServiceCode=quota_item['service_code'],
                    QuotaAppliedAtLevel='ALL',
                    MaxResults=100
                )
                
                # self.logger.debug('list_service_quotas_response: ' + str(list_service_quotas_response))
            
                token = list_service_quotas_response.get("NextToken")
                
                while token:
                        
                    tempDict = self.service_quota_client.list_service_quotas(
                        ServiceCode=quota_item['service_code'],
                        QuotaAppliedAtLevel='ALL',  
                        MaxResults=100,
                        NextToken=token
                    )
                    
                    list_service_quotas_response['Quotas'].extend(tempDict.get("Quotas", []))
                    token = tempDict.get("NextToken")
                    
                    # self.logger.debug(len(list_service_quotas_response['Quotas']))
                    # self.logger.debug(token)
                    time.sleep(1)
                        
                # self.logger.debug(len(list_service_quotas_response['Quotas']))
                
                list_services_quotas_dict = list_service_quotas_response.get('Quotas', [])
                
                if list_services_quotas_dict:
                    
                    # self.logger.debug(self.config['services'])
                    # self.logger.debug(self.config.items())
                    
                    for list_services_quota_item in list_services_quotas_dict:
                            
                        # self.logger.debug('quota_item: ' + str(quota_item))
                        # self.logger.debug('list_services_quota_item: ' + str(list_services_quota_item))
                        
                        if str(quota_item['quota_name']) == str(list_services_quota_item['QuotaName']):
                            
                            service_quota_codes_list.append({
                                "quota_name": quota_item['quota_name'],
                                "quota_code": list_services_quota_item["QuotaCode"],
                                "quota_value": list_services_quota_item["Value"]
                            })
                            break
                    
                    self.logger.debug(service_quota_codes_list)
            return service_quota_codes_list
        return {}
    
    def list_aws_default_service_quotas(self, quota_requirements_list: list) -> dict:
        
        default_service_quota_codes_list = []
        
        if quota_requirements_list:
        
            for quota_item in quota_requirements_list:
                
                list_aws_default_service_quotas_response = self.service_quota_client.list_aws_default_service_quotas(
                    ServiceCode=quota_item['service_code'],
                    MaxResults=100
                )
                
                # self.logger.debug('list_service_quotas_response: ' + str(list_service_quotas_response))
            
                token = list_aws_default_service_quotas_response.get("NextToken")
                
                while token:
                        
                    tempDict = self.service_quota_client.list_aws_default_service_quotas(
                        ServiceCode=quota_item['service_code'],
                        MaxResults=100,
                        NextToken=token
                    )
                    
                    list_aws_default_service_quotas_response['Quotas'].extend(tempDict.get("Quotas", []))
                    token = tempDict.get("NextToken")
                    
                    # self.logger.debug(len(list_aws_default_service_quotas_response['Quotas']))
                    # self.logger.debug(token)
                    time.sleep(1)
                        
                # self.logger.debug(len(list_aws_default_service_quotas_response['Quotas']))
                
                list_aws_default_service_quotas_dict = list_aws_default_service_quotas_response.get('Quotas', [])
                
                if list_aws_default_service_quotas_dict:
                    # self.logger.debug(list_services_dict)
                    
                    # self.logger.debug(self.config['services'])
                    # self.logger.debug(self.config.items())
                    
                    for list_aws_default_service_quota_item in list_aws_default_service_quotas_dict:
                            
                        # self.logger.debug('quota_item: ' + str(quota_item))
                        self.logger.debug('list_aws_default_service_quota_item:' + str(list_aws_default_service_quota_item))
                        
                        if str(quota_item['quota_name']) == str(list_aws_default_service_quota_item['QuotaName']):
                            
                            default_service_quota_codes_list.append({
                                "quota_name": quota_item['quota_name'],
                                "quota_code": list_aws_default_service_quota_item["QuotaCode"],
                                "quota_value": list_aws_default_service_quota_item["Value"]
                            })
                            break
                    
                    # self.logger.debug('default_service_quota_codes_list: ' + str(default_service_quota_codes_list))
            return default_service_quota_codes_list
        return {}
    
    def combine_quotas(self, default_service_quotas_list: list, service_quotas_list: list) -> list:
        
        if default_service_quotas_list or service_quotas_list:
            
            import copy
            combined_service_quota_list = copy.deepcopy(default_service_quotas_list)
            
            for service_quota in service_quotas_list:
                
                # quota_code = 
                # quota_value = service_quota['quota_value']
                
                for default_service_quota in default_service_quotas_list:
                    
                    if default_service_quota['quota_code'] == service_quota['quota_code'] and service_quota['quota_value'] > default_service_quota['quota_value']:
                        
                        for combined_quota in combined_service_quota_list:
                            
                            if combined_quota['quota_code'] == service_quota['quota_code']:
                                
                                combined_service_quota_list[combined_service_quota_list.index(combined_quota)]['quota_value'] = service_quota['quota_value']
                                        
            return combined_service_quota_list
        return []
    
    def compare_quota_requirements_with_actuals(self, combined_service_quota_list: list, quota_requirements_list: list) -> list:
        
        quota_change_list = []
        
        if combined_service_quota_list and quota_requirements_list:
        
            for service_quota in combined_service_quota_list:
                
                for quota_requirement_item in quota_requirements_list:
                    
                    if service_quota['quota_name'] == quota_requirement_item['quota_name'] and service_quota['quota_value'] < quota_requirement_item['request_limit']:
                        
                        # self.logger.debug('Service Quota: ' + str(service_quota))
                        
                        # self.logger.debug('Quota Requirements Item: ' + str(quota_requirement_item))
                        
                        temp_dict = {}
                        temp_dict.update(service_quota)
                        temp_dict.update(quota_requirement_item)
                        
                        quota_change_list.append(temp_dict)

        return quota_change_list
        
    def start_auto_management(self, notification_arn: str) -> dict:
        
        start_auto_management_response = self.service_quota_client.start_auto_management(
            OptInLevel='ACCOUNT',
            OptInType='NotifyOnly',
            NotificationArn=notification_arn
        )
        
        self.logger.debug('start_auto_management_response: ' + str(start_auto_management_response))
        
        return start_auto_management_response
    
    def request_service_quota_increase(self, service_code: str, quota_code: str, desired_value: str) -> dict:
        
        request_service_quota_increase_response = self.service_quota_client.request_service_quota_increase(
            ServiceCode=service_code,
            QuotaCode=quota_code,
            DesiredValue=desired_value,
            SupportCaseAllowed=True
        )
        
        self.logger.debug('request_service_quota_increase_response: ' + str(request_service_quota_increase_response))