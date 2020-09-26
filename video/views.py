from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect

#video/urls.pyから呼び出されるindex関数をviews.pyに定義
#render関数はHTMLのひな形を読み込んで内容を動的に生成し表示します。
# ひな形はアプリケーションのtemplateフォルダに設置します。
def index(request):
    return render(request, 'video/index.html')