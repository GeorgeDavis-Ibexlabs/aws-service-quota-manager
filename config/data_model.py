from pydantic import BaseModel
from typing import List, Optional
    
class ServiceQuotaItem(BaseModel):
    service_name: Optional[str] = ''
    quota_name: str
    request_limit: int
    
class ServiceQuotas(BaseModel):
    service_name: str
    quotas: List[ServiceQuotaItem] = []
    
class Config(BaseModel):
    level: str = 'account'
    services: List[ServiceQuotas] = []