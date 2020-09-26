from django.db import models

#動画サイトに必要なもの管理ID、タイトル、説明文、
# タグ情報、アップロード日、ファイル名
#タグ情報は複数つけることができます。
# また、複数の動画に同じタグが付けられます。
#  これは動画の管理IDとタグの管理IDを紐づけることで実現します

class VideoContent(models.Model):
    title = models.CharField(max_length=200)#タイトル
    description = models.TextField()#解説、説明
    upload_date = models.DateTimeField()
    original_name = models.CharField(max_length=200)
    filename = models.CharField(max_length=200, default="")
    thumb_frame = models.IntegerField(default=0)

class VideoTagName(models.Model):
    name = models.CharField(max_length=200, default="")

class VideoTagList(models.Model):
    content = models.ForeignKey(VideoContent, on_delete=models.CASCADE)
    tag = models.ForeignKey(VideoTagName, on_delete=models.CASCADE)