from datetime import datetime, timedelta

from flask import render_template, Blueprint, request
from pony.orm import select

from db import Page, UserRSS, RSS
from util.tool import check_user, select_website, redirect_home, guess_locale

page_bp = Blueprint('page', __name__, template_folder='templates')

page_bp.before_request(check_user)


@page_bp.route('/', methods=['GET'])
def index():
    """根据用户是否登录判断返回页面"""
    cl = guess_locale()
    last_year = datetime.utcnow() - timedelta(days=365)
    if hasattr(request, 'user') and request.user:
        sites, categories = select_website()
        pages = sorted(select(
            (p.page_id, p.title, p.link, p.publish_date, p.rss, ur.name) for ur in UserRSS for p in Page
            if ur.user == request.user and not ur.delete
            and p.publish_date > last_year and ur.rss == p.rss
        ), key=lambda x: x[3], reverse=True)
        return render_template('index.html', sites=sites, categories=categories, pages=pages, locale=cl)

    pages = sorted(select(
        (p.page_id, p.title, p.link, p.publish_date, p.rss, r.name) for p in Page for r in RSS
        if r.mark == 1 and p.publish_date > last_year and p.rss == r
    ), key=lambda x: x[3], reverse=True)

    if cl == 'zh':
        return render_template('index.zh.html', pages=pages)
    return render_template('index.en.html', pages=pages)


@page_bp.route('/<cl>/shopping', methods=['GET'])
def shopping(cl):
    """购物网站"""
    if cl == 'zh':
        return render_template('shopping/shopping.zh.html')
    if cl == 'ja':
        return render_template('shopping/shopping.ja.html')
    return render_template('shopping/shopping.en.html')


@page_bp.route('/locale/<lc>', methods=['GET'])
def locale(lc):
    """设置位置"""
    resp = redirect_home()
    resp.set_cookie('locale', lc, max_age=99999999)
    return resp
