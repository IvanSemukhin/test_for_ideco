# main.py

from fun_module import *
from aiohttp import web


async def index(request):
    now = get_now()
    print(request)
    js_dic_news, js_dic_comments = get_all_data()

    js_dic_news[KEY_NEWS].sort(key=lambda el: get_datetime(el[KEY_NEW_DATE]))
    filter_news(js_dic_news, now)
    js_dic_news[KEY_NEWS_COUNT] = len(js_dic_news[KEY_NEWS])

    merge_news_comments(js_dic_news, js_dic_comments)

    return web.json_response(js_dic_news)


async def news(request):
    now = get_now()
    new_id = int(request.match_info[KEY_ID])
    js_dic_news, js_dic_comments = get_all_data()

    found_new = search(js_dic_news, new_id)
    if found_new is None:
        raise web.HTTPNotFound
    if not check_new(found_new, now):
        raise web.HTTPNotFound

    add_comments(found_new, js_dic_comments)

    return web.json_response(found_new)


app = web.Application()
app.router.add_get('/', index)
app.router.add_get('/news/{id}', news)
web.run_app(app)
