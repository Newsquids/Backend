from ninja.errors import HttpError
from ninja.responses import Response
from django.shortcuts import redirect
from ninja.security import HttpBearer
from django.contrib.auth import get_user_model
from ninja_jwt.authentication import JWTAuth
from ninja_jwt.tokens import RefreshToken
from ninja_extra.shortcuts import get_object_or_exception
from ninja import Router
from user.schemas import SignupSchema, RefreshSchema, CallBackSchema
import os, requests

router = Router()

User = get_user_model()

state = os.getenv("GOOGLE_USER_STATE")
front_redirect_uri = 'http://localhost:3000/google'
client_id = os.getenv("GOOGLE_CLIENT_ID")
client_secret = os.getenv("GOOGLE_CLIENT_SECRET")

@router.post("/signin")
def signin(request, payload:SignupSchema):
    email = payload.email
    user = get_object_or_exception(User,email=email)
    tokens = RefreshToken.for_user(user)
    refresh = str(tokens)
    access = str(tokens.access_token)
    token = {
        "access":access,
        "refresh":refresh
    }
    res = Response(data=token)
    return res

@router.get("/auth/google")
def signin_google(request):
    scope = "https://www.googleapis.com/auth/userinfo.email"
    return Response(f"https://accounts.google.com/o/oauth2/v2/auth?client_id={client_id}&response_type=code&redirect_uri={front_redirect_uri}&scope={scope}")

@router.get("/auth/google/callback")
def callback_google(request, payload:CallBackSchema):
    # 발급 받은 1회성 코드로 구글에 Token 요청
    code = payload.code
    req = requests.post(f"https://oauth2.googleapis.com/token?client_id={client_id}&client_secret={client_secret}&code={code}&redirect_uri={front_redirect_uri}&grant_type=authorization_code")
    req_payload = req.json()

    # Token 발급 중 에러 처리
    error = req_payload.get("error")
    if error != None:
        print("Oauth Token 발급 중 에러가 발생했습니다.")
        raise HttpError(400, error)

    # Code를 통해 받은 Token 추출
    google_access_token = req_payload.get('access_token')

    # Access Token으로 유저 정보 획득
    google_req = requests.get(f"https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={google_access_token}")

    # 유저 정보 획득 중 에러 발생 시 종료
    google_req_status = google_req.status_code
    if google_req_status != 200:
        print("Token으로 유저 정보 발급 중 에러가 발생했습니다.")
        raise HttpError(400, "인증 요청 중 에러가 발생했습니다.")
    
    # 유저 정보에서 이메일 추출
    google_payload = google_req.json()
    email = google_payload.get('email')

    if User.objects.filter(email=email).exists():
        user = get_object_or_exception(User,email=email)
        tokens = RefreshToken.for_user(user)
        refresh = str(tokens)
        access = str(tokens.access_token)
        token = {
            "access":access,
            "refresh":refresh
        }
        res = Response(data=token)
        return res
    else:
        user = User.objects.create(email=email)
        return redirect('http://localhost:3000')

@router.post("/refresh",)
def get_refresh(request, refresh:RefreshSchema):
    token = {}
    token["access"] = refresh.access
    token["refresh"] = refresh.refresh
    return token