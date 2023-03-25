import gradio as gr
from modules import script_callbacks
import modules.shared as shared
import glob
import os
import shutil
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tag_config_data import tag_config_data
from colors import hair_colors, eye_colors

# 元のファイルを残す場合はTrue
backup_flag = False
# サブディレクトリの読み込みを行うかどうか
search_subdirectories = False

configs = tag_config_data

config_keys = configs.keys()

def replace_color(tags, source_colors, target_color):
    replaced_tags = []
    for tag in tags:
        if tag in source_colors:
            replaced_tags.append(target_color)
        else:
            replaced_tags.append(tag)
    return replaced_tags

def remove_duplicate_tags(tags):
    seen = set()
    unique_tags = [tag for tag in tags if not (tag in seen or seen.add(tag))]
    removed_tags = set(tags) - set(unique_tags)
    return unique_tags, removed_tags

def process_tags(target_dir, remove_unnecessary_tags, remove_duplicate_tags_option, replace_hair, replace_eyes, new_hair_color, new_eye_color, additional_tags, exclude_tags):
    filelist = glob.glob(f"{target_dir}/*.txt")
    if search_subdirectories:
        filelist += glob.glob(f"{target_dir}/**/*.txt", recursive=True)

    backup_file_pattern = re.compile(r'\.back\d+$')  # 追加

    for filepath in filelist:
        if backup_file_pattern.search(os.path.splitext(filepath)[0]):
            continue

        with open(filepath, "r", encoding="utf8") as txt:
            content = txt.read()

        tags = content.split(", ")
        dellist = []
        logs = f"処理ファイル: {filepath}"

        if remove_unnecessary_tags:
            for tag in tags:
                if tag in config_keys:
                    for v in configs[tag]:
                        if not v in tags:
                            continue
                        dellist.append(tag)
                        logs += f"\n詳細タグ:{v} / 不要タグ:{tag}"
                        break

        newtxt = ""
        for tag in tags:
            if tag in dellist:
                continue
            if newtxt == "":
                newtxt = f"{tag}"
            else:
                newtxt = f"{newtxt}, {tag}"

        new_tags = newtxt.split(", ")

        if replace_hair or replace_eyes:
            if replace_hair:
                old_tags = new_tags[:]
                new_tags = replace_color(new_tags, hair_colors, new_hair_color)
                for old_tag, new_tag in zip(old_tags, new_tags):
                    if old_tag != new_tag:
                        logs += f"\n置換: {old_tag} → {new_tag}"
            if replace_eyes:
                old_tags = new_tags[:]
                new_tags = replace_color(new_tags, eye_colors, new_eye_color)
                for old_tag, new_tag in zip(old_tags, new_tags):
                    if old_tag != new_tag:
                        logs += f"\n置換: {old_tag} → {new_tag}"

        if additional_tags:
            additional_tags_list = additional_tags.split(", ")
            new_tags = additional_tags_list + new_tags
            logs += f"\n追加タグ: {', '.join(additional_tags_list)}"

        if exclude_tags:
            exclude_tags_list = exclude_tags.split(", ")
            old_tags = new_tags[:]
            new_tags = [tag for tag in new_tags if tag not in exclude_tags_list]
            removed_tags = set(old_tags) - set(new_tags)
            if removed_tags:
                logs += f"\n削除タグ: {', '.join(removed_tags)}"
        
        if remove_duplicate_tags_option:
            old_tags = new_tags[:]
            new_tags, removed_tags = remove_duplicate_tags(new_tags)
            if removed_tags:
                logs += f"\n重複タグを削除: {', '.join(removed_tags)}"

        newtxt = ", ".join(new_tags)

        print(logs)
        if backup_flag:
            i = 0
            while True:
                backup_path = f"{os.path.splitext(filepath)[0]}.back{i}"
                if os.path.isfile(backup_path):
                    i += 1
                    continue
                break
            shutil.copyfile(filepath, f"{os.path.splitext(filepath)[0]}.back{i}")

        with open(filepath, "w", encoding="utf8") as txt:
            txt.write(newtxt)
            txt.close()

def main(target_dir, backup, search_subdirs, remove_unnecessary_tags, remove_duplicate_tags_option, replace_hair, replace_eyes, new_hair_color, new_eye_color, additional_tags, exclude_tags):
    global backup_flag
    backup_flag = backup
    global search_subdirectories
    search_subdirectories = search_subdirs

    process_tags(target_dir, remove_unnecessary_tags, remove_duplicate_tags_option, replace_hair, replace_eyes, new_hair_color, new_eye_color, additional_tags, exclude_tags)

def on_ui_tabs():
    with gr.Blocks() as ch_helper_interface:
        with gr.Row(equal_height=True):
            with gr.Column(variant='panel'):
                with gr.Column(variant='panel'):
                    target_dir = gr.Textbox(label="Dataset Directory", placeholder="C:\Dataset")
                    backup = gr.Checkbox(label="Backup（元のテキストファイルをを.bakファイルで保持します）")
                    search_subdirs = gr.Checkbox(label="Search Subdirectories（サブディレクトリ内のデータも参照します）")
                    remove_unnecessary_tags = gr.Checkbox(label="Remove Unnecessary Tags（重複概念タグを削除し、より詳細なタグを残します。例:black jacket, jacketのタグが存在する場合black jacketのみが残ります。）")
                    remove_duplicate_tags_option = gr.Checkbox(label="Remove Duplicate Tags（同名タグが複数存在する場合、1つにまとめます）")
                    replace_hair = gr.Checkbox(label="Replace Hair Color（New Hair Colorで選択したタグを適応します。Hair Colorタグを統一します）")
                    replace_eyes = gr.Checkbox(label="Replace Eye Color（New Eye Colorで選択したタグを適応します。Eye Colorタグを統一します）")
                    new_hair_color = gr.Dropdown(choices=hair_colors, label="New Hair Color")
                    new_eye_color = gr.Dropdown(choices=eye_colors, label="New Eye Color")
                    additional_tags = gr.Textbox(label="Additional tags(先頭から順にタグを追加します)", placeholder="例:cat, dog")
                    exclude_tags = gr.Textbox(label="Exclude tags(入力されたタグを削除します)", placeholder="例:tree, sky")

        run_button = gr.Button(elem_id="process_tags_btn", label="Process Tags", variant='primary')
        
        run_button.click(
            fn=main,
            inputs=[target_dir, backup, search_subdirs, remove_unnecessary_tags, remove_duplicate_tags_option, replace_hair, replace_eyes, new_hair_color, new_eye_color, additional_tags, exclude_tags],
            outputs=[]
        )

    return (ch_helper_interface, "Captioning Helper", "ch_helper_interface"),

script_callbacks.on_ui_tabs(on_ui_tabs)