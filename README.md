fastapi练习项目

参考：https://www.cnblogs.com/traditional/p/14733610.html

使用 fastapi 需 python 版本大于等于3.6


安装
```
pip install fastapi
pip install uvicorn
```
- uvicorn是一个基于asyncio开发的一个轻量级高效的web服务器框架。
- Starlette 是一个轻量级的 ASGI 框架和工具包，特别适合用来构建高性能的 asyncio 服务。
- pydantic库是一种常用的用于数据接口schema定义与检查的库。


fastapi遵循类型注解


APIRouter类似于Flask中的蓝图，更好的组织大型项目