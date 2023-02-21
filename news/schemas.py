from ninja import Schema
from datetime import datetime
from typing import Optional, List

class NewsInSchema(Schema):
    channel : str
    link : str
    headline : str
    image : str = None
    created_time : datetime
    category : str

class NewsListSchema(Schema):
    newsId : int
    newsOriginLink : str
    newsChannel : str
    newsImage : str
    newsHeadline : str
    newsCategory : str
    newsDate : datetime
    isBookmarked : bool = False

class NewsOutSchema(Schema):
    newsItems : List[NewsListSchema]

class NewsChannelSchema(Schema):
    channels : list
    
class NewsCategorySchema(Schema):
    categories : list

class NewsEmail(Schema):
    emails : list