from django import forms

from .models import Post, Comment, Document

class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ('title', 'text',)

class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('author', 'text',)

#ファイルアップロード
class DocumentForm(forms.ModelForm):
    #class Meta:「class文の持つ定義する機能」を定義する機能
    class Meta:
        #model.py定義のDocumentクラス
        model = Document
        fields = ('description', 'document', )