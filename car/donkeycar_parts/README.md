# ベンダ版 Donkey Car への追加ファイル

実機で使ったベンダ版 Donkey Car（`991693552/donkeycar_jetson_nano@0656898c…`）へ、
私たちが**新しく足した**ファイルです。使うときはベンダ版の `donkeycar/parts/` へ置きます。

| ファイル | 役割 |
|---|---|
| `datastore_for_record.py` | 走行中の steering・throttle・画像を溜めるモジュール共有リスト3本。`car/manage2.py` がこれを import します |

`images_record` だけ 120×160×3 のゼロ画像1枚で初期化しています。
`MyController` がカメラより先に Vehicle へ登録されるため、最初のループで `images_record[-1]` が
参照できるようにするためです。

このファイルは標準の `datastore.py` の派生ではありません。クラスもディスク保存もありません。
リストへ溜めたものを、改変した `vehicle.py` が終了時に1個の pickle へ書き出します。
その `vehicle.py` は [`../vendor_mods/vehicle.py`](../vendor_mods/vehicle.py) に同梱しています（差分は同ディレクトリの `vehicle.py.diff`）。
