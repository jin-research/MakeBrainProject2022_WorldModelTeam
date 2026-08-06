# 実機走行データの目録

`car/manage2.py` で実機を走らせるたびに1個の pickle が作られ、そのファイル名がこの台帳へ追記されます。
ファイル名を組み立てるのは `real_data_names_store.py`（[`../car/vendor_mods/real_data_names_store.py`](../car/vendor_mods/real_data_names_store.py) に同梱）で、この台帳ファイルへ追記するのは改変版 `vehicle.py:149-151` です。ファイル名は
JST の時刻からファイル名を生成し、コロンをアンダースコアに置き換えます。

`real_data_names_store.txt` が当時の実物です。`car/gets_reward_done_independent.py` は、
この一覧に並ぶ各 `.bin` を読んで reward と done を付け加えます。

## 残っている10本

| # | ファイル名 |
|---:|---|
| 1 | `./data/2022-12-09 01_57_22.034270+09_00_data.bin` |
| 2 | `./data/2022-12-09 03_02_00.308620+09_00_data.bin` |
| 3 | `./data/2022-12-09 06_26_59.310558+09_00_data.bin` |
| 4 | `./data/2022-12-09 06_45_05.618180+09_00_data.bin` |
| 5 | `./data/2022-12-09 07_02_31.496224+09_00_data.bin` |
| 6 | `./data/2022-12-09 07_54_27.903425+09_00_data.bin` |
| 7 | `./data/2022-12-09 08_28_21.261160+09_00_data.bin` |
| 8 | `./data/2022-12-09 08_33_44.780586+09_00_data.bin` |
| 9 | `./data/2022-12-09 08_52_26.356881+09_00_data.bin` |
| 10 | `./data/2022-12-09 09_07_56.232461+09_00_data.bin` |

**10本すべてが 2022年12月9日**、成果発表会当日の 01:57 から 09:07 に収集したものです。ファインチューニング自体は発表会の2日前から行いましたが、データとして残っているのはこの10本です。

## 中身

`.bin` は pickle で、段階によって項目数が変わります。

車上（`car/manage2.py` の走行終了時）は3項目です。

```text
steerings
throttles
images
```

`car/gets_reward_done_independent.py` を通した後は5項目になります。

```text
steerings
throttles
images
rewards
dones
```

## `.bin` 本体について

大容量のため、このリポジトリには含めていません。1本が80MB を超えるものもあります。動画と重みとあわせて、Release の Assets に置きます。

## 注意

`car/train_world_model.py` は、この一覧をループで回しながら、
中では固定のファイル名を開きます。ループ変数は表示されるだけで使われていません。
詳しくは [`../README.md`](../README.md) の「そのままでは動かないコード」を見てください。
