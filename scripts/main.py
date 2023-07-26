import gradio as gr
from modules import script_callbacks
import modules.shared as shared
import glob
import os
import shutil
import re
import sys
import random

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tag_config_data import tag_config_data
from save_tags import save_tags
from colors import hair_colors, eye_colors
from hair_style import hair_style

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

def dropout_tags(tags, dropout_probability):
    # dropout_probability以下の場合、タグの削除をスキップ
    if random.random() > dropout_probability:
        return tags, []

    # save_tagsとhair_colorsを結合
    allowed_tags = save_tags + hair_colors
    # allowed_tagsにないタグを削除
    new_tags = [tag for tag in tags if tag in allowed_tags]
    removed_tags = set(tags) - set(new_tags)
    return new_tags, removed_tags

def remove_duplicate_tags(tags):
    seen = set()
    unique_tags = [tag for tag in tags if not (tag in seen or seen.add(tag))]
    removed_tags = set(tags) - set(unique_tags)
    return unique_tags, removed_tags

def replace_tags(tags, replacements):
    replacements_dict = {old_new.split(":")[0]: old_new.split(":")[1] for old_new in replacements.split(", ")}
    replaced_tags = [replacements_dict.get(tag, tag) for tag in tags]
    return replaced_tags

def clean_tags(tags):
    original_tags = tags  # 変更前のタグを保存

    if 'girls' in tags or 'boys' in tags:
        # 髪の色に関するタグが2つ以上存在する場合、それらをすべて削除
        hair_color_tags = [color for color in hair_colors if color in tags]
        if len(hair_color_tags) > 1:
            for color in hair_color_tags:
                color_pattern = re.compile(f'(, {color}, |^{color}, |, {color}(, )?)')
                tags = color_pattern.sub(", ", tags)

        # 目の色に関するタグが2つ以上存在する場合、それらをすべて削除
        eye_color_tags = [color for color in eye_colors if color in tags]
        if len(eye_color_tags) > 1:
            for color in eye_color_tags:
                color_pattern = re.compile(f'(, {color}, |^{color}, |, {color}(, )?)')
                tags = color_pattern.sub(", ", tags)

        # 髪型に関するタグが2つ以上存在する場合、それらをすべて削除
        hair_style_tags = [style for style in hair_style if style in tags]
        if len(hair_style_tags) > 1:
            for style in hair_style_tags:
                style_pattern = re.compile(f'(, {style}, |^{style}, |, {style}(, )?)')
                tags = style_pattern.sub(", ", tags)

    # 先頭と末尾の", "を削除
    tags = tags.strip(", ")

    cleaned_tags = tags  # 変更後のタグを保存

    return original_tags, cleaned_tags  # 変更前と変更後のタグを返す
    
def merge_tags(tags):
    tag_dict = {}
    special_tags = {}

    if "solo" not in tags:
        return tags, "solo tag not found: merge tags skipped"

    for tag in reversed(tags):
        # "\"を含むタグを無視し、特別なタグとして保存
        if "\\" in tag:
            special_tags[tag] = tag
            continue

        *first_parts, last_part = tag.split(' ')
        base_tag = ' '.join(first_parts), last_part  # タグを前半と後半に分ける
        if base_tag[1] in tag_dict:
            tag_dict[base_tag[1]] = f"{base_tag[0]} {tag_dict[base_tag[1]]}"
        else:
            tag_dict[base_tag[1]] = tag

    merged_tags = list(tag_dict.values())
    merged_tags += list(special_tags.values())

    merged_tags = merged_tags[::-1]

    return merged_tags, "merge tags: done"

def process_tags(target_dir, remove_unnecessary_tags, remove_duplicate_tags_option, replace_hair, replace_eyes, new_hair_color, new_eye_color, additional_tags, exclude_tags, clean_tags_option, tag_replacements, merge_tags_option, dropout_tags_option):
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

        if dropout_tags_option:
            old_tags = tags[:]
            tags, removed_tags = dropout_tags(tags, dropout_tags_option)
            if removed_tags:
                logs += f"\nドロップアウトタグ: {', '.join(removed_tags)}"

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

        if tag_replacements:
            old_tags = new_tags[:]
            new_tags = replace_tags(new_tags, tag_replacements)
            for old_tag, new_tag in zip(old_tags, new_tags):
                if old_tag != new_tag:
                    logs += f"\n置換: {old_tag} → {new_tag}"

        if remove_duplicate_tags_option:
            old_tags = new_tags[:]
            new_tags, removed_tags = remove_duplicate_tags(new_tags)
            if removed_tags:
                logs += f"\n重複タグを削除: {', '.join(removed_tags)}"

        if clean_tags_option:
            original_tags, newtxt = clean_tags(newtxt)
            new_tags = newtxt.split(", ")  # クリーニングしたタグを新しいタグリストに適用
            logs += f"\nClean Tags:\nOriginal: {original_tags}\nCleaned: {newtxt}"

        if merge_tags_option:
            new_tags, merge_tags_result = merge_tags(new_tags)
            if merge_tags_result is not None:
                logs += f"\n{merge_tags_result}"
        
        newtxt = ", ".join(new_tags)  # マージしたタグを新しいテキストに適用
  
     # タグの先頭と末尾にある余分なカンマとスペースを削除
        newtxt = newtxt.strip(", ").strip(",")
    
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

def main(target_dir, backup, search_subdirs, remove_unnecessary_tags, remove_duplicate_tags_option, replace_hair, replace_eyes, new_hair_color, new_eye_color, additional_tags, exclude_tags, clean_tags_option, tag_replacements, merge_tags_option, dropout_tags_option):
    global backup_flag
    backup_flag = backup
    global search_subdirectories
    search_subdirectories = search_subdirs

    process_tags(target_dir, remove_unnecessary_tags, remove_duplicate_tags_option, replace_hair, replace_eyes, new_hair_color, new_eye_color, additional_tags, exclude_tags, clean_tags_option, tag_replacements, merge_tags_option, dropout_tags_option)

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
                    clean_tags_option = gr.Checkbox(label="Clean Tags（複数人がいる場合、髪型、髪色、目の色のタグを削除します。）")
                    merge_tags_option = gr.Checkbox(label="Merge Tags（末尾が同じタグをマージします。例:long hair, black hair → long black hair）")
                    dropout_tags_option = gr.Slider(minimum=0.0, maximum=1.0, default=0.0, step=0.1, label="・Dropout Tags(最低限のタグのみ残します。0で無効)")
                    replace_hair = gr.Checkbox(label="Replace Hair Color（Hair Colorタグを選択した色に統一します）")
                    new_hair_color = gr.Dropdown(choices=hair_colors, label="New Hair Color")
                    replace_eyes = gr.Checkbox(label="Replace Eye Color（Eye Colorタグを選択した色に統一します）")
                    new_eye_color = gr.Dropdown(choices=eye_colors, label="New Eye Color")
                    tag_replacements = gr.Textbox(label="Tag Replacements(タグの置換を行います)", placeholder="1girl:woman, hat:cap, ...")
                    additional_tags = gr.Textbox(label="Additional tags(先頭から順にタグを追加します)", placeholder="例:cat, dog")
                    exclude_tags = gr.Textbox(label="Exclude tags(入力されたタグを削除します)", placeholder="例:tree, sky")

        run_button = gr.Button(elem_id="process_tags_btn", label="Process Tags", variant='primary')
        
        run_button.click(
            fn=main,
            inputs=[target_dir, backup, search_subdirs, remove_unnecessary_tags, remove_duplicate_tags_option, replace_hair, replace_eyes, new_hair_color, new_eye_color, additional_tags, exclude_tags, clean_tags_option, tag_replacements, merge_tags_option, dropout_tags_option],
            outputs=[]
        )

    return (ch_helper_interface, "Captioning Helper", "ch_helper_interface"),

script_callbacks.on_ui_tabs(on_ui_tabs)