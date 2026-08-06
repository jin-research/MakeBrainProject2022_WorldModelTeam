# 実機データによるモデル更新

私たちは、このディレクトリのノートブックで、実機走行後のデータ処理と
PC 上での Dreamer モデル更新を行いました。

## ファイル

| ファイル | 何をするか |
|---|---|
| `real_final.ipynb` | 49セル。実機の pickle に reward と done を付け、Replay Buffer へ投入してモデルを更新し、6つの `.pth` を保存して `.npy` へ変換します |

このノートブックはカメラやモーターを制御しません。
実機での推論、駆動、データ収集は [`../car/`](../car/) のコードが担当します。

## 前提

- PC 側の環境: [`../env/requirements-rl3.7.0.txt`](../env/requirements-rl3.7.0.txt)
- 入力は実機で保存した pickle

reward / done の追加後、pickle は次の5項目をこの順で持ちます。

```text
steerings
throttles
images
rewards
dones
```

## 当時の reward と done

基準にした RGB 範囲は `R: 210–240 / G: 170–200 / B: 110–140` で、
`extention_color = 10` により判定範囲を上下へ10（±10）広げました。

done でないフレームの報酬は次の式です。done のフレームでは `-1.0` としました。

```text
reward = (all_square_pixel_percentage / 5) * (throttle / 10)
```

指定色の割合が `0.1%` 未満のとき `count_to_dead` を増やし、
`count_to_dead >= 15*2` になったフレームを done としました。

当時のコードは分母を次のように計算します。

```python
all_square_pixel = sum(image.shape) / 3
```

64×64画像では `131 / 3 ≈ 43.67` となり、実際の総画素数4096ではありません。
私たちは、当時この計算で動かした事実として残しています。

## 実行

起動例:

```bash
jupyter notebook real_final.ipynb
```

この起動例では、引数にノートブック名を1つ渡します。
開いた後はセルを上から実行します。**ただし下記の警告を先に読んでください**。

> [!CAUTION]
> **このノートブックは、読み込んだ pickle ファイルを削除することがあります。必ず複製に対して実行してください**。
>
> 実機データを読む処理は、`pickle.load()` が `EOFError` になったときに `os.remove(data)` で
> 入力ファイルを削除し、同じ名前を `'wb'` で開き直します。走行データが途中で切れていた場合、
> 元のファイルは失われます。続く復旧処理も書込み専用で開いたファイルから読もうとするため動きません。
>
> 実行する前に、元の `.bin` を別ディレクトリへ複製してください。

> [!WARNING]
> このノートブックには、当時のまま残している次の箇所があります。
>
> - `os.mkdir(..., exist_ok=True)` が6箇所あります（重み変換のセル）。標準の `os.mkdir()` は `exist_ok` を受け取らないため
>   `TypeError` になります。`os.makedirs()` が正しいです。
> - `np.bool` を使う箇所があります。新しい NumPy では削除されています。
> - `pickle.load()` が26箇所、`torch.load()` が17箇所あります。どちらも読み込むだけで任意のコードが
>   実行されえます。**自分で作ったファイルか、出所の確かなファイルにだけ使ってください**。
> - `save_path` を出力する箇所があります。この変数はこのノートブック内で定義されていないため
>   `NameError` になります。

更新後は6つの `.pth` を保存し、Jetson Nano へ渡すため、各モデルの重みを
`.npy` へ変換します。環境、データ形式、重み変換の詳細は
[`../docs/SETUP.md`](../docs/SETUP.md) を参照してください。

ノートブック内の `<PATH_TO_DONKEY_SIM_EXECUTABLE>` はシミュレータ実行ファイルのパス、
`<PATH_TO_REAL_DATA_NAMES_STORE>` は走行データ台帳のパスへ置き換えます。
当時の台帳の実物は [`../data/real_data_names_store.txt`](../data/real_data_names_store.txt) にあります。

> [!NOTE]
> **`take_action_moving_average` は何もしません**。引数をそのまま返します。
> ステアリングの移動平均は蛇行の解消に至らなかったため、最終版では無効にしました。
> 呼び出し側のコメントには「ステアリングの移動平均」と書いてありますが、実際には適用されていません。

## このノートブックの出所

| 当時のファイル名 | 最終更新 | 本リポジトリでの位置 |
|---|---|---|
| `2022_world_model_1208_realcartest.ipynb` | 2022-12-09 | **`real_final.ipynb` の元ファイル** |
| `2022_world_model_jetsontest.ipynb` | 2022-10-21 | 使っていません（Jetson 側の別処理） |

整理の内容は `sim/` と同じで、処理そのものは変えていません。
