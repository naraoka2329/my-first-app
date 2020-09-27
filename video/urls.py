from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'video'
urlpatterns = [
    path('', views.index, name='index'),
    path('<int:page>', views.index, name='index'),
    path('tag/<str:tag_name>', views.tag, name='tag'),
    path('tag/<str:tag_name>/<int:page>', views.tag, name='tag'),
    path('search/', views.search_post, name='search'),
    path('search/<str:search_word>', views.search, name='search'),
    path('search/<str:search_word>/<int:page>', views.search, name='search'),
#    path('watch/<int:content_id>/', views.watch, name='watch'),
    path('upload/', views.UploadView.as_view(), name='upload'),
#   path('edit/<int:content_id>', views.edit, name='edit'),
#    path('edit/<int:content_id>/thumb/<int:frame>', views.thumb, name='thumb'),
#   path('delete/<int:pk>', views.DeleteView.as_view(), name='delete'),
#    path('update/<int:content_id>', views.update, name='update'),
#    path('update/tag/<int:content_id>', views.update_add_tag, name='update_add_tag'),
#    path('update/tag/<int:content_id>/<str:tag_name>', views.update_remove_tag, name='update_remove_tag'),

]
#インデックス("/")のみのURLを取り扱い、views.pyに記載された
# index関数を呼び出して処理します。
# name='index'は後ほど'index'という文字からURLを生成できる
# ようするため設定します。 
# また、video/urls.pyをルートのURL設定に反映する必要があります。

#以下のページがあるとよさそう
#トップページ
#検索結果
#アップロードページ
#動画情報編集ページ
#動画削除ページ
#視聴ページ