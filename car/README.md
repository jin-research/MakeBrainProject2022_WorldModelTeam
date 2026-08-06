# 実機 Jetson Nano "Nao" のコード

私たちは、ここに Jetson Nano 上での Dreamer 推論、車体駆動、走行データ処理、
PC での再学習を試みた Python コードを置きます。28本のうち18本は `dreamer/` にあります。
元の28本にあった `setup.py` は、この公開物には同梱していません。

| ファイル名 | 何をするか | 実行の起点か |
|---|---|---|
| `config.py` | 車両ループ、カメラ、PWM、保存先を設定します | いいえ |
| `gets_reward_done.py` | 1個の `.bin` に reward / done を追加するクラス。**単体では動きません**（`donkeycar.real_data_names_store` からファイル名を import します。`car/vendor_mods/real_data_names_store.py` をベンダ木へ置く必要があります）。`independent` 版を使います | いいえ |
| `gets_reward_done_independent.py` | 一覧中の `.bin` に reward / done を追加して上書きします | はい、引数なし |
| `manage.py` | Donkey Car 標準系の手動・Keras 操縦と学習 | はい、引数あり |
| `manage2.py` | Dreamer 推論で実機を駆動し、走行データを収集します | はい、引数なし |
| `pkl.py` | `.bin` を読み、画像を確認用に書き出します | 補助起点、引数なし |
| `pull_weight.py` | `.npy` を `.pth` へ戻します | はい、引数なし |
| `pthToOnnx.py` | `.pth` の ONNX 変換を試した未完成コード | いいえ |
| `train_world_model.py` | 実機データでモデルを再学習しようとします | 意図上は起点、現状実行不能 |
| `wl_test.py` | データ名を作り、`test.txt` の追記・上書き・読出しを試します | テスト起点、引数なし |
| `dreamer/action_old.py` | 旧版の ActionModel（当時のファイル名は `action (copy).py`。最終版との差分が読めるよう残しています） | いいえ |
| `dreamer/action.py` | 行動分布から steering / throttle を生成します。末尾に報酬計算の断片が貼り付いたまま残っています（下記）| いいえ |
| `dreamer/agent.py` | 画像から行動を生成し、RNN 状態を保持します | いいえ |
| `dreamer/encoder.py` | 64×64 RGB画像を埋め込みへ変換します | いいえ |
| `dreamer/lambda_target.py` | Actor / Critic 用の λ-return を計算します | いいえ |
| `dreamer/main.py` | ノートブック分割途中の学習コード | 形式上は起点、実行不能 |
| `dreamer/makeEnv.py` | DonkeySim 環境ラッパーの未完成コード | いいえ |
| `dreamer/observation.py` | 状態表現から64×64 RGB画像を再構成します | いいえ |
| `dreamer/param.py` | モデル、Optimizer、学習値をまとめる未完成コード | いいえ |
| `dreamer/preprocessObs.py` | 画像を `[-0.5, 0.5]` へ正規化します | いいえ |
| `dreamer/preprocess_obs.py` | 同じ画像正規化の別ファイル | いいえ |
| `dreamer/randomAction.py` | DonkeySim で経験収集する未完成コード | いいえ |
| `dreamer/replaybuffer.py` | done 境界をまたがない系列を保存・抽出します | いいえ |
| `dreamer/reward.py` | 状態表現から報酬を予測します | いいえ |
| `dreamer/rssm.py` | Transition / Observation / Reward を束ねます | いいえ |
| `dreamer/takeAction.py` | steering の移動平均を行う未完成コード | いいえ |
| `dreamer/transition.py` | GRU、prior、posterior を実装します | いいえ |
| `dreamer/value.py` | 状態価値を予測します | いいえ |

## 当時の実行順

**これはそのまま動かせる手順ではありません**。当時どの順で動かしていたかの記録です。
現存コードには下記「そのままでは動かない箇所」に挙げた問題があります。

実機で Python を起動する前に `export OPENBLAS_CORETYPE=ARMV8` が必要です。
これがない場合、`import torch` が `Illegal instruction` で終了しました。

> [!CAUTION]
> `manage2.py` は、ベンダ版に**存在しない**シンボルを2つ import します。どちらも配置しないと
> 重みを読む前に ImportError で停止します。
>
> - `:16` `from donkeycar.parts.camera import CSICamera` … `car/vendor_mods/parts/camera.py` で追加したもの
> - `:20` `donkeycar.parts.datastore_for_record` … `car/donkeycar_parts/datastore_for_record.py`
>
> **先に止まるのは16行目の `CSICamera` です**。
>
> また `manage2.py` には起動前の arm スイッチと安全確認がありません。緊急停止手順の記録も残っていません。
> 停止方法を決めるまで実車で起動せず、車輪を接地しない試験から確認してください。
>
> **同じことが `manage.py` にも当てはまります**。`manage.py:108,112` は `PWMSteering` と `PWMThrottle` を
> 車両ループへ組み込むので、`python3 manage.py drive` 系のコマンドも**実際にモーターを回します**。
> こちらにも arm スイッチと安全確認はありません。下記の起動例を試す前に、車輪を浮かせてください。

1. `python3 manage2.py` は実機走行とデータ収集を行います。引数なし。起動前に
   `presentemp/` へ `encoder.pth`、`rssm.pth`、`obs_model.pth`、
   `reward_model.pth`、`value_model.pth`、`action_model.pth` の6本が必要です。
   これら6本はこのリポジトリに含めていません。
2. `python3 gets_reward_done_independent.py` は reward / done を付加します。引数なし。
   元の `.bin` を上書きします。
3. `python3 train_world_model.py` は PC で再学習する意図の引数なしコマンド。
   **現状のままでは動きません。ただし壊れていても `os.remove` は実行されます**。読み込みが
   `EOFError` になると入力の `.bin` を削除します（`:157`）。試すなら必ず複製に対して行ってください。
4. `python3 pull_weight.py` は `.npy` を `.pth` へ戻す引数なしコマンド。
   版により action の出力名が `action.pth` / `action_model.pth` と異なります。

そのほかの起点は `python3 manage.py drive`、`python3 manage.py drive --model=<keras-model>`、
`python3 manage.py drive --js`、`python3 manage.py drive --chaos`、
`python3 manage.py train --tub=<tub-paths> --model=<new-model>` です。
補助・テストは引数なしの `python3 pkl.py` と `python3 wl_test.py` です。

## 駆動設定

駆動経路は `Dreamer Agent → angle/throttle → PWMSteering/PWMThrottle → donkeycar.parts.actuator`
（ベンダの `actuator.so`）`→ XiaoR GEEK 拡張ボード` です。
I2C バス番号は Python 側で指定していません。`manage2.py` の `PCA9685_I2C_BUSNUM` の行は
コメントアウトされ、`config.py` にも該当行がありません。

バス番号はベンダの `actuator.so` が内部で扱っていたとみられます。`.so` の中身は確認していません。

拡張ボードは XiaoR GEEK の PWR.A53 系です。当時の部品資料に、DC モーター制御の BCM ピン割当
`ENA = 13` / `ENB = 20` / `IN1 = 19` / `IN2 = 16` と、降圧レギュレータ LM2596s の記載があります。

Nao の `i2cdetect` 出力と、配線を説明付きで示した図は残っていません。

I2C は当時からの未解決事項です。後期発表の資料に「I2C通信（解決できない）」とあります。あわせて
同資料には「xiaorgeekのボードを使わずに直接配線するとgpioとPWMでモータの制御ができることは確認」ともあり、拡張ボードを介さない経路では動くところまで確認していました。

PWM は `STEERING_LEFT_PWM = 40` / `STEERING_RIGHT_PWM = 150` / `THROTTLE_FORWARD_PWM = 200` / `THROTTLE_STOPPED_PWM = 100` / `THROTTLE_REVERSE_PWM = 0` です。

## 残っている問題と不足物

`train_world_model.py` は `lambda_target()` 未import、`model_log_dir` 未定義、固定 `.bin` の反復読込、
EOF 時の削除後に書込み専用ファイルから読む処理、Optimizer 作成後のモデル再生成があり、ロード済みモデルが更新対象になりません。
`manage2.py` は1フレームで Agent を2回呼び、表示は Ctrl+S ですが実装は Ctrl+C で、
2つ目の `TubWriter` も成立していません。スロットル変換は4種類あります。シミュ収集と訓練中テスト `/2`、独立した評価セル `/4`、実機駆動 `/8`、学習投入 `/16` です。

`makeEnv.py`、`main.py`、`param.py`、`randomAction.py` はノートブック分割途中で、
未定義変数があり単独では動きません。

`dreamer/action.py:40` に `all_square_pixel = sum((self.image_array).shape) / 3` を含む報酬計算の断片が
`ActionModel` の中へ貼り付いたまま残っています。`self.image_array` も `self.speed` も `ActionModel` には無いので、
この部分は死んでいます。同じ式はシミュレータ側・実機側の報酬計算と `vendor_mods/vehicle.py:191`（実車の dead 判定）にもあり、**最終版ファイル全体で6ファイル・10箇所**です（一覧はリポジトリ README の §6）。
引数なしの `python3 dreamer/main.py` は形式上の起点ですが、現状のままでは実行できません。

ベンダの `.so` 3本、`XiaoRGEEK.jpg`、`INIT_LED.py`、`server.key`、改造 JetPack は同梱していません。
`server.key` は秘密鍵なので含めません。その他はベンダの商業利用禁止条件により再配布せず、キットを購入した方は、元の提供物をお使いください。
詳しい環境と欠落箇所は [`../docs/SETUP.md`](../docs/SETUP.md) を参照してください。

> [!WARNING]
> このディレクトリのコードは `pickle.load()` と `torch.load()` を使います。どちらも読み込むだけで
> 任意のコードが実行されえます。**自分で作ったファイルか、出所の確かなファイルにだけ使ってください**。
> 該当するのは `gets_reward_done.py`、`gets_reward_done_independent.py`、`pkl.py`、
> `train_world_model.py`、`manage2.py`、`dreamer/param.py` です。
>
> `dreamer/replaybuffer.py` は `np.bool` を使います。新しい NumPy では削除されています。
