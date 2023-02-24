from datetime import timedelta
from django.utils import timezone
from ninja.pagination import paginate, PageNumberPagination
from ninja.errors import HttpError
from ninja_jwt.authentication import JWTAuth
from ninja_extra.shortcuts import get_object_or_exception
from ninja import Router
from news.schemas import NewsInSchema, NewsOutSchema, NewsChannelSchema, NewsCategorySchema, NewsEmail
from news.models import NewsChannel, NewsCategory, News
from django.core.mail.message import EmailMessage
from elasticsearch import Elasticsearch


def search_data(start:int, content:str|int, category_id:int = None, only_channel_data:bool = False):
    '''
    start : int
    only_channel_data : bool
    content:str|int
    only_search:bool
    category_id : int = None

    1. category_id가 None이 아닐때, 무조건 카테고리/채널 데이터 요청 (content = channel_id)
    2. category_id가 None이고, only_channel_data가 True일때, 채널의 데이터 요청 (content = channel_id)
    3. category_id가 None이고, only_channel_data가 False일때, 검색 기능 (content = headline content)

    return => data:list, lastpage:bool
    '''
    es = Elasticsearch(["http://localhost:9200"])
    start_point = start*5

    # 채널의 카테고리 별 자료 가져오기
    if category_id != None:
        match_content = {
            "category_id":f'{category_id}',
            "channel_id":f'{content}'
        }
    # 채널 별 자료 가져요기
    elif only_channel_data == True:
        match_content = {"channel_id":f'{content}'}
    # 검색 기능
    else:
        match_content = {"headline":f'{content}'}

    result = es.search(
        index="news",
        body={
            "from" : start_point,
            "query" : {
                "match" : match_content
            },
            "sort" : [{
                        "id" : {
                                "order" : "desc"
                                }
                        },{
                        "created_time" : {
                                "order" : "desc"
                                }
                        },
                        ],
            "size" : 5
            })
    data = result['hits']['hits']
    last_page =  start_point > (result['hits']['totla']['value'] - 5)
    return data, last_page


router = Router()

@router.post("/channel")
def create_channel(request, payload:NewsChannelSchema):
    for channel in payload.channels:
        NewsChannel.objects.create(channel_name=channel)
    return {"msg" : "채널이 생성되었습니다."}

@router.post("/category")
def create_category(request, payload:NewsCategorySchema):
    for category in payload.categories:
        NewsCategory.objects.create(category_name=category)
    return {"msg" : "카테고리가 생성되었습니다."}

@router.post("")
def create_news(request, payload:NewsInSchema):
    dict_data = payload.dict()
    channel = NewsChannel.objects.get(channel_name=dict_data.pop("channel"))
    category = NewsCategory.objects.get(category_name=dict_data.pop("category"))
    News.objects.create(**dict_data, channel=channel, category=category)
    return {"msg" : "뉴스가 생성되었습니다."}

@router.get("", response=NewsOutSchema)
def read_news(request, page:int, channel:str = None, category:str = None, search:str = None):
    channel_obj = NewsChannel.objects.get(channel_name=channel)
    if category != None:
        category_obj = NewsCategory.objects.get(category_name=category)
        data_list, last_page = search_data(start=page, content=channel_obj.id, category_id=category_obj.id)
    elif search == None:
        data_list, last_page = search_data(start=page, content=channel_obj.id, only_channel_data=True)
    else:
        data_list, last_page = search_data(start=page, content=search)
    res = {"newsItems" : []}
    for data in data_list:
        tem_dict = {}
        tem_dict['newsId'] = data['id']
        tem_dict['newsOriginLink'] = data['link']
        if search != None:
            channel_obj = NewsChannel.objects.get(id=data['channel_id'])
        tem_dict['newsChannel'] = channel_obj.channel_name
        tem_dict['newsImage'] = data['image']
        tem_dict['newsHeadline'] = data['headline']
        if category == None:
            category_obj = NewsCategory.objects.get(category_name=category)
        tem_dict['newsCategory'] = category_obj.category_name
        tem_dict['newsDate'] = data['created_time']
        tem_dict['isBookmarked'] = False
        res["newsItems"].append(tem_dict)
    res["lastPage"] = last_page
    return res

@router.post("/email")
def send_email(request, payload:NewsEmail):
    mail = EmailMessage('test subject','test content', to=payload.emails)
    mail.send()
    return {"msg" : "메일 발송"}