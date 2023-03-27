from django.conf import settings
from django.core.paginator import Paginator
from django.shortcuts import render

from .models import Article, Category


def portal(request):
    try:
        q_page = request.GET.get('page', 1)

        category = Category.objects.published().get(full_path=request.path)
        articles = category.articles.published().order_by('-pk')
        p = Paginator(
            articles, settings.PAGINATOR_ARTICLE_PER_PAGE).get_page(q_page)
        return render(request, 'portal/portal.html',
                      context={'category': category,
                               'articles': p.object_list,
                               'p': p})

    except Category.DoesNotExist:
        try:
            article = Article.objects.published().get(full_path=request.path)
            return render(request, 'portal/article.html',
                          context={'article': article})
        except Article.DoesNotExist:
            pass
    return render(request, 'portal/portal.html')
