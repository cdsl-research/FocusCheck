# FocusCheck
<p>このリポジトリは, CDSLの日本語サイトをバックアップしているデータをリストアした際のテストを実行する際, ブログ全体の固定ページや記事の確認を行う対象を決定し, テストの実行を行うプログラムが入っています.</p>

## 使い方


<p>Python3で構成されています.</p>
<p>仮想環境を読みこむことで実行することが可能です.</p>

---

### 実行方法

```bash
# Pythonの仮想環境を作成
python3 -m venv .venv
source .venv/bin/activate
pip3 install -U pip
pip3 install -r requirements.txt
```

---

<p>File: All-Check.py</p>
<p>WP REST API経由で, WordPressのデータベースに記録されているコンテンツ全てを探索します.</p>
<p>コンテンツ全てを探索した際にかかったテストの実行時間の計測を行うプログラムです.</p>

<p>動作条件: WordPressのプラグインである, [WP REST API](https://ja.wp-api.org/) が導入されており, アプリケーションパスワードを生成済みの状態で実行できます.</p>

<p>トップページ, 固定ページ, 投稿記事のうち公開されているものをWP REST API経由で確認を行います. </p>

---

<p>File: DB-Write.py</p>
<p>閲覧数の差分を取るために, データベースに接続し, WordPressのPluginである, WP Statisticsが取得した統計情報(閲覧数)を保存するプログラムです.</p>

---

<p>File: FoucsCheck.py</p>
<p>パレートの法則にしたがい, バックアップデータをリストアした際のデータベース(2日分)に記録されている閲覧数を比較します.</p>
<p>その後, トップページ, 固定ページ, 投稿記事の閲覧数を比較し, 閲覧数に差分のあったコンテンツのうち, 差分のあったコンテンツの値の上位2割を対象として定めた際の, テストの実行時間を計測するプログラムです.</p>

---

### 確認項目
- WordPressのブログコンテンツの確認
    - WordPressのトップページが閲覧できるか
    - 投稿内容の確認ができるか
    - 画像が表示できるか
- WordPressのブログダッシュボードの確認
    - 新しい記事が作成できるか
    - 投稿済みの記事が編集できるか
    - 投稿済みの記事が削除できるか

---

### 結果の一部:
File: FoucsCheck.py

```bash
2024-11-11 04:34:33,749 Top page is accessible.
2024-11-11 04:34:33,750 Execution time for check_top_page: 0.18291187286376953 seconds
2024-11-11 04:34:34,005 Top post "/archives/460" is accessible. View count difference: 451
2024-11-11 04:34:34,785 Image "http://c0a21099-website-0916.a910.tak-cslab.org/wp-content/uploads/2020/07/bft1-2.png" is accessible.
2024-11-11 04:34:34,852 Image "http://c0a21099-website-0916.a910.tak-cslab.org/wp-content/uploads/2020/07/bft2.png" is accessible.
...
2024-11-11 04:35:10,180 Top post "/archives/3291" is accessible. View count difference: 7
2024-11-11 04:35:10,187 Image "http://c0a21099-website-0916.a910.tak-cslab.org/wp-content/uploads/2023/02/IMG_20230209_171019-2-scaled.jpg" is accessible.
2024-11-11 04:35:10,196 Image "http://c0a21099-website-0916.a910.tak-cslab.org/wp-content/uploads/2023/02/IMG_8998-scaled.jpg" is accessible.
2024-11-11 04:35:10,203 Image "http://c0a21099-website-0916.a910.tak-cslab.org/wp-content/uploads/2023/02/IMG_8993-scaled.jpg" is accessible.
2024-11-11 04:35:10,210 Image "http://c0a21099-website-0916.a910.tak-cslab.org/wp-content/uploads/2023/02/IMG_20230209_134927-1-scaled.jpg" is accessible.
2024-11-11 04:35:10,217 Image "http://c0a21099-website-0916.a910.tak-cslab.org/wp-content/uploads/2023/02/IMG_8992-scaled.jpg" is accessible.
2024-11-11 04:35:10,222 Image "http://c0a21099-website-0916.a910.tak-cslab.org/wp-content/uploads/2023/02/IMG_8994-scaled.jpg" is accessible.
2024-11-11 04:35:10,226 Image "http://c0a21099-website-0916.a910.tak-cslab.org/wp-content/uploads/2023/02/IMG_8990-1-scaled.jpg" is accessible.
2024-11-11 04:35:10,232 Image "http://c0a21099-website-0916.a910.tak-cslab.org/wp-content/uploads/2023/02/IMG_20230209_164637-scaled.jpg" is accessible.
2024-11-11 04:35:10,238 Image "http://c0a21099-website-0916.a910.tak-cslab.org/wp-content/uploads/2023/02/IMG_20230209_130803-scaled.jpg" is accessible.
2024-11-11 04:35:10,267 Top post "/archives/3060" is accessible. View count difference: 7
2024-11-11 04:35:10,298 Top post "/archives/4491" is accessible. View count difference: 7
2024-11-11 04:35:10,326 Top post "/archives/2826" is accessible. View count difference: 7
2024-11-11 04:35:10,355 Top post "/archives/3450" is accessible. View count difference: 7
2024-11-11 04:35:10,355 Execution time for check_top_pages_content: 4.331315994262695 seconds
2024-11-11 04:35:10,468 Post created successfully: Title "New Post Title"
2024-11-11 04:35:10,468 Execution time for create_post: 0.11319565773010254 seconds
2024-11-11 04:35:10,494 Failed to delete post: ID 6177. Status Code: 404
2024-11-11 04:35:10,494 Execution time for delete_post: 0.02551865577697754 seconds
2024-11-11 04:35:10,494 check_top_page: 1.12 seconds
2024-11-11 04:35:10,494 check_top_pages_content: 4.33 seconds
2024-11-11 04:35:10,494 create_post: 0.11 seconds
2024-11-11 04:35:10,494 delete_post: 0.03 seconds
2024-11-11 04:35:10,494 Total execution time: 5.59 seconds
```

## Terminalでの実行結果:
<p>File: All-Check.py</p>
<p>実行開始時</p>

![image](https://github.com/user-attachments/assets/8fc769a6-ded5-4819-9a63-f38c3d00d2b2)

<p>実行終了時</p>

![image](https://github.com/user-attachments/assets/c53db627-27be-4fb2-856c-2454b598ddfb)


<p>File : FocusCheck.py</p>
<p>実行開始時</p>

![image](https://github.com/user-attachments/assets/cb6d0e11-3493-4719-b79a-708c1b00549b)

<p>実行終了時</p>

![image](https://github.com/user-attachments/assets/3648baa9-9d29-4569-8e01-d411b1a336a4)


