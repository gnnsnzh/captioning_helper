# Captioning Helper
stable-diffusion-webui用のエクステンション  
DeepDanbooruやWDv1.4 Taggerによってキャプション付けされたテキストファイルを編集できます。  
# インストール
"Extensions" →"Install from URL"タブにリポジトリのURLを入力してインストールしてください。

# 使用方法  
![ui](https://user-images.githubusercontent.com/128453054/256229427-d4435b29-955d-45ab-825b-5de92ce60fc9.png)  
Dataset Directory…データセットが入っているフォルダのパスを入力してください。  
  
・Backup  
変更前のデータを.backファイルで保持します。  
  
・Search Subdirectories  
サブディレクトリ内のデータも参照します。  
  
・Remove Duplicate Tags  
同名タグが複数存在する場合、1つにまとめます。  

・Remove Unnecessary Tags  
重複する概念のタグを削除し、より詳細なタグを残します。  
重複するワードを検出してるわけではなく、手動でリスト化したタグを参照しています。  
削除対象のタグはtag_config_data.pyを参照してください。  
例1:black jacket, jacket → black jacketのみが残ります  
例2:swim suit, bikini, red bikini → red bikiniのみが残ります。  

・Merge Tags  
末尾が同じタグをマージします  
例:long hair, black hair → long black hair  
※soloのタグがあるファイルのみ実行されます。  
※作品名タグは無視されます。  
※Remove Unnecessary Tagsとの併用を推奨します。  

・Dropout Tags  
少ないプロンプトで学習が反映されやすくなるかもしれません。caption dropoutが使用できない場合などに使ってください。  
スライダーでDropout機能が適応される確率を操作できます。0で無効になります。  
適応された場合以下のタグのみ残ります。  
1girl, 2girls, 3girls, 4girls, 5girls, 6+girls, 1boy, 2boys, 3boys, 4boys, 5boys, 6+boys, solo,   
indoors, outdoors, simple background, standing, sitting, from side, scenery, closed eyes, animal, sky, city, no humans  

・Replace Hair Color,Replace Eye Color  
キャラ学習用
チェックボックスをonにすることでNew Hair Color,New Eye Colorで選択したタグが適応されます。  
Hair Colorタグ,Eye Colorタグを選択したタグに統一します。  
キャラ学習用のデータセットを作る際に使ってます。  

・Tag Replacements  
タグの置換を行います  
例: 1girl:woman, hat:cap  

・Additional tags  
入力したタグを先頭に追加します。複数入力可能です。  
  
・Exclude tags  
入力したタグを削除します。複数入力可能です。
