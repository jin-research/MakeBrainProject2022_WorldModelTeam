---
layout: default
title: 拡張ボードが動かない
---

# 拡張ボードが動かない — PCA9685 から MyController まで

2022年10月〜11月

## 問題

Jetson Nano に載せた XiaoR GEEK の拡張ボードで、モーターを制御できませんでした。この拡張ボードはネット上でほとんど情報を得られず、開発を進める中で障害になりました。

## 試した経路

1. 最初に PCA9685 を使うクラスを試しました。XiaoR GEEK の拡張ボードには対応しませんでした。
2. 次に、別の Jetson Nano へ `actuator.so` を移しました。移した `.so` は認識されませんでした。
3. Arduino を使う案へ移りましたが、実現には至りませんでした。
4. 別の記録では、拡張ボードを使わずに GPIO と PWM を直接配線するとモーターを制御できることも確認しています。
5. その後、XiaoR GEEK が公開していた改造 JetPack を見つけ、Nao へ作業を移しました。

最終経路は、改造 JetPack 4.2.2 を使う Nao でした。

## `MyController` の発見

Nao と拡張ボードを使える状態になった後も、`manage.py` はアプリを経由した操作になっていました。

`MyController` というクラスを見つけたことで、コマンドから Donkey Car を直接動かせるようになりました。ここから Dreamer を組み込む処理へ進みました。

`manage2.py` では、`MyController` がカメラ画像を64×64へ変換し、Dreamer の Agent から steering と throttle を受け取ります。

---

[経緯の一覧へ戻る](../ABOUT_appendix)
