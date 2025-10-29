from django.db import models 
import uuid 

class BaseModel(models.Model):
    uid = models.UUIDField(
        unique=True, editable=False, default=uuid.uuid4, primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True) 
    
    class Meta:
        abstract = True