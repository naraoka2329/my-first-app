from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from .models import VideoContent, VideoTagList, VideoTagName
from django.db.models import Count

#アップロードファイル用
from django.urls import reverse, reverse_lazy
from django.views import generic
from django import forms
from django.core.files.storage import default_storage, FileSystemStorage
from django.utils import timezone
from django.conf import settings

import ffmpeg


#video/urls.pyから呼び出されるindex関数をviews.pyに定義
#render関数はHTMLのひな形を読み込んで内容を動的に生成し表示します。
# ひな形はアプリケーションのtemplateフォルダに設置します。
def index(request):
    return render(request, 'video/index.html')

#トップページではタグを多い順で関連タグとして表示し、最近投稿された順で動画を表示します。

#index関数ではページの情報や表示する動画のリストを用意します。
def index(request, page=0):
    max_page = VideoContent.objects.count() // 10
    #.values('content_id'):ビデオタグリストからIDを取得、ビデオコンテンツをアップ日順にソート、？ .order_by()[] ？
    return construct_page(request, VideoTagList.objects.values('content_id'), VideoContent.objects.order_by('-upload_date')[page*10:(page+1)*10].values(), page, max_page, 'video:index')


def construct_page(request, all_content_ids, page_contents, current_page, max_page, url_type, url_word=''):
    # page_contents(動画)に関連するタグを抜き出し、テンプレートで使えるよう整形
    contents = []
    for item in page_contents:
        tmp_dict = item
        #DBから関連タグを抜き出し(select_related('tag'))、page_contents内のcontent_idをfilterで抽出？
        tmp_dict.update({'tags': VideoTagList.objects.filter(content_id=item['id']).select_related('tag')})
        #contentsにtemp_dictを加える
        contents.append(tmp_dict)

    # all_content_idsからタグを多い順で集計し、整形する
    #annotate()：注釈をつける？
    tag_cnt = VideoTagList.objects.filter(content__in = all_content_ids).values('tag').annotate(tag_count=Count('tag')).order_by('-tag_count')[:10]
    tag_names = [VideoTagName.objects.filter(id = item.get('tag'))[0] for item in tag_cnt]
    tags = [{'name': tag_names[i].name, 'count': tag_cnt[i]["tag_count"]} for i in range(len(tag_names))]

    # ページが有効な範囲をvalidでマークを付ける
    page_list = [{'num':x, 'valid':0 <= x and x <= max_page} for x in range(current_page-5, current_page+4)]

    return render(request, 'video/index.html', {'tags': tags, 'contents': contents, 'page':{'type':url_type, 'word': url_word, 'current': current_page, 'max': max_page, 'list': page_list}})

#タグ検索
def tag(request, tag_name, page=0):
    # tag_nameからIDを探し、見つかったIDを基にタグが付いた動画をフィルタする
    tag_id = VideoTagName.objects.filter(name=tag_name).get().id
    filtered_list = VideoTagList.objects.select_related('content').filter(tag=tag_id).order_by('-content__upload_date')

    max_page = filtered_list.count() // 10

    content_list = filtered_list[page*10:(page+1)*10]
    contents = [{'id':item.content.id, 'title':item.content.title} for item in content_list]

    return construct_page(request, filtered_list.values('content_id'), contents, page, max_page, 'video:tag', tag_name)

#キーワード検索
def search(request, search_word, page=0):
    filtered_list = VideoContent.objects.filter(title__contains=search_word).order_by('-upload_date')
    max_page = filtered_list.count() // 10
    content_list = filtered_list[page*10:(page+1)*10]
    contents = [{'id':item.id, 'title':item.title} for item in content_list]

    return construct_page(request, filtered_list.values('id'), contents, page, max_page, 'video:search', search_word)

#検索窓からのPOSTを受け持つ処理
def search_post(request):
    if hasattr(request, 'POST') and 'search_text' in request.POST.keys():
        if request.POST['search_text'] != "":
            return HttpResponseRedirect(reverse('video:search', args=(request.POST['search_text'],)))

    return HttpResponseRedirect(reverse('video:index'))


#ファイルアップロード用
#VideoUploadFormクラスはアップロードページのフォームを規定します。今回はファイルのみです。 
# 正常にユーザからファイルがアップロードされた後にform_validが呼ばれます。
# content.save()によりデータベースに新しくレコードを追加され、ユニークなIDが割り当てられます。
# このIDを基に動画を保存するフォルダを作成し保存します。 
# 正常に保存されたらmake_video_thumb関数によりサムネイルを作成します。
DATA_DIR = settings.MEDIA_ROOT + 'video/'

class VideoUploadForm(forms.Form):
    file = forms.FileField()

class UploadView(generic.FormView):
    form_class = VideoUploadForm
    template_name = 'video/upload.html'

    def form_valid(self, form):
        upload_filename = form.cleaned_data["file"].name

        content = VideoContent(title=upload_filename, description="", upload_date=timezone.now(), original_name=upload_filename, filename="")
        content.save()

        try:
            storage = FileSystemStorage()
            storage.location = DATA_DIR + str(content.id)
            filename = storage.save(upload_filename, form.cleaned_data["file"])
            make_video_thumb(DATA_DIR + str(content.id) + "/" + filename, content.thumb_frame, DATA_DIR + str(content.id) + "/thumb.jpg")

        except:
            delete_video(content.id, filename)
            content.delete()
            raise

        else:
            content.filename = filename
            content.save()

            return HttpResponseRedirect(reverse('video:edit', args=(content.id,)))


#ffmpegを使用し指定されたフレームの画像を生成しています。
#もし、アップロード処理中にエラーが発生した場合はexceptが呼ばれ、
# delete_video関数により動画は削除されます。
#正常に動画をアップロードできた場合はHttpResponseRedirectにより編集ページにリダイレクトされます。
#今回はまだ作成していないのでダミーページを返すようにします。
def make_video_thumb(src_filename, capture_frame, dst_filename=None):
    probe = ffmpeg.probe(src_filename)
    video_info = next(x for x in probe['streams'] if x['codec_type'] == 'video')
    nframes = video_info['nb_frames']
    avg_frame_rate = (lambda x: int(x[0])/int(x[1])) (video_info['avg_frame_rate'].split('/'))
    start_position = int(capture_frame)/avg_frame_rate

    if dst_filename == None:
        out_target = 'pipe:'
    else:
        out_target = dst_filename

    im = (
        ffmpeg.input(src_filename, ss=start_position)
        .filter('scale', 200, -1)
        .output(out_target, vframes=1, format='image2', vcodec='mjpeg', loglevel='warning')
        .overwrite_output()
        .run(capture_stdout=True)
    )

    return im


def delete_video(content_id, video_filename):
    print('remove files at ' + str(content_id) + '/')
    storage = FileSystemStorage()
    storage.location = DATA_DIR
    storage.delete(str(content_id) + '/' + video_filename)
    storage.delete(str(content_id) + '/' + 'thumb.jpg')
    storage.delete(str(content_id) + '/')

def edit(request, content_id):
    return HttpResponse("dummy")