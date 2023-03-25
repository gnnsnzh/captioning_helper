# Captioning Helper
stable-diffusion-webui用のエクステンション  
DeepDanbooruやWDv1.4 Taggerによってキャプション付けされたテキストファイルを編集できます。  
コードの一部は匿名で配布されていたスクリプトを参考にしています。  
問題があればお伝えください。  
# インストール
"Extensions" →"Install from URL"タブにリポジトリのURLを入力してインストールしてください。

# 使用方法  
Dataset Directory…データセットが入っているフォルダのパスを入力してください。  
  
Backup…変更前のデータを.backファイルで保持します。  
  
Search Subdirectories…サブディレクトリ内のデータも参照します。  
  
Remove Duplicate Tags…同名タグが複数存在する場合、1つにまとめます。  

・Remove Unnecessary Tags  
重複する概念のタグを削除し、より詳細なタグを残します。  
重複するワードを検出してるわけではなく、手動でリスト化したタグを参照しています。  
削除対象のタグはtag_config_data.pyを参照してください。  
例1:black jacket, jacket → black jacketのみが残ります  
例2:swim suit, bikini, red bikini → red bikiniのみが残ります。  
  
・Replace Hair Color,Replace Eye Color  
チェックボックスをonにすることでNew Hair Color,New Eye Colorで選択したタグが適応されます。  
Hair Colorタグ,Eye Colorタグを選択したタグに統一します。  
キャラ学習用のデータセットを作る際に使ってます。  
  
・Additional tags  
入力したタグを先頭に追加します。複数入力可能です。  
  
・Exclude tags  
入力したタグを削除します。複数入力可能です。
