# 環境スナップショット

私たちは、学習用 PC と2台の Jetson Nano で記録した requirements をここに置きます。

## ファイル

| ファイル名 | 行数 | どの機体・どの環境のものか |
|---|---:|---|
| `requirements-rl3.7.0.txt` | 106 | 学習用 PC・Dreamer 側（Python 3.7.0） |
| `requirements-sim3.7.0.txt` | 231 | 学習用 PC・シミュレータ側（Python 3.7.0） |
| `requirements-rl3.7.0-freeze.txt` | 101 | 学習用 PC・追加の freeze |
| `requirements-jetson-nao.txt` | 125 | 実機 Nao（JetPack 4.2.2 / Python 3.6.8 / aarch64） |
| `requirements-jetson-jassy.txt` | 162 | 実機 Jassy（JetPack 4.6.2 / Python 3.7 / aarch64） |

## Nao と Jassy

Nao と Jassy は別の Jetson Nano で、Donkey Car のリポジトリと
PyTorch の入手方法も異なります。

- **Nao**:
  [`991693552/donkeycar_jetson_nano@0656898c14099f105f82945dd481cc6ce606b103`](https://github.com/991693552/donkeycar_jetson_nano/tree/0656898c14099f105f82945dd481cc6ce606b103)。
  PyTorch は stock の `1.1.0a0+b457266`。
- **Jassy**:
  [`ari-viitala/donkeycar@4d8bc923f3c188df4b72057c4fdf4315f5d1ad67`](https://github.com/ari-viitala/donkeycar/tree/4d8bc923f3c188df4b72057c4fdf4315f5d1ad67) と
  [`tawnkramer/gym-donkeycar@4ea670491eaef66178a1ffe3d672c7d4344c51bf`](https://github.com/tawnkramer/gym-donkeycar/tree/4ea670491eaef66178a1ffe3d672c7d4344c51bf)。
  PyTorch はソースから自前ビルドした `1.9.0a0+gitd69c22d`（cp37）。

## Jassy の `torch` 行

[`requirements-jetson-jassy.txt`](requirements-jetson-jassy.txt) の149行目にある次の行は、pyenv を torch として
インストールしたことを表していません。

```text
-e git+https://github.com/pyenv/pyenv.git@…#egg=torch
```

私たちは自前ビルドした torch を editable install しました。
`pip freeze` は、そのソース位置を包む最も近い Git リポジトリだった `~/.pyenv` を
出所として書き出しました。torch の実体は `1.9.0a0+gitd69c22d` です。

requirements には、`file:///`、`git+https://`、
`https://files.pythonhosted.org/…` のように直接 URL、ローカルファイル、
Git コミットを指す行もあります。これらは当時の環境の記録です。

Jassy 向け PyTorch の自前ビルドを含む環境の詳細は
[`../docs/SETUP.md`](../docs/SETUP.md) を参照してください。
