from ninja.errors import HttpError
from ninja.responses import Response, resp_codes
from ninja_jwt.authentication import JWTAuth, Any, HttpRequest, Type, AbstractUser, AnonymousUser
from ninja_extra.shortcuts import get_object_or_exception
from ninja import Router
from news.schemas import NewsInSchema, NewsOutSchema, NewsChannelSchema, NewsCategorySchema, NewsEmail
from news.models import NewsChannel, NewsCategory, News
from user.models import UserBookmark
from django.contrib.auth import get_user_model
from django.core.mail.message import EmailMessage
from elasticsearch import Elasticsearch
from typing import Optional
import os

User = get_user_model()

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
    4. start를 제외한 모든 것이 None일때, 최신 데이터 요청

    return => data:list, lastpage:bool
    '''
    es = Elasticsearch([f'{elastic_ip}:9200'])
    start_point = start*5
    filters = None


        
    # 채널의 카테고리 별 자료 가져오기
    if category_id != None:
        try:
            NewsCategory.objects.get(id=category_id)
        except NewsCategory.DoesNotExist:
            raise HttpError(status_code=400, message="존재하지 않는 카테고리 입니다")

        match_content = {
            "match" :
                {
                    "category_id" : f'{category_id}',
                }}
        filters = {
            "term" : {
                "channel_id" : f'{content}'
            }
        }
    # 채널 별 자료 가져요기
    elif only_channel_data == True:
        try:
            NewsChannel.objects.get(id=content)
        except NewsCategory.DoesNotExist:
            raise HttpError(status_code=400, message="존재하지 않는 채널 입니다")

        match_content = {
            "match" :
            {
                "channel_id" : f'{content}'
            }}
    # 검색 기능
    else:
        match_content = {
            "match" :
            {
                "headline" : f'{content}'
            }}

    query = {
        "bool" : {
            "must" : match_content
        }
    }

    if filters != None:
        query["bool"]["filter"] = filters

    # 최신 글 가져오기
    if content == None:
        query = {
            "match_all" : {}
            }

    result = es.search(
        index="news",
        body={
            "from" : start_point,
            "query" : query,
            "sort" : [{
                        "created_time" : {
                                "order" : "desc"
                                }
                        },
                        {
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

def get_user_or_none(request):
    try:
        token = request.headers['Authorization'].split(" ")[1]
        user_email = JWTAuth.jwt_authenticate(JWTAuth(),request=request,token=token)
    except KeyError or IndexError:
        user_email = None
    return user_email


router = Router()

@router.post("/channel")
def create_channel(request, payload:NewsChannelSchema):
    for channel in payload.channels:
        NewsChannel.objects.create(channel_name=channel)
    return Response({"msg" : "채널이 생성되었습니다."})

@router.post("/category")
def create_category(request, payload:NewsCategorySchema):
    for category in payload.categories:
        NewsCategory.objects.create(category_name=category)
    return Response({"msg" : "카테고리가 생성되었습니다."})

@router.post("")
def create_news(request, payload:NewsInSchema):
    dict_data = payload.dict()
    channel = NewsChannel.objects.get(channel_name=dict_data.pop("channel"))
    category = NewsCategory.objects.get(category_name=dict_data.pop("category"))
    News.objects.create(**dict_data, channel=channel, category=category)
    return Response({"msg" : "뉴스가 생성되었습니다."})

@router.get("", response=NewsOutSchema)
def read_news(request, page:int, channel:str = None, category:str = None, search:str = None):
    user_email = get_user_or_none(request)
    if page == None:
        return HttpError(400, "페이지 넘버가 없습니다")
    if category != None and len(category) < 2:
        category = None
    if category != None:
        try:
            category_obj = NewsCategory.objects.get(category_name=category)
        except NewsCategory.DoesNotExist:
            raise HttpError(status_code=400, message="존재하지 않는 카테고리 입니다")
        try:
            channel_obj = NewsChannel.objects.get(channel_name=channel)
        except NewsChannel.DoesNotExist:
            raise HttpError(status_code=400, message="존재하지 않는 채널 입니다")
        data_list, page_number = search_data(start=page, content=channel_obj.id, category_id=category_obj.id)
    elif search == None:
        try:
            channel_obj = NewsChannel.objects.get(channel_name=channel)
        except NewsChannel.DoesNotExist:
            raise HttpError(status_code=400, message="존재하지 않는 채널 입니다")
        data_list, page_number = search_data(start=page, content=channel_obj.id, only_channel_data=True)
    else:
        data_list, page_number = search_data(start=page, content=search)
    if user_email:
        user_id = User.objects.get(email=user_email)
        bookmark_obj = UserBookmark.objects.select_related('news','user').filter(user_id=user_id)
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
        if user_email:
            tem_dict['isBookmarked'] = bookmark_obj.filter(news_id=data['_source']['id']).exists()
        res["newsItems"].append(tem_dict)
    res["pageNumber"] = page_number
    return Response(res)

@router.get("/today", response=NewsOutSchema)
def read_news(request, page:int):
    user_email = get_user_or_none(request)
    if page == None:
        return HttpError(400, '페이지 넘버가 없습니다')
    data_list, page_number = search_data(start=page, content=None)
    res = {"newsItems" : []}
    if user_email:
        user_id = User.objects.get(email=user_email)
        bookmark_obj = UserBookmark.objects.select_related('news','user').filter(user_id=user_id)
    for data in data_list:
        tem_dict = {}
        tem_dict['newsId'] = data['_source']['id']
        tem_dict['newsOriginLink'] = data['_source']['link']
        channel_obj = NewsChannel.objects.get(id=data['_source']['channel_id'])
        tem_dict['newsChannel'] = channel_obj.channel_name
        tem_dict['newsImage'] = data['_source']['image']
        tem_dict['newsHeadline'] = data['_source']['headline']
        category_obj = NewsCategory.objects.get(id=data['_source']['category_id'])
        tem_dict['newsCategory'] = category_obj.category_name
        tem_dict['newsDate'] = data['_source']['created_time']
        if user_email:
            tem_dict['isBookmarked'] = bookmark_obj.filter(news_id=data['_source']['id']).exists()
        tem_dict['isBookmarked'] = False
        res["newsItems"].append(tem_dict)
    res["pageNumber"] = page_number
    return Response(res)

@router.post("/email")
async def send_email(request, payload:NewsEmail):
    mail = EmailMessage('test subject','test content', to=payload.emails)
    mail.send()
    return Response({"msg" : "메일 발송"})

@router.post("/bookmark/{int:news_id}")
def bookmark_news(request, news_id:int):
    # 존재하지 않으면 에러 발생
    
    user = get_object_or_exception(User, email=request.user)
    news = get_object_or_exception(News, id=news_id)
    
    bookmark = UserBookmark.objects.filter(user_id=user.id, news_id=news_id)
    if bookmark:
        bookmark.delete()
        return Response({"msg" : "북마크를 해지하셨습니다"})
    else:
        UserBookmark.objects.create(user_id=user.id, news_id=news_id)
        return Response({"msg" : "북마크를 설정하셨습니다"})