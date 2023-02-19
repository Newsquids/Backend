from ninja import Schema
from datetime import datetime
from typing import Optional

class NewsInSchema(Schema):
    channel : str
    link : str
    headline : str
    image : str = None
    create_time : datetime
    category : str

class NewsOutSchema(Schema):
    id : int
    link : str
    headline : str
    image : str = None
    create_time : datetime

class NewsChannelSchema(Schema):
    channel_name : str
    
class NewsCategorySchema(Schema):
    category_name : str