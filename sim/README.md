# シミュレーション学習

私たちは、このディレクトリのノートブックで DonkeySimLinux を Dreamer V1 に接続し、
シミュレーション走行の経験を使って学習しました。

## ファイル

| ファイル | 何をするか |
|---|---|
| `sim_final.ipynb` | 54セル。DonkeySimLinux から経験を収集し、Replay Buffer に入れて600エピソード学習し、6つの `.pth` を保存します |

## 前提

- PC 側の `sim3.7.0` 環境: [`../env/requirements-sim3.7.0.txt`](../env/requirements-sim3.7.0.txt)
- DonkeySimLinux v18.9
- `gym-donkeycar`: [`tawnkramer/gym-donkeycar@4ea670491eaef66178a1ffe3d672c7d4344c51bf`](https://github.com/tawnkramer/gym-donkeycar/tree/4ea670491eaef66178a1ffe3d672c7d4344c51bf) がベース
- Dreamer 実装: [`cross32768/Dreamer_PyTorch`](https://github.com/cross32768/Dreamer_PyTorch)（MIT © 2020 Kaito Suzuki）

ノートブック内のプレースホルダは3種あります。`<PATH_TO_DONKEY_SIM_EXECUTABLE>` は、展開した
`donkey_sim.x86_64` のパスへ置き換える必要があります。`<PATH_TO_MODEL_DIRECTORY>`（6箇所）と
`<PATH_TO_MODEL_CHECKPOINT>`（1箇所）は、保存した6モデルのディレクトリと checkpoint のパスに置き換えます
（コメント内にもあるため、実行時に必要なのは有効行のもののみ）。

## 私たちが加えた `gym-donkeycar` の改変

- `donkey_env.py` の `cam_resolution` を `(120, 160, 3)` から `(64, 64, 3)` へ変え、`headless` を追加しました。
- CTE ベースの報酬を、黄色のピクセル率×速度の報酬へ置き換えました。
- `determine_episode_over()` を、同じ色のピクセル率を使う終了判定へ差し替えました。

改変したファイルは [`gym_donkeycar_mods/`](gym_donkeycar_mods/) に置いています。
改変前の `donkey_sim_original.py`、中間の2版、最終 `donkey_sim.py`、`donkey_env.py`、
および差分があります。パッケージ全体ではなく、変更した `envs/` のファイルだけを置きました。

使うときは上記コミットの `gym-donkeycar` を取得し、`gym_donkeycar/envs/` の該当ファイルを差し替えます。

## 実行

起動例:

```bash
jupyter notebook sim_final.ipynb
```

この起動例では、引数にノートブック名を1つ渡します。
開いた後はセルを上から実行します。

学習は600エピソードで、次の6モデルを `.pth` として保存します。

```text
encoder.pth
rssm.pth
obs_model.pth
reward_model.pth
value_model.pth
action_model.pth
```

環境構築と実行時の注意は [`../docs/SETUP.md`](../docs/SETUP.md) を参照してください。

## 注意

> [!WARNING]
> このノートブックには、当時のまま残している次の箇所があります。
>
> - **`take_action_moving_average` は何もしません**。ステアリングの移動平均は、単純移動平均・
>   加重移動平均・指数平滑移動平均を試しましたが、蛇行が解消しなかったため最終版では無効にしました。
>   古い2版は関数の定義ごとコメントアウトされています。実際に呼ばれる最終版は**定義自体は生きている**が、
>   中の計算がすべてコメントアウトされ、受け取った `action` をそのまま返します。呼び出し側のコメントには
>   「ステアリングの移動平均」とありますが、実際には適用されていません。
> - `np.bool` を使う箇所があります。新しい NumPy では削除されています。
> - `torch.load()` が20箇所あります。読み込むだけで任意のコードが実行されえます。
>   **自分で作ったファイルか、出所の確かなファイルにだけ使ってください**。
> - 同名の `ReplayBuffer` が2つのセルで別々に定義されています。後のセルが前を上書きします。

> [!NOTE]
> `car/train_world_model.py:72` には `all_episodes = 600  # 学習全体のエピソード数（300ほどで, ある程度収束します）`
> というコメントが残っています。**値は 600 で、私たちが実際に回した回数もこれです**。
> 「300ほどで収束します」の部分は元コード由来の説明で、私たちが確かめた値ではありません。

## このノートブックの出所

当時のアーカイブには複数の版が残っています。ここに置いたのは最終更新が最も新しいものです。

| 当時のファイル名 | 最終更新 | 本リポジトリでの位置 |
|---|---|---|
| `2022_world_model_wrapper1 (11_23) (cleared).ipynb` | 2022-12-23 | **`sim_final.ipynb` の元ファイル** |
| `2022_world_model_wrapper2.ipynb` | 2022-09-29 | 使っていません（別コースの版） |
| `2022_world_model_from10_31.ipynb` | 2022-11-09 | 使っていません |

整理の内容は、教材由来の日本語解説の除去、MIT 帰属の明記、個人環境の絶対パスのプレースホルダ化です。
処理そのものは変えていません。
