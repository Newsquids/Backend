from ninja.errors import HttpError
from ninja.responses import Response,resp_codes
from django.shortcuts import redirect
from ninja.security import HttpBearer
from django.contrib.auth import get_user_model
from ninja_jwt.authentication import JWTAuth
from ninja_jwt.tokens import RefreshToken
from ninja_extra.shortcuts import get_object_or_exception
from ninja import Router
from user.schemas import SignupSchema, RefreshSchema
import os, requests

router = Router()

User = get_user_model()

state = os.getenv("GOOGLE_USER_STATE")
base_url = 'http://localhost:8000/'
google_callback_uri = base_url + 'api/user/auth/google/callback'
client_id = os.getenv("GOOGLE_CLIENT_ID")
client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
local_secret = os.getenv("LOCAL_SECRET")

class AuthBearer(HttpBearer):
    def authenticate(self, request, token: str):
        if token == local_secret:
            return token

@router.get("/auth/google")
def signin_google(request):
    scope = "https://www.googleapis.com/auth/userinfo.email"
    return redirect(f"https://accounts.google.com/o/oauth2/v2/auth?client_id={client_id}&response_type=code&redirect_uri={google_callback_uri}&scope={scope}")

@router.get("/auth/google/callback")
def callback_google(request):
    code = request.GET.get('code')
    req = requests.post(f"https://oauth2.googleapis.com/token?client_id={client_id}&client_secret={client_secret}&code={code}&grant_type=authorization_code&redirect_uri={google_callback_uri}&state={state}")
    req_payload = req.json()
    error = req_payload.get("error")

    # 에러 발생 시 종료
    if error != None:
        raise HttpError(400,error)

    # 구글 로그인 이후 받은 Access Token 추출
    google_access_token = req_payload.get('access_token')

    # Access Token을 기반으로 유저 정보 획득
    google_req = requests.get(f"https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={google_access_token}")

    # 유저 정보 획득 중 에러 발생 시 종료
    google_req_status = google_req.status_code
    if google_req_status != 200:
        raise HttpError(400, "인증 요청 중 에러가 발생하였습니다.")
    
    ### 2-2. 성공 시 이메일 가져오기
    google_payload = google_req.json()
    email = google_payload.get('email')

    if User.objects.filter(email=email).exists():
        user = get_object_or_exception(User,email=email)
        tokens = RefreshToken.for_user(user)
        refresh = str(tokens)
        access = str(tokens.access_token)
        res = {
            "access":access,
            "refresh":refresh
        }
        return Response(res)
    else:
        data = {'email' : email}
        auth = {'Authorization' : f'Bearer {local_secret}'}
        create_user = requests.post(f"{base_url}api/user/auth/google/signup", json=data, headers=auth)
        create_user_status = create_user.status_code
        if create_user_status != 200:
            raise HttpError(400, "회원가입 중 에러가 발생하였습니다.")
        return Response({"msg" : "회원가입에 성공하였습니다"})

@router.post("/auth/google/signup", auth=AuthBearer())
def signup_user(request, payload:SignupSchema):
    user = User.objects.create(email=payload.email)
    user.save()
    return

@router.post("/refresh",)
def get_refresh(request, refresh:RefreshSchema):
    token = {}
    token["access"] = refresh.access
    token["refresh"] = refresh.refresh
    return token