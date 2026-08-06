---
layout: default
title: 環境・実行記録
---

# 世界モデルカーの環境・実行記録

この文書は、私たちが2022年に使った環境、当時の操作ログ、現存コードから復元した処理順をまとめたものです。完成済みの再現手順ではありません。

> [!CAUTION]
> この文書には、2022年当時の `fdisk` ログ、実車のモーター駆動、pickleの同名上書き、データ削除を含むコードが載っています。そのまま現在の環境で実行しないでください。

---

## 0. 全体の処理

| 当時の処理 | 場所 |
|---|---|
| DonkeySimLinuxとDreamerによる初期学習 | GPU搭載PC |
| 学習済み重みの `.pth` から `.npy` への変換 | PC |
| `.npy` から実機用 `.pth` への復元 | Jetson Nano |
| カメラ画像からsteeringとthrottleを生成 | Jetson Nano "Nao" |
| 実機走行データをpickleへ保存 | Jetson Nano "Nao" |
| rewardとdoneを後付け | 独立スクリプト |
| Replay Bufferへの投入とモデル更新 | PC |

私たちは、Jetson Nano（Jassy 版）だけでモデルを一から作るとメモリが不足することを確認しました。Jetson Nanoは推論とデータ収集を担当しました。PCは初期学習とモデル更新を担当しました。

実機の結果は2段階でした。

1. シミュレーション学習済みモデルの転移走行では、十分な速度でサーキットを走行しました。
2. 実機データによるファインチューニングを重ねた後も、報酬設定の見直しなどにより、直線・Lカーブ・S字カーブでの自動走行を実現しました。ただし、シミュレーション環境で作ったモデルほどの速度は出ず、カーブに対処できずコース外へ進む試行もありました。ファインチューニングの試行回数は一桁でした。

> [!NOTE]
> 当時の `.npy` から `.pth` への復元には `pull_weight.py` を使いました。このスクリプトは `car/pull_weight.py` に置いています。

---

## 1. 機材

### 1.1 学習用 PC

| 項目 | 値 |
|---|---|
| PC | ROG Zephyrus G15 GA503QR（端末記録のホスト名 `mbp-ROG-Zephyrus-G15-GA503QR` による）|
| CPU | Ryzen 9 |
| GPU | GeForce RTX 3070 |
| GPUメモリ表示 | 8192 MiB |

### 1.2 車体と周辺機器

| 機材 | 型番・記録 | 価格・入手形態 |
|---|---|---:|
| カーキット | XiaoR GEEK Donkey Car XR-F2 for Nvidia Jetson Nano kit、Amazon `B096MFLZ91` | 78,900円 |
| SDカード | SanDisk Extreme `SDSDXV5-128G-GHENN`、128GB SDXC Class 10、UHS-I U3、V30 | 3,680円 |
| 無線LAN子機 | TP-Link `TL-WN725N` | 727円 |
| 無線LAN | Intel 8265（購入品リストと「検討」の両方に記録があり、最終形は特定できません） | - |
| ACアダプター | SUCCUL 5V4A | 借用（1,580円は検討時の記録） |
| カメラ候補 | SainSmart IMX219、8MP、160度FoV、3280×2464 | 購入記録あり |
| 別のカメラ記録 | Raspberry Pi Camera V2 | 備品DBにあり |
| モバイルバッテリー | - | 借用 |

キットには、車体、Jetson Nano、DCモーター、サーボモーター、カメラ、モータードライバーを含む拡張ボードがありました。

購入時のリンクと注文日は、[リポジトリの README](https://github.com/jin-research/MakeBrainProject2022_WorldModelTeam/blob/main/README.md) の「機材と環境」にまとめています。

### 1.3 コース材料

| 材料 | 品番・寸法 | 記録額 |
|---|---|---:|
| 黒い背景布 | 3m×6m | 3,810円 |
| 白色テープ2ロール | ニトムズ 布粘着テープSE `J5445` | 766円 |
| 黄色テープ | ニトムズ カラー布粘着テープSE `J5442`、50mm×25m | 284円 |
| 合計 |  | 4,860円 |

当時の記録には、別案として `黒 300 x 360`（3m×3.6m）3,260円 も並記されています。合計 4,860円 に入っているのは 3m×6m の方です。参考にしたのは DIYRobocars Standard Track です。制作期間はおよそ1日でした。

線幅は、テープの幅からみて50mmです。

---

## 2. PC 側の環境

### 2.1 当時確認した値

| 項目 | 値 |
|---|---|
| OS | Ubuntu 20.04.4 LTS |
| カーネル / アーキテクチャ | 5.15.0-41-generic / x86_64 |
| GPUドライバ | 510.73.05（2022-06-17 の `nvidia-smi` 出力）|
| `nvidia-smi` のCUDA表示 | 11.6 |
| CUDA Toolkit | release 11.1, V11.1.74 |
| Python | 3.7.0系 |
| 最終的な環境管理 | pyenv + virtualenv |
| Dreamer / RL環境 | `rl3.7.0` |
| シミュレータ環境 | `sim3.7.0` |
| conda配布物 | Miniforge |

`nvidia-smi` のCUDA 11.6はドライバ側の表示です。`nvcc -V` の11.1はCUDA Toolkitの記録です。

CUDA Toolkit は途中で変わっています。2022年6月1日の記録には、当時の `nvcc -V` の出力が残っています。

```text
nvcc: NVIDIA (R) Cuda compiler driver
Copyright (c) 2005-2021 NVIDIA Corporation
Built on Thu_Nov_18_09:45:30_PST_2021
Cuda compilation tools, release 11.5, V11.5.119
Build cuda_11.5.r11.5/compiler.30672275_0
```

CUDA Toolkit は **11.5（2022年6月）→ 11.1（稼働時）** と下がっています。Ubuntu の入れ直しに伴うもので**、11.1 が最終形**です。

### 2.2 Ubuntu

私たちが使用したPCは当初Windowsでした。まず **Ubuntu 22.04** を入れ、最終的に **Ubuntu 20.04系** へ入れ直しました。当時の報告書に経緯が残っています。

> 1. 機械学習用のライブラリの充実度を加味し、Ubuntu(22.04)を用いることに決定し、必要なライブラリなどを複数人で分担して調査した
> 2. Jetson Nanoと開発環境を統一するために、環境の複製が容易とされるDockerを用いて仮想環境を構築しようとした
> 3. しかしDockerのインストールや、機械学習を行う上での必須モジュールであるCUDAやcuDNNなどのバージョンが難航したため、メンバーと協力して解決策を調査した
> 4. 最終的には、有識者の手助けを得つつ学習用PCにUbuntu(20.04)をインストールし直した上で仮想環境としてpyenvを用いて環境構築を行なった

理由は、フレームワークを TensorFlow から PyTorch へ変更したことです。PyTorch の都合で Ubuntu を下げました。当時の作業メモには「pytorchとか入れにくいので、ubuntu20.04にダウングレード」と残っています。

つまり順序は **22.04 → TensorFlow で依存解決できず → Docker 断念 → PyTorch へ変更 → その都合で 20.04 へ入れ直し → pyenv → Jupyter** です。

- 稼働時の端末記録はUbuntu 20.04.4 LTS、カーネル5.15.0-41-generic、x86_64でした。

> [!WARNING]
> Ubuntu 20.04へ変更した後、有線と無線LANが使えなくなりました。当時はRealtekのドライバをUSBの代替機器へ切り替えました。ドライバ名と導入コマンドは記録が残っていません。

### 2.3 NVIDIA ドライバと CUDA

当時は `nvidia-smi` と `nvcc -V` の両方を確認しました。これはコピペ用手順ではなく、版を区別するために使ったコマンド名の記録です。

```text
nvidia-smi:
  Driver Version: 510.73.05
  CUDA Version: 11.6

nvcc -V:
  Cuda compilation tools, release 11.1, V11.1.74
```


### 2.4 TensorFlow、Docker、PyTorch

私たちはTensorFlowで環境構築を始めました。ライブラリ、CUDA、ドライバの依存関係を解消できませんでした。

次にDockerを試しました。目的に合うイメージを用意する段階でDockerの使用を止めました。その後、フレームワークをPyTorchへ変更しました。

Docker試行では、次のエラーを確認しました。

- Docker socketのpermission denied。
- NVIDIA driverがロードされず、`nvidia-container-cli` が停止。
- `nvidia/cuda:latest` のmanifestがない。
- 存在しないCUDA image名でmetadata取得に失敗。
- Docker build内で `torch==1.9.0+cu111` が見つからない。
- Pillowのsource buildでzlib header / libraryが不足。

これらは成功した手順ではありません。

### 2.5 pyenv と virtualenv

Dreamerの元コードはPython 3.6.9を前提としていました。シミュレータはPython 3.7.0以上を必要としました。

PCの最終環境はPython 3.7.0系でした。環境名は `rl3.7.0` と `sim3.7.0` です。

記録には、Python 3.6.9用の環境を作った例として `pyenv install 3.6.9` と `pyenv virtualenv 3.6.9 python_env` が残っています。この2つは 3.6.9 環境を作ったときの記録で、最終環境 `rl3.7.0`・`sim3.7.0` のコマンドではありません。

環境の確認には `pyenv versions` を使いました。

前身の環境 `py3.6.9`・`py3.7.0` は、次の手順で作りました（2022年8月16〜18日）。

```text
mkdir py3.6.9
cd py3.6.9
pyenv virtualenv 3.6.9 py3.6.9
pyenv local py3.6.9
pip install -r requirements.txt
```

donkeycar は clone して最新タグを checkout し `pip install -e .[pc]`、`donkey createcar --path ~/py3.6.9/mycar` まで実行しています。gym-donkeycar はここで「3.7以上じゃないと gym-donkey 入れられない」（当時の記録の原文）となり、**Python 3.7.0 の環境を作り直す**流れになりました。

3.7.0 側では、Dreamer 用の版指定を入れた `require3.txt` と、シミュレータ用の `requires_sim0.txt` を使っています。keras-vis が新しい版のモジュールを引き込んでしまうため、次の順序が重要でした。

```text
git+https://github.com/autorope/keras-vis.git
typing-extensions==3.7.4.3
tensorboard==2.6.0
```

この手順の後に `python manage.py drive` が成功しました。

当時の `.bashrc` の該当部分です。

```bash
export PATH=/usr/local/cuda-11.1/bin${PATH:+:${PATH}}
export LD_LIBRARY_PATH=/usr/local/cuda-11.1/lib64/${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}
export PYENV_ROOT="$HOME/.pyenv"
command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
```

> [!WARNING]
> pyenvのPATHより先に初期化を評価すると、ログイン時に `pyenv: コマンドが見つかりません` となりました。`PYENV_ROOT` とPATHを設定してから初期化しました。

### 2.6 Miniforge

当時の `.bashrc` にはMiniforgeのconda初期化も残っていました。個人環境のホームディレクトリは伏せています。

```text
<HOME>/miniforge3/bin/conda
```

最終方針はpyenv + virtualenvでした。Miniforgeとpyenvが併存した時点もありました。

> [!WARNING]
> Dreamer用環境とシミュレータ用環境でcondaとpipを混ぜ、環境を壊しました。その後は `rl3.7.0` と `sim3.7.0` を分けました。

### 2.7 5本の requirements

| ファイル | 行数 | 環境 |
|---|---:|---|
| `env/requirements-rl3.7.0.txt` | 106 | PC・Dreamer |
| `env/requirements-sim3.7.0.txt` | 231 | PC・シミュレータ |
| `env/requirements-rl3.7.0-freeze.txt` | 101 | PCの追加freeze |
| `env/requirements-jetson-nao.txt` | 125 | Nao |
| `env/requirements-jetson-jassy.txt` | 162 | Jassy |

これらは当時の環境の証拠です。インストール順を示すlockfileではありません。

そのままインストール指示に使わない行があります。

| 公開ファイル | 内容の種類 | 扱い |
|---|---|---|
| `env/requirements-jetson-jassy.txt` | Donkey Carのeditable Git URL | clone / editable installとして別に扱う |
| `env/requirements-jetson-jassy.txt` | gym-donkeycarのeditable Git URL | clone / editable installとして別に扱う |
| `env/requirements-jetson-jassy.txt` | NumPyのGit commit指定 | aarch64のsource buildとして扱う |
| `env/requirements-jetson-jassy.txt` | pytoolsの直接URL | URL指定として確認する |
| `env/requirements-jetson-jassy.txt` | TensorFlowのローカルwheel | wheel本体が別途必要 |
| `env/requirements-jetson-jassy.txt` | pyenv repositoryを `#egg=torch` としたfreezeの誤記 | インストール指示に使わない |
| `env/requirements-jetson-nao.txt` | ベンダDonkey Carのeditable Git URL | clone後のeditable installとして扱う |

Jassyのfreezeにあるtorchの誤記について、実体は自前ビルド `1.9.0a0+gitd69c22d` です。

### 2.8 PC 側の主なパッケージ版

`rl3.7.0` の主要版は次のとおりです。

| パッケージ | バージョン |
|---|---:|
| gym | 0.17.3 |
| torch | 1.9.0+cu111 |
| torchvision | 0.10.0+cu111 |
| torchaudio | 0.9.0 |
| tensorflow-gpu | 2.6.2 |
| Keras | 2.6.0 |
| NumPy | 1.19.5 |
| h5py | 3.1.0 |
| protobuf | 3.19.4 |
| SciPy | 1.5.4 |
| matplotlib | 3.3.4 |
| Pillow | 8.4.0 |

`sim3.7.0` で追加確認した主要版は次のとおりです。

| パッケージ | バージョン |
|---|---:|
| gym | 0.21.0 |
| opencv-python | 4.6.0.66 |
| opencv-python-headless | 4.6.0.66 |
| moviepy | 1.0.3 |
| pandas | 1.1.5 |
| keras-vis | 0.5.0 |
| torchmetrics | 0.9.3 |

### 2.9 Jupyter と NumPy

Jupyter Notebookは、コードをセル単位で実行するために導入しました。

- NumPy 1.19.2から1.19.5では、Jupyter kernelが起動直後に終了しました。
- 別のNumPy版はTensorFlow 2.6.0の `numpy~=1.19.2` と衝突しました。
- 7 つの NumPy 版を試した表が残っています。1.19.2〜1.19.5 は TensorFlow 2.6.0 の依存を満たしますがカーネルが落ち、1.19.1・1.20.0・1.21.6 は依存を満たしません。
- `pip install git+https://github.com/numpy/numpy.git@v1.19.4` でソースから入れる方法も試し、`ImportError: numpy.core.multiarray failed to import` になりました。
- 途中では依存の警告を許容して 1.21.6 を使いました。
- `RuntimeError: module compiled against API version 0xe but this version of numpy is 0xd` も出ています。
- **これを解いたのは NumPy ではなく matplotlib です**。当時の記録に「一応 matplotlib のバージョンを 3.3.0 → うまくいった」とあります。`ImportError` は `import matplotlib.pyplot` の中の `from . import ft2font` で出ており、古い NumPy ABI に対してビルドされていなかったのは matplotlib の側でした。`env/requirements-jetson-jassy.txt:79` の `matplotlib==3.3.0` がその結果です。
- `env/requirements-jetson-jassy.txt:89` の git URL は試行錯誤の途中で入れたものが残った形で、これ自体が解決策ではありません（`@6d7b8aae` は `v1.19.4` タグと同じツリーです）。
- `AttributeError: 'EntryPoints' object has no attribute 'get'` には `pip install importlib-metadata==4.13.0` で対処しました。

---

## 3. DonkeySimLinux と gym-donkeycar

### 3.1 DonkeySimLinux v18.9

- 使用したバイナリはDonkeySimLinux v18.9です。
- 入手先は `https://github.com/tawnkramer/gym-donkeycar/releases/download/v18.9/DonkeySimLinux.zip` です。
- バイナリはx86_64用です。
- Jetson Nanoで実行すると `Exec format error` になりました。

### 3.2 gym-donkeycar の基準

ベースコミットは `tawnkramer/gym-donkeycar@4ea670491eaef66178a1ffe3d672c7d4344c51bf` です。

- 改変前の `donkey_sim_original.py` が残っています。
- 上流コミットと `donkey_sim_original.py` の差は35行です。デバッグ用 print の追加、`calc_reward` の複製を `"""` で囲んだもの、`img_w`・`img_h` の既定値を `0` から `64` へ変更したもの、空白の差です。上流と最終 `donkey_sim.py` の差は109行（追加102・削除7）で、差分は `sim/gym_donkeycar_mods/donkey_sim_upstream_vs_final.diff` にあります。
- `donkey_sim_original.py` から最終 `donkey_sim.py` への差は77行追加、7行削除です。

### 3.3 `donkey_env.py`

当時の変更は次のとおりです。

```diff
-("cam_resolution", (120, 160, 3)),
+("cam_resolution", (64, 64, 3)),
+("headless", 1),
```

私たちは `cam_resolution` を変え、シミュレータの出力自体を64×64×3にしました（当初は120×160の出力を OpenCV で縮小していました。ノートブックの `cv2.resize` は同じサイズへの変換として残っています）。実機カメラは120×160のままで、Agent の前に64×64へ変換します。

### 3.4 `donkey_sim.py` の報酬

Donkey Car標準のCTEベース報酬は次でした。

```python
return (1.0 - (self.cte / self.max_cte) ** 2) * (self.speed / max_speed)
```

私たちの最終版は、CTE超過と衝突の分岐をコメントアウトしました。報酬を次へ置き換えました。

```python
max_speed = 10
base_all_square_pixel_percentage = 5

return_reward = (
    all_square_pixel_percentage / base_all_square_pixel_percentage
) * (
    self.speed / max_speed
)
```

doneのフレームでは `-1.0` です。RGB基準範囲はR:210–240、G:170–200、B:110–140です。

### 3.5 終了条件

最終 `donkey_sim.py` では、CTE版の終了条件を差し替えました。旧CTE版は `"""archive` ブロックとして同じファイルに残っています。

1. 指定色の画素割合を計算します。
2. `< 0.1%` なら `count_to_dead += 1` とします。
3. `count_to_dead >= 15*2`、すなわち30なら終了します。
4. 終了時に `count_to_dead=0.0` とします。
5. 色が戻った場合、`count_to_dead > 5` のときだけ5を引きます。

`count_to_dead` は `__init__` とreset処理の2箇所で0.0へ初期化します。

### 3.6 ピクセル割合の分母

シミュレータ側と実機側は次の式を使います。

```python
all_square_pixel = sum(image.shape) / 3
```

64×64×3では `131 / 3 ≈ 43.67` です。1画素だけ一致しても約2.29%になります。`< 0.1%` は実質0画素判定です。

> [!IMPORTANT]
> 当時の学習済みモデルの挙動を読む場合は、この分母を前提にします。修正版を作る場合は、`height * width` への変更とreward / doneの再検証を別作業にします。

---

## 4. Dreamer の学習記録

### 4.1 対象

公開版のシミュレーション側は `sim/sim_final.ipynb` です。

このNotebookには、DonkeySimLinuxとの接続、6モデル、Replay Buffer、初期データ収集、600エピソード学習、評価、保存が含まれます。

NotebookにはJupyter magic、シェル記法、対話入力、セル間状態があります。通常のPythonスクリプトとして先頭から実行するものではありません。

### 4.2 シミュレータパス

Notebookに残る絶対パスは、利用者の展開先へ置き換える必要があります。公開文書では次のプレースホルダーを使います。

```python
exe_path = "<PATH_TO_DONKEY_SIM_EXECUTABLE>"
```

### 4.3 主なモデル設定

| 項目 | 値 |
|---|---:|
| 観測 | RGB 64×64 |
| 行動 | steering / throttleの2次元 |
| Encoder出力 | 1024 |
| `state_dim` | 30 |
| RNN hidden | 200 |
| Transition hidden | 200 |
| Reward / Value hidden | 400 |
| Action hidden | 400 |

### 4.4 主な学習設定

| 項目 | 値 |
|---|---:|
| Replay Buffer capacity | 300,000 |
| Model learning rate | `6e-4` |
| Value learning rate | `8e-5` |
| Action learning rate | `8e-5` |
| Adam epsilon | `1e-4` |
| Seed episodes | 5 |
| All episodes | 600 |
| Test interval | 10 |
| Save interval | 100 |
| Updates per collected episode | 100 |
| Action noise variance | 0.3 |
| Batch size | 50 |
| Chunk length | 50 |
| Imagination horizon | 15 |
| `gamma` | 0.9 |
| `lambda` | 0.95 |
| Gradient clipping | 100 |
| `free_nats` | `1e-7` |
| 1エピソードの上限 | 2,000 step |

### 4.5 復元した処理順

| 順番 | 当時の処理 |
|---:|---|
| 1 | 最初の5エピソードをランダム行動で収集 |
| 2 | 観測、行動、reward、doneをReplay Bufferへ投入 |
| 3 | 5エピソード目以降はAgentで行動を生成 |
| 4 | 行動へノイズを追加 |
| 5 | 1エピソード収集後に100回モデルを更新 |
| 6 | 10エピソードごとに評価 |
| 7 | 100エピソードごとに6モデルを保存 |

保存されるファイルは次の6つです。

```text
encoder.pth
rssm.pth
obs_model.pth
reward_model.pth
value_model.pth
action_model.pth
```

実機へ載せたセットは `episode_0600_` です。この6ファイルは手元にありますが、本リポジトリには含めていません。

- 連携コード（`SummaryWriter`、ログ先 `logs_test1006` ／ `logs_test_from1031`）はノートブックに残っています。

---

## 5. Jetson Nano の機体と呼び名

| 機体 | JetPack | Donkey Car | PyTorch |
|---|---|---|---|
| **Nao** | 4.2.2 | XiaoRベンダ版2.5.8と `actuator.so` | stock `1.1.0a0+b457266` |
| **Jassy** | 4.6.2 | `ari-viitala/donkeycar` とPCA9685 | 自前ビルド `1.9.0a0+gitd69c22d`、cp37 |
| **Chaos** | 4.6.1 | - | - |

各機体の JetPack 版は、実機で次を実行して比較しました。

```text
xiaor@xiaor-desktop:~$ dpkg-query --showformat='${Version}' --show nvidia-l4t-core
32.2.1-20190812212815
```

L4T 32.2.1 が JetPack 4.2.2 に対応します。Jassy は 4.6.2、Chaos は 4.6.1 でした。

Jassy では Docker の版も固定していました。当時の記録に「現在の環境➡️Jetpack 4.6.2でした。(docker 20.10.7)」とあります。

**Chaos は別の機体ではありません**。当時の記録に「nao の jetpack バージョンを jassy の方に合わせるように新たにフラッシュしたもの」（2022-11-22）とあり、Nao を焼き直した状態に付けた呼び名です。この試みは「保留」のまま終わり、最終的に走行したのは JetPack 4.2.2 の Nao です。

最終的に走行した実機はNaoです。Jassy の cp37 wheel と Nao の Python 3.6.8 は別の環境のものです。

### 5.1 Jassy の PCA9685

Jassyは通常のJetPack 4.6.2です。Dreamerコードの動作確認まで進みましたが、XiaoR GEEKの拡張ボードを制御できませんでした。

記録には、`i2c.py` のbusを1から8へ変更し、`actuator.py` の `busnum=None` を `busnum=8` へ変更したことが残っています。

- `OSError: [Errno 121] Remote I/O error` が発生しました。
- **重要**: このbus 8はJassyの記録です。Naoへ適用しません。

### 5.2 Jassy の PyTorch 自前ビルド

当時の `torch.sh` は次のとおりです（実行対象の行のみ）。

```bash
#!/usr/bin/env bash

set -xe

VER="$1"
export PYTORCH_BUILD_VERSION="$VER"
export PYTORCH_BUILD_NUMBER="1"

git clone https://github.com/pytorch/pytorch torch || :

cd torch
git checkout "v$VER"
git checkout --recurse-submodules "v$VER"
git submodule sync
git submodule update --init --recursive

rm build/CMakeCache.txt || :

export MAX_JOBS=1
export BUILD_TEST=0
export USE_BREAKPAD=0

python3 setup.py build
python3 setup.py install
python3 setup.py bdist_wheel
```

有効な環境変数は `PYTORCH_BUILD_VERSION`、`PYTORCH_BUILD_NUMBER`、`MAX_JOBS=1`、`BUILD_TEST=0`、`USE_BREAKPAD=0` の5つです。

> [!IMPORTANT]
> `MAX_JOBS=1` は並列ビルドを止める指定です。Jetson Nano のメモリは 4GB とみられ（README §3.4）、並列にするとビルドがメモリ不足で落ちます。**ビルドの前に swap の確保（§6.5）を済ませてください**。当時のビルド所要時間の記録は残っていません。

build後に `ImportError: Failed to load PyTorch C extensions:` が出ました。その後、追加の対処として `python setup.py develop` を実行し、`python -c "import torch"` で確認しました。これは `torch.sh` の外で行った操作です。

ほかに次のエラーを確認しました。

- `AttributeError: module 'distutils' has no attribute 'version'`
- `Illegal instruction (core dumped)`
- `ImportError: Failed to load PyTorch C extensions:`
- 外部配布のcp37 wheelがCPU用だったこと。

生成物名は `torch-1.9.0a0gitd69c22d-cp37-cp37m-linux_aarch64.whl` です。

### 5.3 Jassy の個別パッケージ記録

- Keras は 2.10.0 から `keras==2.6` へ指定し直しました。
- TensorFlow は KumaTea の aarch64 wheel をローカルファイルで指定しました。
- NumPyはGit commit指定で、aarch64のsource buildが走る行です。

### 5.4 Jassy の実行前環境変数

Jassyでは、`import torch` の前に `OPENBLAS_CORETYPE=ARMV8` を設定しました。

設定しない場合は `Illegal instruction (core dumped)` になりました。これはインストールコマンドではなく、実行前条件の記録です。

---

## 6. Nao の microSD

### 6.1 改造 JetPack の配布記録

- 当時は Google Drive 上の再アップロードから入手しました。**その URL はここには載せません**（第三者のフォルダであり、私たちに再配布する権利がないためです）。ベンダのハンドブックには公式サイトからの入手が案内されています。
- 分割ファイルは `JetsonNanoDonkey.part1.rar` と `JetsonNanoDonkey.part2.rar` です。当時の記録はベンダのハンドブック13ページを転記したもので、そこでは結合後のファイル名が `JetsonNanoDonkey.ing` と書かれています。`.img` の転記ミスと思われますが、原文のまま記します。
- 2つを展開して完全な `.img` を得ました。
- 書込みツールはUSB Image Toolです。

### 6.2 フラッシュの記録

当時は次の順で行いました。

1. 改造JetPackの `.img` をmicroSDへ書き込みました。
2. JetPack 4.2対応のJetson Nano Developer Kit SD card imageを適用しました。

128GBのmicroSDへのフラッシュは、メモリと依存関係で失敗するたびに初期化し、5、6回やり直しました。一度で決まらなかったため、この工程には時間を見ておく必要があります。

使用状態へ到達するまで約1週間かかりました。

### 6.3 パーティションの実ログ

> [!CAUTION]
> `fdisk` はパーティションテーブルを変更します。次は当時の128GBカードの実ログです。別のカードへそのまま適用しません。
>
> **この作業の目的は容量の確保です**。パーティションを広げて swap を確保しないままパッケージ導入や学習を進めると、当時の報告書の言葉では「swap メモリが最大となったままシャットダウンし、未来永劫起動しなくなる」状態になります。

当時の入力列は次のとおりです。

```text
fdisk /dev/mmcblk0

p
d
1
n
1
Enter
249737182
y
p
w
```

First sectorではEnterを押し、既定値24576を採用しました。

| 入力 | 当時の操作 |
|---|---|
| `p` | 現在のパーティションを表示 |
| `d` | 削除 |
| `1` | パーティション1 |
| `n` | 新規作成 |
| `1` | 新しいパーティション1 |
| Enter | First sectorの既定値24576 |
| `249737182` | Last sector |
| `y` | signatureを削除 |
| `p` | 変更後を表示 |
| `w` | 書込み |

### 6.4 ファイルシステム拡張

成功記録のコマンドは `resize2fs /dev/mmcblk0p1` です。これは当時のログの引用です。

結果は `/dev/mmcblk0p1` が118G、使用13G、空き101Gでした。

> [!WARNING]
> `resize2fs /dev/mmcblk0` と、`p1` を付けずに入力してしまうこともありました。成功したのは `/dev/mmcblk0p1` です。

### 6.5 swap

- パーティション拡張後、swapを2GBから18GBへ広げました。
- 最終ファイル名の記録は `swapfile2` です。

> [!CAUTION]
> パーティションとswapを確保せずに大きなパッケージ導入や長時間処理を進めると、swapが最大のままシャットダウンし、その後起動しなくなります。

---

## 7. Nao のソフトウェアとハードウェア

### 7.1 基準環境

| 項目 | 値 |
|---|---|
| CPUアーキテクチャ | aarch64 |
| Python | 3.6.8 |
| CUDA | 10.0 |
| JetPack | 4.2.2 |
| PyTorch | stock `1.1.0a0+b457266` |
| Donkey Car | XiaoRベンダ版2.5.8 |
| commit | `991693552/donkeycar_jetson_nano@0656898c14099f105f82945dd481cc6ce606b103` |

Nao の PyTorch は stock `1.1.0a0+b457266` です。Jassy の自前ビルド 1.9.0 は入っていません。

### 7.2 Donkey Car

NaoのDonkey Carでは、clone後に `pip install -e .[nano]` を実行しました。当時のコマンドのままでは、現在は成功するとは限りません。

`env/requirements-jetson-nao.txt` は当時のfreezeです。まとめて適用した際に複数のエラーが出ました。

- 個別に `tornado==5.0` を指定しました。

### 7.3 `car/config.py`

```python
DRIVE_LOOP_HZ = 20
MAX_LOOPS = 100000

CAMERA_RESOLUTION = (120, 160)

STEERING_CHANNEL = 1
STEERING_LEFT_PWM = 40
STEERING_RIGHT_PWM = 150

THROTTLE_CHANNEL = 0
THROTTLE_FORWARD_PWM = 200
THROTTLE_STOPPED_PWM = 100
THROTTLE_REVERSE_PWM = 0
```

`car/config.py` はベンダ版から機能変更されていません。PWM値はベンダ既定値です。

### 7.4 Nao の I2C

Naoの `car/config.py` には `PCA9685_I2C_BUSNUM` と `PCA9685_I2C_ADDR` がありません。`car/manage2.py` のPCA9685 controller作成行はコメントアウトされています。

有効な経路は次のとおりです。

```text
Dreamer Agent
  → PWMSteering / PWMThrottle
  → donkeycar.parts.actuator
  → actuator.so
  → XiaoR GEEK 拡張ボード
```

#### 参考: 別環境の Donkey Car 4.x config

別環境には、次の形式のconfigが残っています。

```python
PCA9685_I2C_ADDR = 0x40
PCA9685_I2C_BUSNUM = None
DRIVE_TRAIN_TYPE = "PWM_STEERING_THROTTLE"
PWM_STEERING_THROTTLE = {
    "PWM_STEERING_PIN": "PCA9685.1:40.1",
    "PWM_THROTTLE_PIN": "PCA9685.1:40.0",
    "STEERING_LEFT_PWM": 460,
    "STEERING_RIGHT_PWM": 290,
    "THROTTLE_FORWARD_PWM": 500,
    "THROTTLE_STOPPED_PWM": 370,
    "THROTTLE_REVERSE_PWM": 220,
}
```

460、290、500、370、220 と `0x40` は Nao の実値ではありません。

### 7.5 カメラ

`car/manage2.py` は `CSICamera` を使い、画像が来るまで待つ構成です。

```python
cam = CSICamera()

while cam.run() is None:
    time.sleep(1)
```

実機では `nvgstcapture` でカメラ映像を確認しました。これは当時使ったコマンド名の記録です。

カメラ画像は120×160です。Agentへ渡す直前に64×64へ変換します。

### 7.6 Dreamer 統合前の駆動確認

私たちはDreamer統合前に、`manage.py` でカメラとアクチュエータを確認しました。三角関数の行動値でサーボモーターとDCモーターが動くことも確認しました。

対応する痕跡は改変した `parts/keras.py` にあります。保存版では `count_loop` が更新されず、完全な動作版ではありません。

この改変 `parts/keras.py` は `car/vendor_mods/parts/keras.py` に同梱しています。

---

## 8. 重みの変換と転送

### 8.1 変換元

実機へ載せた変換元は `episode_0600_` の6ファイルです。

```text
encoder.pth
rssm.pth
obs_model.pth
reward_model.pth
value_model.pth
action_model.pth
```

この6ファイルは手元にありますが、本リポジトリには含めていません。公開リポジトリでは `.gitignore` で `*.pth` を除外します。

### 8.2 `.pth` から `.npy`

PC側では各state dictについて次を行いました。

1. `torch.load()` で読みました。
2. TensorをCPUへ移しました。
3. NumPy配列へ変換しました。
4. パラメータ名の `.` を `+` へ置き換えました。
5. パラメータごとに `.npy` を保存しました。

`.npy` は次の6ディレクトリに分かれています。

```text
tmp_action/
tmp_encoder/
tmp_obs/
tmp_reward/
tmp_rssm/
tmp_value/
```

- 64個の `.npy` が残っています。
- 変換元コードには `os.mkdir(..., exist_ok=True)` という無効な呼出しがあります。標準Pythonの `os.mkdir()` は `exist_ok` を受け取りません。

### 8.3 転送

PCからNaoへモデルを転送したことは確認できています。

### 8.4 `.npy` から `.pth`

当時の `pull_weight.py` は次を行いました。

1. `.npy` を読みました。
2. ファイル名の `+` を `.` へ戻しました。
3. `torch.from_numpy()` でTensorにしました。
4. `OrderedDict` を作りました。
5. Jetson Nano側のPyTorchで `.pth` を保存しました。

> [!IMPORTANT]
> `pull_weight.py` は `car/pull_weight.py` に置いています。当時の記録です。そのままでは実行できません。`.npy` を置いたディレクトリ構成に依存します。

actionの出力名には版差がありました。

| 記録された版 | actionの出力名 |
|---|---|
| `mycar/presentemp/pull_weight.py` | `action.pth` |
| `mycar/tmp/pull_weight.py` | `action_model.pth` |
| `car/manage2.py` が要求する名前 | `action_model.pth` |

### 8.5 ONNX の試行

私たちはONNXも試しました。最終的に採用した重みの移動形式は `.npy` 経由です。

---

## 9. `car/manage2.py`

### 9.1 最初に止まる箇所

> [!CAUTION]
> `car/manage2.py` はベンダ版に存在しないシンボルを2つ import します。`:16` の `CSICamera`（`car/vendor_mods/parts/camera.py` で追加したクラス）と `:20` の `datastore_for_record`（`car/donkeycar_parts/` に同梱）です。**先に止まるのは16行目の `CSICamera`** で、両方をベンダ版の `donkeycar/parts/` へ配置しないと、6重みを読む前に ImportError で停止します。

不足モジュールを別途復元した後は、`mycar/presentemp/` に §8.1 の6ファイル（`encoder.pth` ほか）を置く必要があります。この6ファイルも本リポジトリには含めていません。

### 9.2 復元した起動処理

| 順番 | 当時の処理 |
|---:|---|
| 1 | Dreamerの各モデルを作成 |
| 2 | 6重みを読込み |
| 3 | `MyController` をVehicleへ追加 |
| 4 | CSIカメラを追加し、画像が来るまで待機 |
| 5 | 画像用TubWriterを追加 |
| 6 | steeringとthrottleのアクチュエータを追加 |
| 7 | Vehicle loopを開始 |

当時の実行形式は `cd mycar` の後に `python3 manage2.py` でした。これは復元したコマンド文字列であり、現在の成功手順ではありません。

### 9.3 安全上の注意

> [!CAUTION]
> `manage2.py` は重みを読んだ後、Vehicle loopをアクチュエータへ接続します。起動前のarmスイッチと安全確認はありません。
> また、ベンダ版へ組み込む改変 `vehicle.py` の dead 判定は、コース逸脱を検知すると**走行を15秒間止めます**（`car/vendor_mods/vehicle.py:205-208`）。

> [!CAUTION]
> 緊急停止手順の記録は残っていません。停止方法を決めるまで実車で起動せず、車輪を接地しない試験から確認する必要があります。

画面には `CTRL+S` と表示しますが、Ctrl+Sを扱うコードはありません。終了保存処理は `KeyboardInterrupt` を通ります。現存コード上の停止操作はCtrl+Cです。

### 9.4 現存コードの問題

- 同じ画像に対してAgentを2回呼びます。RNN隠れ状態も2回更新します。
- 表示したactionと制御に使うactionが別になります。
- 2つ目のTubWriterは `recording` を要求しますが、それを出力するpartがありません。
- カメラ出力名 `image` と要求名 `image_array` が一致しません。
- コメントには20秒走行とあります。実configは20Hz、最大100000ループです。上限までなら約83分20秒です。
- 実機でもActionModelの既定 `training=True` により確率的sampleを使います。

---

## 10. 実機データの保存

### 10.1 車上の pickle

車上では次の3本の共有リストを使いました。

```text
steerings_record
throttles_record
images_record
```

終了時に1個の `.bin` へ次の順で保存しました。

```text
steerings
throttles
images
```

> [!IMPORTANT]
> この共有リストを定義した `donkeycar.parts.datastore_for_record` は `car/donkeycar_parts/` に置いています。steering と throttle をリストへ追加するのは `car/manage2.py:85-86` です。画像を追加する処理と、終了時に pickle へ書き出す処理は、改変版 `vehicle.py`（`car/vendor_mods/vehicle.py:238` と `:145-166`）にあります。

### 10.2 reward / done 追加後

処理後は次の5項目です。

```text
steerings
throttles
images
rewards
dones
```

車上の3項目と処理後の5項目を同じ形式として読みません。

### 10.3 `TubWriter`

標準 `TubWriter.run()` は、入力名の数と実引数の数が一致しないと `assert` で停止します。

私たちは `assert` をコメントアウトし、`zip()` できた範囲だけを記録するようにしました。この変更は不足した項目を補いません。

`parts/datastore.py` は `car/vendor_mods/parts/datastore.py` に同梱しています。

---

## 11. reward と done の後付け

### 11.1 RGB 範囲

基準範囲は次のとおりです。

```text
R: 210–240
G: 170–200
B: 110–140
```

これは**シミュレータの路面色 `#ECBC79`**（R=236, G=188, B=121）を囲む範囲です。

実環境のテープからもサンプルを取りました。`#eaa004`（R=234, G=160, B=4）と
`#fccc54`（R=252, G=204, B=84）です。**どちらも上の範囲には入りません**。
当時の記録にも「結構違うので別々にする」とあります。

実機側は `extention_color = 10` とし、各範囲を上下へ10広げます。報告書には「報酬とみなす RGB の範囲をシミュレーション環境よりも広めに設定した」とあります。当時の記録にあるのは「結構違うので別々にする」という判断だけです。

10広げても上の2色は範囲に入りません。実環境で実際にどの画素が拾われていたかは、走行データの画像から確かめられます（目録は `../data/INVENTORY.md`）。データ本体は容量の都合で同梱していません。

#### この報酬の限界

当時、影がかかった黄色テープの色も測っています。

| サンプル | R | G | B | 基準範囲 |
|---|---:|---:|---:|---|
| `#836916` | 131 | 105 | 22 | 入らない |
| `#826600` | 130 | 102 | 0 | 入らない |

影の下ではテープを認識できません。`extention_color` で上下へ10広げても届きません。
**この報酬は照明条件に依存します**。同じコースでも影の位置が変われば拾える画素が変わります。

±10 を適用したコード上の厳密な判定範囲は、channel 0が200より大きく250より小さい範囲、channel 1が160より大きく210より小さい範囲、channel 2が100より大きく150より小さい範囲です。

`base_all_square_pixel_percentage` は探索中に2、10、5と変わり、最終値は5です。`count_to_dead` は `15*10` から `15*2` へ変わりました。

### 11.2 done

| 順番 | 当時の処理 |
|---:|---|
| 1 | 画像を64×64へ変換 |
| 2 | 指定色の割合が0.1%未満なら `count_to_dead` を1増加 |
| 3 | 30に達したフレームでdoneを `True` |
| 4 | done後にカウンタを0へ戻す |
| 5 | 閾値以上へ戻り、カウンタが5より大きければ5減少 |

30フレームが完全に連続する条件ではありません。

### 11.3 reward

doneのフレームでは `reward = -1.0` です。

doneでない場合は次の式です。

```text
reward =
  (all_square_pixel_percentage / 5)
  × (throttle / 10)
```

steeringは式に入りません。

### 11.4 分母

実機側も `all_square_pixel = sum(image.shape) / 3` を使います。

分母の式と帰結は §3.6 と同じです（約43.67・1画素で約2.29%・`<0.1%` は実質0画素判定）。実機側の違いは、入力が リサイズなしの生画像 という点だけです。

実機のdone判定は64×64画像を使います。reward計算は保存画像をその場でリサイズしません。両者は入力サイズと分母の値が異なります。

### 11.5 復元した実行形式

当時は `cd mycar` の後に `python3 gets_reward_done_independent.py` を実行しました。これは復元したコマンド文字列です。

`real_data_names_store.txt` の各 `.bin` を読み、rewardとdoneを加えて同じファイルへ書き戻します。

> [!CAUTION]
> 元の `.bin` を `wb` で同名上書きします。別名または別ディレクトリへバックアップしてから扱う必要があります。

> [!WARNING]
> `pickle.load()` は信頼できるファイルだけに使います。

---

## 12. PC でのモデル更新

### 12.1 意図した処理

`car/train_world_model.py` は次を意図しています。

| 順番 | 意図した処理 |
|---:|---|
| 1 | 6重みを読込み |
| 2 | 5項目のpickleをReplay Bufferへ投入 |
| 3 | Dynamics、Actor、Criticを100回更新 |
| 4 | 6重みを保存 |

ファインチューニング開始時に、PC側の6モデルを1つのcheckpoint dictから読むコードも残っています。

当時の実行形式は `cd mycar` の後に `python3 train_world_model.py` でした。

### 12.2 現存版の問題

> [!CAUTION]
> 現存 `car/train_world_model.py` はそのままでは動きません。EOF分岐でデータファイルを削除します。

1. `lambda_target()` をimportせずに呼びます。
2. action modelの保存先 `model_log_dir` が未定義です。
3. データ名一覧を回しても、毎回同じ固定 `.bin` を開きます。
4. EOFでデータファイルを削除します。
5. その後、`wb` で開いた書込み専用ファイルから `pickle.load()` します。
6. Optimizer作成後にモデルを別インスタンスへ作り直します。
7. Replay Bufferは画像領域だけで約3.43GiBを確保する設定です。
8. import する `car/dreamer/replaybuffer.py:18` の `ReplayBuffer` が `np.bool` を使います。新しいNumPyでは削除されている別名です。

修正後は、複製したデータで検証してから実データへ使う必要があります。

---

## 13. ほかの動かないファイル

### 13.1 `car/pthToOnnx.py`

`car/pthToOnnx.py:14` には `torch.onnx.export(model = PATH = "...", dummy_input, ...)` があります。

引数内の連鎖代入により構文エラーになります。ファイル自体をparseできません。

### 13.2 `car/dreamer/main.py`

`car/dreamer/main.py:43` は `obsercation` をimportします。実ファイル名は `observation.py` です。

名前の不一致によりImportErrorになります。

### 13.3 `car/dreamer/makeEnv.py`

`car/dreamer/makeEnv.py:2` は `def __init__():` となっており、`self` がありません。

以降の処理も `self.` を付けずに値を参照しています。このままではインスタンスの状態を保持できません。

---

## 14. 4種類のスロットル変換

| 場所 | 用途 | 変換 |
|---|---|---|
| `sim/sim_final.ipynb` の初期データ収集 | シミュレータのランダム収集 | `(action[1] + 0.75) / 2` |
| `sim/sim_final.ipynb:1571,1808,1832` ／ `real/real_final.ipynb:1769,1793` | 訓練中のテストとburn-in | `(action[1] + 0.75) / 2` |
| `sim/sim_final.ipynb:1761` ／ `real/real_final.ipynb:1722` | 独立した評価セル | `(action[1] + 0.75) / 4` |
| `car/manage2.py` | 実機駆動 | `(action[1] + 0.75) / 8` |
| 実機データの学習投入処理 | Replay Bufferへ投入 | `(throttles[i] + 0.75) / 16` |

`training=False` のループは他にもあり、そちらは `/2` です。`/4` は独立評価セルの2箇所だけで、どちらも生きています。

実機で記録するthrottleは、すでに `/8` 変換後です。その値へ学習投入時の `/16` をさらに適用するコードは、PC側のaction空間と一致しません。

---

## 15. 復元した実機サイクル

実機サイクルは次の順だったと復元できます。

| 順番 | 当時の処理 | 現在の状態 |
|---:|---|---|
| 1 | `episode_0600_` の6重みをPCで `.npy` 群へ変換 | 変換コードには無効な `os.mkdir(..., exist_ok=True)` があります |
| 2 | `.npy` 群をJetson Nanoへ転送 | PCからNaoへモデルを転送したことは確認できています |
| 3 | `pull_weight.py` で6個の `.pth` を復元 | `car/pull_weight.py` に同梱しています |
| 4 | `manage2.py` で走行と収集 | 不足importにより現状は起動前に停止します |
| 5 | `gets_reward_done_independent.py` でrewardとdoneを追加 | 元pickleを同名上書きします |
| 6 | `train_world_model.py` でPC上のモデルを更新 | 現存版は実行不能で、データ削除を含みます |
| 7 | 更新重みを再び `.npy` 経由で実機へ戻す | 変換ツールは両方向とも現存します（往路は `real/real_final.ipynb` 内のセル、復路は `car/pull_weight.py`） |

この反復は完成した手順ではありません。

解消が必要な事項は次のとおりです。

- `car/train_world_model.py` の修正。
- 元 `.bin` のバックアップ。
- 緊急停止手順。
- 4種類のスロットル変換の統一。
- PCとJetson Nano間の転送方法。

---

## 16. ベンダ版への改変と未同梱ファイル

改行を正規化すると、ベンダ版に対する実コードの変更は次の6ファイルでした。**行数は空行の増減を除いた実質変更です**（同梱 diff の生カウントは空行を含むため少し多く出ます）。

| ファイル | 追加 | 削除 | 本リポジトリでの状態 |
|---|---:|---:|---|
| `vehicle.py` | 107 | 1 | `car/vendor_mods/vehicle.py` |
| `parts/camera.py` | 49 | 88 | `car/vendor_mods/parts/camera.py` |
| `parts/web_controller/web.py` | 12 | 3 | `car/vendor_mods/parts/web_controller/web.py` |
| `parts/keras.py` | 10 | 0 | `car/vendor_mods/parts/keras.py` |
| `parts/datastore.py` | 8 | 2 | `car/vendor_mods/parts/datastore.py` |
| `parts/web_controller/templates/base.html` | 3 | 5 | `car/vendor_mods/parts/web_controller/templates/base.html` |

`car/manage2.py` がimportする `donkeycar.parts.datastore_for_record` は `car/donkeycar_parts/` に同梱しています。

`config.py`、`parts/controller.py`、`memory.py`、`management/tub.py`、`management/base.py`、`log.py`、`__init__.py` は実質0行の変更でした。改行コードだけが変わっていました。

---

## 17. 当時のログが手元にないもの

次の項目は、この文書に書けませんでした。手順を追ってここで行き止まりになった場合は、当時の記録がそこまでだったということです。

**Jetson 側**

- 改造 JetPack イメージのチェックサムとファイルサイズ
- swap を作るときの `fallocate`、`mkswap`、`swapon`、`fstab` の実コマンド
- Jassy でビルドした PyTorch と TensorFlow の wheel 本体
- Nao の I2C バス番号と、説明付きの配線図
- Nao の緊急停止手順

**PC 側**

- Ubuntu 導入時の ISO の point release と入手先（版の変遷 22.04 → 20.04 は §2.2）
- NVIDIA ドライバを入れた apt のコマンド列
- ONNX を採用しなかった理由を示す実行時エラーの原文

---

## 18. 公開物に含めないもの

- Jetsonの認証情報は記載していません。
- 個人環境のホームディレクトリを含む絶対パスは、`sim/`・`real/` のノートブックでは `<PATH_TO_DONKEY_SIM_EXECUTABLE>`・`<PATH_TO_MODEL_DIRECTORY>`・`<PATH_TO_MODEL_CHECKPOINT>`・`<PATH_TO_REAL_DATA_NAMES_STORE>` の形へ置き換えています。`<PATH_TO_REAL_DATA_NAMES_STORE>` が指すのは、同梱している `data/real_data_names_store.txt` に相当する当時の台帳です。`car/dreamer/makeEnv.py`、`car/pthToOnnx.py`、`car/vendor_mods/vehicle.py:15`（コメント行）、`env/` の freeze ファイルには、当時の記録としてそのまま残しています。
- XiaoR GEEKの `actuator.so`、`xrcamera.so`、`_XiaoRGEEK_SERVO_.so`、`XiaoRGEEK.jpg` は再配布しません。
- `INIT_LED.py` はベンダ著作権表示があり、私たちの自作物として再配布しません。
- `server.key` は公開しません。
- 改造JetPackは再配布しません。
- 学習済み重み、走行データ、動画は本リポジトリに含めません。重みと動画は Release の Assets に置きます。

実機を再現する場合は、キット付属のベンダ提供物を別途用意する必要があります。
