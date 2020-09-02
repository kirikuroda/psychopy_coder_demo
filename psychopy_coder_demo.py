#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Author: Kiri Kuroda

####################
# -- 実験の概要 -- #
####################

# ボックスをクリックすると実験が始まる。
# 毎試行、2つの都市名が表示される。
# 参加者は、どちらの都市の人口が多いかをキー押しで回答する。
# 何もせずに5秒経過すると「Hurry up!」というプロンプトが表示される。
# 回答後、正解不正解のフィードバックが1秒間表示される。
# これを4試行繰り返す。
# 都市名が左右どちらに呈示されるかは、カウンターバランスされる。
# 試行の順序はランダマイズされる。
# 各試行の終わりにデータが記録される。
# 最終的にCSVとlogが保存される。

####################
# -- ライブラリ -- #
####################

# PsychoPy 2020.2.3で検証しています

from __future__ import division
from psychopy import core, data, event, gui, logging, visual
from psychopy.hardware import keyboard
import numpy as np
import pandas as pd
import csv, os

############################
# -- ダイアログボックス -- #
############################

# ダイアログボックスを呈示し、参加者の情報を入力
subj_info = {"subj_id": "", "add_here_what_you_want": ""}
dialogue_box = gui.DlgFromDict(subj_info, order = ["subj_id", "add_here_what_you_want"])

# OKならID（subj_id）を記録して実験を進める。キャンセルなら実験を中止
if dialogue_box.OK:
    subj_id = subj_info["subj_id"]
else:
    core.quit()

####################
# -- 実験の設定 -- #
####################

# 現在日時を記録
exp_date = data.getDateStr("%Y%m%d%H%M%S")

# データファイルを保存するフォルダを作る
# フォルダがなければ作る
try:
    os.makedirs("data/csv")
    os.makedirs("data/log")
# フォルダが既にある場合は何もしない
except OSError:
    pass

# データファイルの名前を作る（ID_日付）
file_name = subj_id + "_" + exp_date
file_name_csv = os.path.join("data/csv/" + file_name + ".csv")
file_name_log = os.path.join("data/log/" + file_name + ".log")

# クイズの項目（都市名、人口）を読み込む
city = pd.read_csv("city.csv")

########################################
# -- 画面、マウス、キーボードの設定 -- #
########################################

# 画面の座標系　units = "norm"
# 画面中心が(0, 0)、X軸が-1〜+1、Y軸が-1〜+1
win = visual.Window(width = 1200, height = 900, units = "norm")
mouse = event.Mouse()
kb = keyboard.Keyboard()

####################
# -- 刺激を定義 -- #
####################

# テキスト刺激の色と日本語フォント
color_default, color_highlight = "white", "yellow"
font_ja = "ヒラギノ角ゴシック W3"

# 刺激（都市名）　textは毎試行変わるので、後で定義
city_1_text = visual.TextStim(win, font = font_ja)
city_2_text = visual.TextStim(win, font = font_ja)

# 刺激の呈示位置のカウンターバランス
# 都市名をX軸方向にどれくらいずらすか
city_nudge_x = 0.5
# 4試行のカウンターバランスをcity_posとして保存
city_pos = ["one_two", "one_two", "two_one", "two_one"]
# city_text_posを並び替える
city_pos = np.random.permutation(city_pos)

# 試行の順序をランダマイズする。trial_order: [3, 2, 0, 1]のようになる
trial_order = np.random.permutation(range(len(city)))

# キー設定
key_left, key_right = "f", "j"

# 押すべきキーの名前（課題中に呈示しておく）
# キーのテキストをY軸方向にどれくらいずらすか
key_text_nudge_y = 0.5
key_left_text = visual.TextStim(win, text = "F", pos = (-city_nudge_x, key_text_nudge_y))
key_right_text = visual.TextStim(win, text = "J", pos = (city_nudge_x, key_text_nudge_y))

# 教示を定義
inst_text = visual.TextStim(win, alignText = "left", anchorHoriz = "center")
inst_text.setText("""
Which city has a larger population?
Select the city by pressing the F or J of the keyboard.

Click "Start" and work on the task.
""")

# ボックスの線の太さ
box_line_width = 10

# 開始ボタンのボックスとテキスト
start_pos_y = -0.5 # Y軸座標
start_box = visual.Rect(win, width = 0.2, height = 0.2, pos = (0, start_pos_y), lineWidth = box_line_width)
start_text = visual.TextStim(win, text = "Start", pos = (0, start_pos_y))

# 試行間で呈示するテキスト（テキストの中身は毎試行変えるので、後で定義する）
iti_text = visual.TextStim(win)
# ITIの長さ
iti_length = 2

# どちらの都市名を選んだかを何秒呈示するか
confirmation_length = 1
# 選んだ方の都市を囲うボックスを定義
city_box_width, city_box_height = 0.5, 0.2 # ボックスのサイズ
city_box_left = visual.Rect(win,
    width = city_box_width, height = city_box_height, pos = (-city_nudge_x, 0),
    lineColor = color_highlight, lineWidth = box_line_width
)
city_box_right = visual.Rect(win,
    width = city_box_width, height = city_box_height, pos = (city_nudge_x, 0),
    lineColor = color_highlight, lineWidth = box_line_width
)

# 正解不正解のテキスト
correct_text = visual.TextStim(win, text = "Correct!")
wrong_text = visual.TextStim(win, text = "Wrong...")
feedback_length = 1

# プロンプトのテキスト
hurry_text = visual.TextStim(win, text = "Hurry up!", pos = (0, 0.8), color = color_highlight)
# time_limit秒経過したらプロンプトを出す
time_limit = 5

####################
# -- ログの設定 -- #
####################

# ログファイルの設定
file_log = logging.LogFile(file_name_log, level = logging.EXP)

##############
# -- 教示 -- #
##############

# 教示（無限ループ）
while True:

    # Startにカーソルが載ってたら黄色に
    if start_box.contains(mouse):
        start_box.setLineColor(color_highlight)
        start_text.setColor(color_highlight)
    # 載ってなければ白に
    else:
        start_box.setLineColor(color_default)
        start_text.setColor(color_default)

    # 教示とボックスを描画
    inst_text.draw()
    start_box.draw()
    start_text.draw()
    win.flip()

    # 開始ボタンがクリックされたら無限ループを抜ける
    if mouse.isPressedIn(start_box):
        break

# CSVファイルの先頭行に変数名を書き込む
with open(file_name_csv, "a", encoding = "cp932") as f:
    writer = csv.writer(f, lineterminator = "\n")
    writer.writerow([
        "subj_id", "trial", "city_1", "city_2",
        "population_1", "population_2", "choice",
        "correct_answer", "result", "rt", "key", "pos"
    ])

##############
# -- 課題 -- #
##############

# カーソルを消す
mouse.setVisible(False)

# 課題開始
for trial_index in range(len(city)):

    # 試行間のテキストを定義して描画
    iti_text.setText(str(trial_index + 1) + "/" + str(len(city)))
    iti_text.draw()
    win.flip()
    core.wait(iti_length)

    # 刺激テキストをセット
    city_1 = city["city_1"][trial_order[trial_index]]
    city_2 = city["city_2"][trial_order[trial_index]]
    city_1_text.setText(city_1)
    city_2_text.setText(city_2)

    # ついでに人口と正解も記録しておく
    population_1 = city["population_1"][trial_order[trial_index]]
    population_2 = city["population_2"][trial_order[trial_index]]
    if population_1 > population_2:
        answer = "city_1"
    else:
        answer = "city_2"

    # 刺激の位置のカウンターバランス
    if city_pos[trial_index] == "one_two":
        city_1_text.setPos((-city_nudge_x, 0))
        city_2_text.setPos((city_nudge_x, 0))
    else:
        city_1_text.setPos((city_nudge_x, 0))
        city_2_text.setPos((-city_nudge_x, 0))

    # 刺激を描画
    city_1_text.draw()
    city_2_text.draw()
    key_left_text.draw()
    key_right_text.draw()
    win.flip()

    # 回答を待ち始めた時間をresp_onsetとして記録
    resp_onset = core.Clock()

    # キー押しをリセット
    kb.getKeys([key_left, key_right], waitRelease = False)
    kb.clock.reset()

    # 回答を待つ（無限ループ）
    while True:

        # FかJのキー押しを待つ
        key_pressed = kb.getKeys(keyList = [key_left, key_right], waitRelease = False)

        # もしFかJが押されたら
        if len(key_pressed) > 0:

            # 反応時間を記録
            rt = key_pressed[0].rt

            # どっちのキーを押したかをkeyとして記録
            # カウンターバランスに応じて、どっちの都市を選んだかをchoiceとして記録
            if key_pressed[0].name == key_left:
                key = key_left
                if city_pos[trial_index] == "one_two":
                    choice = "city_1"
                else:
                    choice = "city_2"
            else:
                key = key_right
                if city_pos[trial_index] == "one_two":
                    choice = "city_2"
                else:
                    choice = "city_1"

            # 結果を記録
            if choice == answer:
                result = "correct"
            else:
                result = "wrong"

            # 選んだ方の都市名を黄色にする
            if choice == "city_1":
                city_1_text.setColor(color_highlight)
            else:
                city_2_text.setColor(color_highlight)

            # 選んだ方の都市を囲う四角を描画
            if key == key_left:
                city_box_left.draw()
            else:
                city_box_right.draw()

            # その他の刺激も描画して、1秒間呈示
            city_1_text.draw()
            city_2_text.draw()
            key_left_text.draw()
            key_right_text.draw()
            win.flip()
            core.wait(confirmation_length)

            # 刺激の色をリセットし、無限ループから抜ける
            city_1_text.setColor(color_default)
            city_2_text.setColor(color_default)
            break

        # ※time_limitを過ぎたらプロンプトを出す
        if resp_onset.getTime() > time_limit:
            city_1_text.draw()
            city_2_text.draw()
            key_left_text.draw()
            key_right_text.draw()
            hurry_text.draw()
            win.flip()

    # 正解不正解のフィードバックを呈示
    if result == "correct":
        correct_text.draw()
    else:
        wrong_text.draw()
    win.flip()
    core.wait(feedback_length)

    # CSVファイルにデータを記録
    with open(file_name_csv, "a", encoding = "cp932") as f:
        writer = csv.writer(f, lineterminator = "\n")
        writer.writerow([
            subj_id, trial_index, city_1, city_2,
            population_1, population_2, choice,
            answer, result, rt, key, city_pos[trial_index]
        ])

    # ログファイルを保存
    logging.flush()

##################
# -- 実験終了 -- #
##################

# 終わりの画面を定義
finish_text = visual.TextStim(win)
finish_text.setText("""
Finish! Thanks!
""")

# 3秒呈示してから実験終了
finish_text.draw()
win.flip()
core.wait(3)
win.close()
core.quit()
