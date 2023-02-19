from ninja import Schema
from datetime import datetime
from typing import Optional

class NewsInOutSchema(Schema):
    channel : str
    link : str
    headline : str
    image : str = None
    create_time : datetime
    category : str

class NewsChannelSchema(Schema):
    channel_name : str
    
class NewsCategorySchema(Schema):
    category_name : str