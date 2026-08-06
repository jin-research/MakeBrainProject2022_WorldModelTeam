# ベンダ版 Donkey Car への改変

Jetson Nano "Nao" では、XiaoR GEEK が配布するベンダ版 Donkey Car（`991693552/donkeycar_jetson_nano`）を土台に、
私たちがファイルを書き換えて使いました。ここにはその**改変後のファイルそのもの**と、ベンダ素との差分を置いています。

`car/manage2.py` を動かすには、ここのファイルをベンダ版の対応する場所へ置き換える必要があります。


## ライセンス

上流は MIT です（`third_party/donkeycar_jetson_nano/LICENSE`、Copyright (c) 2017 Will Roscoe）。
ここのファイルはその派生物なので、同じ MIT の条件で扱ってください。

**ベンダの `.so` 3本、`XiaoRGEEK.jpg`、`INIT_LED.py` は商業利用が禁止されているため同梱していません**。
キットを購入した方の手元にあるものを使ってください。

## ファイル

| ファイル | ベンダ素との差 | 何を変えたか |
|---|---:|---|
| `vehicle.py` | +115 / -3 | 走行ループで steering / throttle / 画像を共有リストへ貯め、終了時に pickle へ書き出す処理と、**色ベースの dead 判定**の追加（下記） |
| `parts/camera.py` | +57 / -111 | `CSICamera` の追加と BGR→RGB 変換。ベンダの汎用カメラ群の削除 |
| `parts/keras.py` | +12 / -1 | 正弦値で steering / throttle を上書き（Dreamer 統合前のモーター単体確認） |
| `parts/web_controller/web.py` | +12 / -5 | IP の固定と HTTPS 化 |
| `parts/web_controller/templates/base.html` | +3 / -5 | 表示名を XR-F1 へ変更。外部 JS / CSS の `integrity`（SRI）の削除 |
| `parts/datastore.py` | +8 / -2 | `TubWriter.run()` の入力数 `assert` のコメントアウトと、確認用 `print` の追加 |
| `real_data_names_store.py` | 新規 | 保存先ファイル名を日本標準時から組み立て（`:` は `_` へ置換） |
| `vehicle_12071852_before_dead_flag.py` | 新規 | **dead 判定を入れる前の `vehicle.py`**。当時の作業途中の版 |

差分は `*.diff` に入れています。`diff -u --strip-trailing-cr` で作りました（改行コードの違いを除いています）。

`parts/datastore_for_record.py` は [`../donkeycar_parts/`](../donkeycar_parts/) にあります。

### `vehicle.py` の dead 判定（走行を15秒止める）

`vehicle.py:181-214` の `determine_episode_over()` は、毎ループ、画像の色（RGB 基準±`extention_color=10`）から
コース逸脱を数えます。`count_to_dead >= 15*2` に達すると action を `[0,0]` にし、
**`for i in range(15): time.sleep(1)` で15秒間ループを止めます**（`:205-208`）。
実車がコースを外れたまま走り続けるのを防ぐための挙動ですが、**走行中に突然15秒停止する**ことになるので、
再利用する場合は先にこの部分を確認してください。分母には他と同じ `sum(image.shape) / 3` の式（`:191`）を使っています。

> [!IMPORTANT]
> `car/manage2.py:16` は `from donkeycar.parts.camera import CSICamera` を実行します。
> **`CSICamera` はベンダ版に存在しません**（ここの `parts/camera.py` で追加したものです）。
> `manage2.py` の import は上から
> `datastore` → `actuator` → `camera`（16行目）→ `datastore_for_record`（20行目）
> の順なので、`camera.py` を置き換えていないと **20行目より先に16行目で ImportError になります**。

> [!CAUTION]
> `parts/web_controller/web.py:94-96` は、同じディレクトリの `server.crt` と `server.key` を読んで HTTPS を有効にします。
> **`server.key` は秘密鍵なので同梱していません**。使う場合は自分で生成してください。
>
> `base.html` では外部 JS / CSS の `integrity` 属性が削除されています。当時なぜ消したのかの記録は残っていません。
> そのまま使うと、配信元が改ざんされた場合に検知できません。

> [!NOTE]
> `vehicle.py:15` に `#sys.path.append("/home/xiaor/mycar/...")` というコメント行があります。
> `xiaor` はベンダ既定のアカウント名です。当時の記録としてそのまま残しています。
