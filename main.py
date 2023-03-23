import os
import jinja2
from fastapi import FastAPI, Request, Response, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2AuthorizationCodeBearer, OAuth2Callback
from fastapi_login import LoginManager
from fastapi_login.exceptions import InvalidCredentialsException
from fastapi_login.github import GitHubOAuth2

app = FastAPI()

# set up static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# set up jinja2 templates
templates = Jinja2Templates(directory="templates")

# set up GitHub OAuth2 client
github_oauth = GitHubOAuth2(
    client_id=os.environ.get("GITHUB_CLIENT_ID"),
    client_secret=os.environ.get("GITHUB_CLIENT_SECRET"),
)

# set up login manager
login_manager = LoginManager(
    "TODOList",
    token_url="/login",
    authorization_url="/github_login",
    secret=os.environ.get("FLASK_SECRET_KEY", "supersekrit"),
    use_cookie=True,
    cookie_secure=False,
)

# set up OAuth2 bearer token
oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="/github_login",
    tokenUrl="/login",
    scopes={"user:email"},
)

# set up GitHub OAuth2 callback
@app.get("/github_callback")
async def github_callback(code: str):
    try:
        token = await github_oauth.get_access_token(code)
        user_info = await github_oauth.get_user_info(token)
        return login_manager.create_response(
            Response,
            payload={"user_id": user_info["id"]},
            headers={"Location": "/"},
            status_code=status.HTTP_302_FOUND,
        )
    except Exception as e:
        raise InvalidCredentialsException(str(e))


# set up login endpoint
@app.post("/login")
async def login(response: Response, data: OAuth2Callback = None):
    if data:
        return await login_manager.login_user(
            response,
            data,
            scheme=oauth2_scheme,
        )
    else:
        return templates.TemplateResponse(
            "login.html",
            {"request": request},
        )


# set up logout endpoint
@app.get("/logout")
async def logout(response: Response):
    return await login_manager.logout_user(
        response,
        scheme=oauth2_scheme,
    )


# set up root endpoint
@app.get("/", response_class=HTMLResponse)
async def index(request: Request, user_id=login_manager.user_id):
    user = None
    if user_id:
        user = await github_oauth.get_user_info(
            login_manager.get_access_token(request),
        )
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "logged_in": bool(user_id),
            "user": user,
            "tasks": ["task 1", "task 2", "task 3"],
            "login_url": login_manager.get_login_url(request),
            "logout_url": login_manager.get_logout_url(request),
        },
    )

