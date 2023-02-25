from datetime import timedelta
from django.utils import timezone
from ninja.errors import HttpError
from ninja_jwt.authentication import JWTAuth
from ninja_extra.shortcuts import get_object_or_exception
from ninja import Router
from news.schemas import NewsInSchema, NewsOutSchema, NewsChannelSchema, NewsCategorySchema, NewsEmail
from news.models import NewsChannel, NewsCategory, News
from django.core.mail.message import EmailMessage
from elasticsearch import Elasticsearch
import os

elastic_ip = os.getenv("ELASTIC_IP")

def search_data(start:int, content:str or int, category_id:int = None, only_channel_data:bool = False):
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
    es = Elasticsearch([f'{elastic_ip}:9200'])
    start_point = start*5
    filters = None

    # 채널의 카테고리 별 자료 가져오기
    if category_id != None:
        match_content = {
            "category_id":f'{category_id}',
        }
        filters = {
            "term" : {
                "channel_id" : f'{content}'
            }
        }
    # 채널 별 자료 가져요기
    elif only_channel_data == True:
        match_content = {"channel_id":f'{content}'}
    # 검색 기능
    else:
        match_content = {"headline":f'{content}'}

    query = {
        "bool" : {
            "must" : {
                "match" : match_content
            }
        }
    }

    if filters != None:
        query["bool"]["filter"] = filters

    result = es.search(
        index="news",
        body={
            "from" : start_point,
            "query" : query,
            "sort" : [{
                        "created_time" : {
                                "order" : "desc"
                                }
                        },{
                        "id" : {
                                "order" : "desc"
                                }
                        },
                        ],
            "size" : 5
            })
    data = result['hits']['hits']
    page_number =  ((result['hits']['total']['value'] - 1)//5)
    return data, page_number


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
    if category != None and len(category) < 2:
        category = None
    if category != None:
        channel_obj = NewsChannel.objects.get(channel_name=channel)
        category_obj = NewsCategory.objects.get(category_name=category)
        data_list, page_number = search_data(start=page, content=channel_obj.id, category_id=category_obj.id)
    elif search == None:
        channel_obj = NewsChannel.objects.get(channel_name=channel)
        data_list, page_number = search_data(start=page, content=channel_obj.id, only_channel_data=True)
    else:
        data_list, page_number = search_data(start=page, content=search)
    res = {"newsItems" : []}
    for data in data_list:
        tem_dict = {}
        tem_dict['newsId'] = data['_source']['id']
        tem_dict['newsOriginLink'] = data['_source']['link']
        if search != None:
            channel_obj = NewsChannel.objects.get(id=data['_source']['channel_id'])
        tem_dict['newsChannel'] = channel_obj.channel_name
        tem_dict['newsImage'] = data['_source']['image']
        tem_dict['newsHeadline'] = data['_source']['headline']
        if category == None:
            category_obj = NewsCategory.objects.get(id=data['_source']['category_id'])
        tem_dict['newsCategory'] = category_obj.category_name
        tem_dict['newsDate'] = data['_source']['created_time']
        tem_dict['isBookmarked'] = False
        res["newsItems"].append(tem_dict)
    res["pageNumber"] = page_number
    return res

@router.get("/rescent", response=NewsOutSchema)
def read_news(request, page:int, channel:str = None, category:str = None, search:str = None):
    if category == None or len(category) < 2:
        category = None
    try:
        channel_obj = NewsChannel.objects.get(channel_name=channel)
    except:
        raise HttpError (status_code=400,message={"msg" : "채널명이 잘못되었습니다."})
    if category != None:
        category_obj = NewsCategory.objects.get(category_name=category)
        data_list, page_number = search_data(start=page, content=channel_obj.id, category_id=category_obj.id)
    elif search == None:
        data_list, page_number = search_data(start=page, content=channel_obj.id, only_channel_data=True)
    else:
        data_list, page_number = search_data(start=page, content=search)
    res = {"newsItems" : []}
    for data in data_list:
        tem_dict = {}
        tem_dict['newsId'] = data['_source']['id']
        tem_dict['newsOriginLink'] = data['_source']['link']
        if search != None:
            channel_obj = NewsChannel.objects.get(id=data['_source']['channel_id'])
        tem_dict['newsChannel'] = channel_obj.channel_name
        tem_dict['newsImage'] = data['_source']['image']
        tem_dict['newsHeadline'] = data['_source']['headline']
        if category == None:
            category_obj = NewsCategory.objects.get(id=data['_source']['category_id'])
        tem_dict['newsCategory'] = category_obj.category_name
        tem_dict['newsDate'] = data['_source']['created_time']
        tem_dict['isBookmarked'] = False
        res["newsItems"].append(tem_dict)
    res["pageNumber"] = page_number
    return res

@router.post("/email")
def send_email(request, payload:NewsEmail):
    mail = EmailMessage('test subject','test content', to=payload.emails)
    mail.send()
    return {"msg" : "메일 발송"}