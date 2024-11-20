# FocusCheck
<p>このリポジトリは, CDSLの日本語サイトをバックアップしているデータをリストアした際のテストを実行する際, ブログ全体の固定ページや記事の確認を行う対象を決定し, テストの実行を行うプログラムが入っています.</p>

## 使い方


<p>Python3で構成されています.</p>
<p>仮想環境を読みこむことで実行することが可能です.</p>

### 実行方法

```bash
# Pythonの仮想環境を作成
python3 -m venv .venv
source .venv/bin/activate
pip3 install -U pip
pip3 install -r requirements.txt
```

<p>File: All-Check.py</p>
<p>WP REST API経由で, WordPressのデータベースに記録されているコンテンツ全てを探索します.</p>
<p>コンテンツ全てを探索した際にかかったテストの実行時間の計測を行うプログラムです.</p>

<p>動作条件: WordPressのプラグインである, [WP REST API](https://ja.wp-api.org/) が導入されており, アプリケーションパスワードを生成済みの状態で実行できます.</p>

<p>トップページ, 固定ページ, 投稿記事のうち公開されているものをWP REST API経由で確認を行います. </p>

<p>File: DB-Write.py</p>
<p>閲覧数の差分を取るために, データベースに接続し, WordPressのPluginである, WP Statisticsが取得した統計情報(閲覧数)を保存するプログラムです.</p>

<p>File: FoucsCheck.py</p>
<p>パレートの法則にしたがい, バックアップデータをリストアした際のデータベース(2日分)に記録されている閲覧数を比較します.</p>
<p>その後, トップページ, 固定ページ, 投稿記事の閲覧数を比較し, 閲覧数に差分のあったコンテンツのうち, 差分のあったコンテンツの値の上位2割を対象として定めた際の, テストの実行時間を計測するプログラムです.</p>

### 確認項目
- WordPressのブログコンテンツの確認
    - WordPressのトップページが閲覧できるか
    - 投稿内容の確認ができるか
    - 画像が表示できるか
- WordPressのブログダッシュボードの確認
    - 新しい記事が作成できるか
    - 投稿済みの記事が編集できるか
    - 投稿済みの記事が削除できるか

### 結果の一部:
File: FoucsCheck.py

```pareto-kekka.log
2024-11-11 04:34:33,749 Top page is accessible.
2024-11-11 04:34:33,750 Execution time for check_top_page: 0.18291187286376953 seconds
2024-11-11 04:34:34,005 Top post "/archives/460" is accessible. View count difference: 451
2024-11-11 04:34:34,785 Image "http://c0a21099-website-0916.a910.tak-cslab.org/wp-content/uploads/2020/07/bft1-2.png" is accessible.
2024-11-11 04:34:34,852 Image "http://c0a21099-website-0916.a910.tak-cslab.org/wp-content/uploads/2020/07/bft2.png" is accessible.
...
2024-11-11 04:34:33,749 Top page is accessible.
2024-11-11 04:34:33,750 Execution time for check_top_page: 0.18291187286376953 seconds
2024-11-11 04:34:34,005 Top post "/archives/460" is accessible. View count difference: 451
2024-11-11 04:34:34,785 Image "http://c0a21099-website-0916.a910.tak-cslab.org/wp-content/uploads/2020/07/bft1-2.png" is accessible.
2024-11-11 04:34:34,852 Image "http://c0a21099-website-0916.a910.tak-cslab.org/wp-content/uploads/2020/07/bft2.png" is accessible.
```
