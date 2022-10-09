# -*- coding:utf-8 -*-
from fastapi import FastAPI
import uvicorn

app = FastAPI()


# 绑定路由和视图函数
@app.get("/")
async def index():
    return {"name": "古明地觉"}


# ========================== 路径参数 ====================
# 通过在路径使用{}指定路径参数，路由里的路劲参数可以放任意个，{}里面的参数必须要在定义的视图函数的参数中出现，可以在视图函数的参数采用类型注解的方式规定类型。
# 如果我们传递的值无法转为规定类型，fastapi会进行提示；通过python的类型声明，fastapi提供了数据校验的功能，当校验不通过的时候会清楚地指出没有通过的原因。在我们开发和调试的时候，这个功能非常有用。
@app.get("/apple/{item_id}")
async def get_item(item_id: int):
    return {"item_id": item_id}

# 使用枚举约束参数范围，只能输入枚举参数
from enum import Enum
class Name(str, Enum):
    satori = "古明地觉"
    koishi = "古明地恋"
    marisa = "雾雨魔理沙"
@app.get("/users/{user_name}")
async def get_user(user_name: Name):
    return {"user_id": user_name}

# 数据校验
# 查询参数数据校验使用的是 Query，路径参数数据校验使用的是 Path，两者的使用方式一模一样，没有任何区别。
from fastapi import Path
@app.get("/items/{item-id}")
async def read_items(item_id: int = Path(..., alias="item-id")):
    """
    因为路径参数是必须的，它是路径的一部分，所以我们应该使用 ... 将其标记为必传参数。当然即使不这么做也无所谓，因为指定了默认值也用不上，因为路径参数不指定压根就匹配不到相应的路由。至于一些其它的校验，和查询参数一模一样
    :param item_id:
    :return:
    """
    return {"item_id": item_id}





# ========================= 查询参数 ==========================
# 通过 Python 的类型注解来实现参数类型的限定。
# 通过类型注解进行声明，如果函数中定义了不属于路径参数的参数时，那么它们将会被自动解释会查询参数。可以指定默认值，如下面的age参数
@app.get("/user_id/{user_id}")
async def get_user(user_id: str, name: str, age: int = 0):
    """我们在函数中参数定义了 user_id、name、age 三个参数
       显然 user_id 和 路径参数中的 user_id 对应，然后 name 和 age 会被解释成查询参数
       这三个参数的顺序没有要求，但是一般都是路径参数在前，查询参数在后
    """
    return {"user_id": user_id, "name": name, "age": age}
# 指定多个类型呢？比如 user_id 按照整型解析、解析不成功退化为字符串。
from typing import Union, Optional
@app.get("/user_id2/{user_id}")
async def get_user(user_id: Union[int, str], name: Optional[str] = None):
    """通过 Union 来声明一个混合类型，int 在前、str 在后。会先按照 int 解析，解析失败再变成 str
       然后是 name，它表示字符串类型、但默认值为 None（不是字符串），那么应该声明为 Optional[str]"""
    return {"user_id": user_id, "name": name}

# 多个路径和查询参数
@app.get("/postgres/{schema}/v1/{table}")
async def get_data(schema: str,
                   table: str,
                   select: str = "*",
                   where: Optional[str] = None,
                   limit: Optional[int] = None,
                   offset: Optional[int] = None):
    """标准格式是：路径参数按照顺序在前，查询参数在后
       但其实对顺序是没有什么要求的"""
    query = f"select {select} from {schema}.{table}"
    if where:
        query += f" where {where}"
    if limit:
        query += f" limit {limit}"
    if offset:
        query += f" offset {offset}"
    return {"query": query}

# 数据校验-参数约定限制，通过Query函数来限制参数
from fastapi import Query
@app.get("/user")
async def check_length(
        # 默认值为 None，应该声明为 Optional[str]，当然声明 str 也是可以的。只不过声明为 str，那么默认值应该也是 str
        # 所以如果一个类型允许为空，那么更规范的做法应该是声明为 Optional[类型]。
        # password 是可选的，但是一旦传递则必须传递字符串、而且还是长度在 6 到 15 之间的字符串。所以如果传递的是 None，那么在声明默认值的时候 None 和 Query(None) 是等价的，只不过 Query 还支持其它的参数来对参数进行限制。
        password: Optional[str] = Query(None, min_length=6, max_length=15)
):
    return {"password": password}
# 数据校验-参数约定限制
@app.get("/user")
async def check_length(
        password: str = Query("satori", min_length=6, max_length=15, regex=r"^satori")
):
    """此时的 password 默认值为 'satori'，并且传递的时候必须要以 'satori' 开头
       但是值得注意的是 password 后面的是 str，不再是 Optional[str]，因为默认值不是 None 了
       当然这里即使写成 Optional[str] 也是没有什么影响的
    """
    return {"password": password}
# 数据校验-必须参数
@app.get("/user")
async def check_length(
        password: str = Query(..., min_length=6)
):
    """将第一个参数换成 ... 即可实现该参数是必传参数
    """
    return {"password": password}

# 查询参数转为一个列表
# 访问/items?a1=1&a2=1&a2=2&b=1&b=2
from typing import List
@app.get("/items")
async def read_items(
        a1: str = Query(...),
        a2: List[str] = Query(...),
        b: List[str] = Query(...)
):
    return {"a1": a1, "a2": a2, "b": b}
# 如果允许为 None（或者有默认值）的话，那么应该这么写：
@app.get("/items")
async def read_items(
        a1: str,
        a2: Optional[List[str]] = Query(None),
        b: List[str] = Query(["1", "嘿嘿"])
):
    return {"a1": a1, "a2": a2, "b": b}

# 参数起别名
# 访问 /items?item-query=123&@@@@=456&$$$$=123
@app.get("/items")
async def read_items(
        # 通过 url 的时候使用别名即可
        item1: Optional[str] = Query(None, alias="item-query"),
        item2: str = Query("哈哈", alias="@@@@"),
        item3: str = Query(..., alias="$$$$")  # item3 是必传的
):
    return {"item1": item1, "item2": item2, "item3": item3}



# ============================== Post请求体 ============================
# 在 FastAPI 中，请求体和响应体都对应一个 Model
from pydantic import BaseModel
class Girl(BaseModel):
    """数据验证是通过 pydantic 实现的，我们需要从中导入 BaseModel，然后继承它"""
    name: str
    age: Optional[str] = None
    length: float
    hobby: List[str]  # 对于 Model 中的 List[str] 我们不需要指定 Query（准确的说是 Field）

@app.post("/girl")
async def read_girl(girl: Girl):
    # girl 就是我们接收的请求体，它需要通过 json 来传递，并且这个 json 要有上面的四个字段（age 可以没有）
    # 通过 girl.xxx 的方式我们可以获取和修改内部的所有属性
    return dict(girl)  # 直接返回 Model 对象也是可以的

# 除了使用这种方式之外，我们还可以使用之前说的 Request 对象
from fastapi import Request
@app.post("/girl")
async def read_girl(request: Request):
    # 是一个协程，所以需要 await
    data = await request.body()  # 原始字节流
    # data = await request.json()  # 在拿到字节流后，自动loads成字典，请求数对应使用json进行参数传递
    print(data)
# 使用requests发送post请求时，通过json参数传递时，会将参数自动转为json字符串；通过data参数传递时，会将其拼接成k1=v1&k2=v2的形式进行传输。


# 路径参数、查询参数、请求体，三者混在一起
class Girl(BaseModel):
    name: str
    age: Optional[str] = None
    length: float
    hobby: List[str]


@app.post("/girl/{user_id}")
async def read_girl(user_id,
                    q: str,
                    girl: Girl):

    return {"user_id": user_id, "q": q, **dict(girl)}
# 也可以使用 Request 对象
from typing import Dict
@app.post("/girl/{user_id}")
async def read_girl(user_id,
                    request: Request):

    q = request.query_params.get("q")
    data: Dict = await request.json()
    data.update({"user_id": user_id, "q": q})
    return data
# 多个请求体
class Girl(BaseModel):
    name: str
    age: Optional[str] = None


class Boy(BaseModel):
    name: str
    age: int


@app.post("/boy_and_girl")
async def read_boy_and_girl(girl: Girl,
                            boy: Boy):
    return {"girl": dict(girl), "boy": dict(boy)}

# 请求方式:requests.post('url', json={'girl': {'name': '123', 'age':12}, 'boy':{'name': '456', 'age':17}})
# 等价于
class BoyAndGirl(BaseModel):
    girl: Dict
    boy: Dict

@app.post("/boy_and_girl")
async def read_boy_and_girl(boy_and_girl: BoyAndGirl):
    return dict(boy_and_girl)

# ===================== From 表单 ============================
# 通过requests.post的参数data传递数据，就相当于提供了一个form表单，在fastapi中可以通过 await requets.form() 获取
@app.post("/girl")
async def girl(request: Request):
    # 此时 await request.json() 报错，因为是通过 data 参数传递的，相当于 form 表单提交
    # 如果是通过 json 参数传递，那么 await request.form() 会得到一个空表单
    form = await request.form()
    return [form.get("name"), form.getlist("age")]
# 其他方式
from fastapi import Form
@app.post("/user")
async def get_user(username: str = Form(...),
                   password: str = Form(...)):
    return {"username": username, "password": password}


# ==================== Depends ======================
# 能够很好的实现依赖注入，而且我们特意写了两个路由，就是想表示它们是彼此独立的。因此当有共享的逻辑、或者共享的数据库连接、增强安全性、身份验证、角色权限等等，会非常的实用。
from fastapi import Depends
async def common_parameters(q: Optional[str] = None, skip: int = 0, limit: int = 100):
    return {"q": q, "skip": skip, "limit": limit}
@app.get("/items/")
async def read_items(commons: dict = Depends(common_parameters)):
    # common_parameters 接收三个参数：q、skip、limit
    # 然后在解析请求的时候，会将 q、skip、limit 传递到 common_parameters 中，然后将返回值赋值给 commons
    # 但如果解析不到某个参数时，那么会判断函数中参数是否有默认值，没有的话就会返回错误，而不是传递一个 None 进去
    return commons
@app.get("/users/")
async def read_users(commons: dict = Depends(common_parameters)):
    return commons


# ==================== Requests =================
# 通过 Request 对象可以获取所有请求相关的信息，我们之前当参数传递不对的时候，FastAPI 会自动帮我们返回错误信息，但通过 Request 我们就可以自己进行解析、自己指定返回的错误信息了.
from fastapi import Request
@app.get("/girl/{user_id}")
async def read_girl(user_id: str,
                    request: Request):
    """路径参数是必须要体现在参数中，但是查询参数可以不写了
       因为我们定义了 request: Request，那么请求相关的所有信息都会进入到这个 Request 对象中"""
    header = request.headers  # 请求头
    method = request.method  # 请求方法
    cookies = request.cookies  # cookies
    query_params = request.query_params  # 查询参数
    return {"name": query_params.get("name"), "age": query_params.get("age"), "hobby": query_params.getlist("hobby")}



# ===================== Response ===================
# 尽管我们可以直接返回一个字典，但 FastAPI 实际上会帮我们转成一个 Response 对象。
# Response 内部接收如下参数:
# content：返回的数据
# status_code：状态码
# headers：返回的请求头
# media_type：响应类型(就是 HTML 中 Content-Type，只不过这里换了个名字)
# background：接收一个任务，Response 在返回之后会自动异步执行
from fastapi import Response
import orjson
@app.get("/girl/{user_id}")
async def read_girl(user_id: str,
                    request: Request):
    query_params = request.query_params  # 查询参数
    data = {"name": query_params.get("name"), "age": query_params.get("age"), "hobby": query_params.getlist("hobby")}
    # 实例化一个 Response 对象
    response = Response(
        # content，我们需要手动转成 json 字符串，如果直接返回字典的话，那么在包装成 Response 对象的时候会自动帮你转
        orjson.dumps(data),
        # status_code，状态码
        201,
        # headers，响应头
        {"Token": "xxx"},
        # media_type，就是 HTML 中的 Content-Type
        "application/json",
    )
    # 如果想设置 cookie 的话，那么通过 response.set_cookie 即可
    # 删除 cookie 则是 response.delete_cookie
    return response
# 另外除了 Response 之外还有很多其它类型的响应，它们都在 fastapi.responses 中，比如：FileResponse、HTMLResponse、PlainTextResponse 等等。它们都继承了 Response，只不过会自动帮你设置响应类型
from fastapi.responses import Response, HTMLResponse
@app.get("/index")
async def index():

    response1 = HTMLResponse("<h1>你好呀</h1>")
    response2 = Response("<h1>你好呀</h1>", media_type="text/html")
    # 以上两者是等价的，在 HTMLResponse 中会自动将 media_type 设置成 text/html
    return response1


# 其他响应
# 返回 json 数据可以是：JSONResponse、UJSONResponse、ORJSONResponse，Content-Type 是 application/json；
# 返回 html 是 HTMLResponse，Content-Type 是 text/html；
# 返回 PlainTextResponse，Content-Type 是 text/plain。
# 但是我们还可以有三种响应，分别是返回重定向、字节流、文件。
# 重定向
from fastapi.responses import RedirectResponse
@app.get("/index")
async def index():
    return RedirectResponse("https://www.bilibili.com")
@app.get("/redirect")
async def redirect():
    url = app.url_path_for("index")
    response = RedirectResponse(url=url)
    return response
# 文件
from fastapi.responses import FileResponse
@app.get("/index")
async def index():
    # filename 如果给出，它将包含在响应的 Content-Disposition 中。
    return FileResponse("main.py", filename="这不是main.py")


# ================== 静态资源 =================
# name 参数只是起一个名字，FastAPI 内部使用
# 浏览器输入：localhost:5555/static/1.png，那么会返回 项目static 下的 1.png 文件。
from fastapi.staticfiles import StaticFiles
app.mount("static", StaticFiles(directory=r".\static"), name="static")


# ====================== 模板渲染 =========================
# FastAPI 常用Jinja2模板引擎实现页面渲染
from fastapi import requests
from fastapi.templating import Jinja2Templates
# 实例化一个模板引擎对象，指定模板所在路径
templates=Jinja2Templates(directory='templates')
@app.get('/index/{info}')
# 在视图函数中传入request对象，用于在模板对象中传递上下文（同时接收路径参数info，将其传递到上下文中）
async def index(request:Request,info:str):
    # 返回一个模板对象，同时使用上下文中的数据对模板进行渲染
    return templates.TemplateResponse(name='index.html', context={'request':request,'info':info})



# =================== 错误处理 ===============
from fastapi import HTTPException
@app.get("/items/{item_id}")
async def read_item(item_id: str):
    if item_id != "foo":
        # 里面还可以传入 headers 设置响应头
        raise HTTPException(status_code=404, detail="item 没有发现")
    return {"item": "bar"}
# HTTPException 是一个普通的 Python 异常类（继承了 Exception），它携带了 API 的相关信息，既然是异常，那么我们不能 return、而是要 raise。
# 个人觉得这个不是很常用，至少我本人很少用这种方式返回错误，因为它能够携带的信息太少了。

# 自定义异常
# 自定义完异常之后，还要定义一个 handler，将异常和 handler 绑定在一起，然后引发该异常的时候就会触发相应的 handler。

from fastapi.responses import ORJSONResponse
class ASCIIException(Exception):
    """自定义异常"""
    pass
# 通过装饰器的方式，将 ASCIIException 和 ascii_exception_handler 绑定在一起
@app.exception_handler(ASCIIException)
async def ascii_exception_handler(request: Request, exc: ASCIIException):
    """当引发 ASCIIException 的时候，会触发 ascii_exception_handler 的执行
       同时会将 request 和 exception 传过去"""
    return ORJSONResponse(status_code=404, content={"code": 404, "message": "你必须传递 ascii 字符串"})

@app.get("/items/{item_id}")
async def read_item(item_id: str):
    if not item_id.isascii():
        raise ASCIIException
    return {"item": f"get {item_id}"}
# 关于 Request、Response，我们除了可以通过 fastapi 进行导入，还可以通过 starlette 进行导入，因为 fastapi 的路由映射是通过 starlette 来实现的。当然我们直接从 fastapi 中进行导入即可。

# 自定义404
from fastapi.exceptions import StarletteHTTPException
@app.exception_handler(StarletteHTTPException)
async def not_found(request, exc):
    return ORJSONResponse({"code": 404, "message": "您要找的页面去火星了。。。"})




# ======================== 后台任务 ==========================
# 如果一个请求耗时特别久，那么我们可以将其放在后台执行
import time
from fastapi import BackgroundTasks
def send_email(email: str, message: str = ""):
    """发送邮件，假设耗时三秒"""
    time.sleep(3)
    print(f"三秒之后邮件发送给 {email!r}, 邮件信息: {message!r}")

@app.get("/user/{email}")
async def order(email: str, bg_tasks: BackgroundTasks):
    """这里需要多定义一个参数
       此时任务就被添加到后台，当 Response 对象返回之后触发"""
    bg_tasks.add_task(send_email, email, message="这是一封邮件")
    # 我们在之前介绍 Response 的时候说过，里面有一个参数 background
    # 所以我们也可以将任务放在那里面
    # 因此我们还可以：
    # return Response(orjson.dumps({"message": "邮件发送成功"}), background=BackgroundTask(send_email, email, message="这是一封邮件"))
    return {"message": "邮件发送成功"}



# ============================= APIRouter ======================
# 将 router 注册到 apps 中，相当于 Flask 中的 register_blueprint
from apps.app01 import router1
from apps.app02 import router2
app.include_router(router1)
app.include_router(router2)


# ============================== 中间件 =========================
# 中间件就是一个函数或者一个类。在请求进入视图函数之前，会先经过中间件（被称为请求中间件），而在中间件里面，我们可以对请求进行一些预处理，或者实现一个拦截器等等；同理当视图函数返回响应之后，也会经过中间件（被称为响应中间件），在中间件里面，我们也可以对响应进行一些润色。
# 自定义中间件
@app.get("/")
async def view_func(request: Request):
    return {"name": "古明地觉"}


@app.middleware("http")
async def middleware(request: Request, call_next):
    """
    定义一个协程函数，然后使用 @apps.middleware("http") 装饰，即可得到中间件
    """
    # 请求到来时会先经过这里的中间件
    if request.headers.get("ping", "") != "pong":
        response = Response(content=orjson.dumps({"error": "请求头中缺少指定字段"}),
                            media_type="application/json",
                            status_code=404)
        # 当请求头中缺少 "ping": "pong"，在中间件这一步就直接返回了，就不会再往下走了
        # 所以此时就相当于实现了一个拦截器
        return response
    # 然后，如果条件满足，则执行 await call_next(request)，关键是这里的 call_next
    # 如果该中间件后面还有中间件，那么 call_next 就是下一个中间件；如果没有，那么 call_next 就是对应的视图函数
    # 这里显然是视图函数，因此执行之后会拿到视图函数返回的 Response 对象
    # 所以我们看到在 FastAPI 中，请求中间件和响应中间件合在一起了
    response: Response = await call_next(request)
    # 这里我们在设置一个响应头
    response.headers["status"] = "success"
    return response

# 内置中间件
# 通过自定义中间件，我们可以在不修改视图函数的情况下，实现功能的扩展。但是除了自定义中间件之外，FastAPI 还提供了很多内置的中间件。
# 要求请求协议必须是 https 或者 wss，如果不是，则自动跳转
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
# apps.add_middleware(HTTPSRedirectMiddleware)

# 请求中必须包含 Host 字段，为防止 HTTP 主机报头攻击，并且添加中间件的时候，还可以指定一个 allowed_hosts，那么它是干什么的呢？
# 假设我们有服务 a.example.com, b.example.com, c.example.com
# 但我们不希望用户访问 c.example.com，就可以像下面这么设置，如果指定为 ["*"]，或者不指定 allow_hosts，则表示无限制
from starlette.middleware.trustedhost import TrustedHostMiddleware
# apps.add_middleware(TrustedHostMiddleware, allowed_hosts=["a.example.com", "b.example.com"])

# 如果用户的请求头的 Accept-Encoding 字段包含 gzip，那么 FastAPI 会使用 GZip 算法压缩
# minimum_size=1000 表示当大小不超过 1000 字节的时候就不压缩了
from starlette.middleware.gzip import GZipMiddleware
# apps.add_middleware(GZipMiddleware, minimum_size=1000)



# ============================= CORS ===================================
# 协议、域名、端口三者只要有一个不同，就属于不同源
# 解决跨域问题
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    # 允许跨域的源列表，例如 ["http://www.example.org"] 等等，["*"] 表示允许任何源
    allow_origins=["*"],
    # 跨域请求是否支持 cookie，默认是 False，如果为 True，allow_origins 必须为具体的源，不可以是 ["*"]
    allow_credentials=False,
    # 允许跨域请求的 HTTP 方法列表，默认是 ["GET"]
    allow_methods=["*"],
    # 允许跨域请求的 HTTP 请求头列表，默认是 []，可以使用 ["*"] 表示允许所有的请求头
    # 当然 Accept、Accept-Language、Content-Language 以及 Content-Type 总之被允许的
    allow_headers=["*"],
    # 可以被浏览器访问的响应头, 默认是 []，一般很少指定
    # expose_headers=["*"]
    # 设定浏览器缓存 CORS 响应的最长时间，单位是秒。默认为 600，一般也很少指定
    # max_age=1000
)


# ======================== HTTP 验证 ======================
# 验证用户名密码
from fastapi.security import HTTPBasic, HTTPBasicCredentials
security = HTTPBasic()

@app.get("/index")
async def index(credentials: HTTPBasicCredentials = Depends(security)):
    return {"username": credentials.username, "password": credentials.password}




# ======================== websocket =============================
from fastapi.websockets import WebSocket
@app.websocket("/ws")
async def ws(websocket: WebSocket):
    await websocket.accept()
    while True:
        # websocket.receive_bytes()
        # websocket.receive_json()
        data = await websocket.receive_text()
        await websocket.send_text(f"收到来自客户端的回复: {data}")

# <!DOCTYPE html>
# <html lang="en">
# <head>
#     <meta charset="UTF-8">
#     <title>Title</title>
# </head>
# <body>
#     <script>
#         ws = new WebSocket("ws://localhost:5555/ws");
#
#         //如果连接成功, 会打印下面这句话, 否则不会打印
#         ws.onopen = function () {
#             console.log('连接成功')
#         };
#
#         //接收数据, 服务端有数据过来, 会执行
#         ws.onmessage = function (event) {
#             console.log(event)
#         };
#
#         //服务端主动断开连接, 会执行.
#         //客户端主动断开的话, 不执行
#         ws.onclose = function () {  }
#
#     </script>
# </body>
# </html>


# ================================ 部署 ==================================
# 直接 uvicorn.run 即可。run()参数如下：
# apps：第一个参数，不需要解释
# host：监听的ip
# port：监听的端口
# uds：绑定的 unix domain socket，一般不用
# fd：从指定的文件描述符中绑定 socket
# loop：事件循环实现，可选项为 auto|asyncio|uvloop|iocp
# http：HTTP 协议实现，可选项为 auto|h11|httptools
# ws：websocket 协议实现，可选项为 auto|none|websockets|wsproto
# lifespan：lifespan 实现，可选项为 auto|on|off
# env_file：环境变量配置文件
# log_config：日志配置文件
# log_level：日志等级
# access_log：是否记录日志
# use_colors：是否带颜色输出日志信息
# interface：应用接口，可选 auto|asgi3|asgi2|wsgi
# debug：是否开启 debug 模式
# reload：是否自动重启
# reload_dirs：要自动重启的目录
# reload_delay：多少秒后自动重启
# workers：工作进程数
# limit_concurrency：并发的最大数量
# limit_max_requests：能 hold 住的最大请求数


# 在 Windows 中必须加上 if __name__ == "__main__"，否则会抛出 RuntimeError: This event loop is already running
if __name__ == "__main__":
    # 启动服务，因为我们这个文件叫做 main.py，所以需要启动 main.py 里面的 apps
    # 第一个参数 "main:apps" 就表示这个含义，然后是 host 和 port 表示监听的 ip 和端口
    uvicorn.run("main:apps", host="0.0.0.0", port=5555, reload=True)


# FastAPI 会自动提供一个类似于 Swagger 的交互式文档，访问交互式文档，url：/docs
# 可以设置docs页面本身
# apps = FastAPI(title="测试文档", description="这是一个简单的 demo", docs_url="/my_docs", openapi_url="/my_openapi")