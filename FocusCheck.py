import requests
from requests.auth import HTTPBasicAuth
import logging
from datetime import datetime
import time
import re
import mysql.connector

# WordPressサイトのログイン情報
url_base = 'http://c0a21099-website-0916.a910.tak-cslab.org'
api_url_0915 = 'http://c0a21099-website-0915.a910.tak-cslab.org/wp-json/wp/v2'
api_url_0916 = 'http://c0a21099-website-0916.a910.tak-cslab.org/wp-json/wp/v2'
username = 'your-username'
application_password = 'your-password'
auth = HTTPBasicAuth(username, application_password)

# 日付を取得
date_str = datetime.now().strftime("%Y-%m-%d")

# ログファイルの設定
log_file = f'/home/nissy/website/pareto-new/log/alllog-{date_str}.log'
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s %(message)s')

# キャッシュ無効化のヘッダー
headers = {
    'Cache-Control': 'no-store, no-cache, must-revalidate, proxy-revalidate, max-age=0',
    'Pragma': 'no-cache',
    'Expires': '0'
}

# 実行時間を計測してサマリーを作成するためのリスト
execution_times = []

# 実行時間を計測するデコレーター
def log_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        logging.info('Execution time for %s: %s seconds', func.__name__, elapsed_time)
        print(f'Execution time for {func.__name__}: {elapsed_time} seconds')

        # 実行時間をサマリーに追加
        execution_times.append((func.__name__, elapsed_time))
        return result
    return wrapper

# トップページが閲覧できるか
@log_time
def check_top_page():
    response = requests.get(url_base, headers=headers)
    if response.status_code == 200:
        logging.info('Top page is accessible.')
        print('Top page is accessible.')
    else:
        logging.error('Failed to access top page. Status Code: %s', response.status_code)
        print(f'Failed to access top page. Status Code: {response.status_code}')

# ページコンテンツ内の画像URLを確認し、アクセスできるかをチェックする関数
def check_images_in_content(content):
    image_urls = set(re.findall(r'<img.*?src="(.*?)"', content))
    for image_url in image_urls:
        if image_url.startswith('http://') or image_url.startswith('https://'):
            response = requests.get(image_url, headers=headers)
            if response.status_code == 200:
                logging.info('Image "%s" is accessible.', image_url)
                print(f'Image "{image_url}" is accessible.')
            else:
                logging.error('Failed to access image "%s". Status Code: %s', image_url, response.status_code)
                print(f'Failed to access image "{image_url}". Status Code: {response.status_code}')
        else:
            logging.error('Invalid image URL: %s', image_url)
            print(f'Invalid image URL: {image_url}')

# データベースから対象記事を取得する関数
def get_target_articles_from_database():
    # データベース接続情報
    db_info_0915 = {
        'host': 'c0a21099-website-0915.a910.tak-cslab.org',
        'user': 'your-name',
        'password': 'your-password',
        'database': 'wordpress',
    }

    db_info_0916 = {
        'host': 'c0a21099-website-0916.a910.tak-cslab.org',
        'user': 'your-name',
        'password': 'your-password',
        'database': 'wordpress',
    }

    # データベースに接続してデータを取得する関数
    def fetch_data_from_database(db_info):
        connection = mysql.connector.connect(
            host=db_info['host'],
            user=db_info['user'],
            password=db_info['password'],
            database=db_info['database']
        )

        try:
            cursor = connection.cursor(dictionary=True)
            # wp_nissy_kekka_newテーブルからcleaned_uriとtotal_countを取得
            sql = "SELECT cleaned_uri, total_count FROM wp_nissy_kekka_new"
            cursor.execute(sql)
            result = cursor.fetchall()
            return result
        finally:
            connection.close()

    # 両方のデータベースからデータを取得
    data_0915 = fetch_data_from_database(db_info_0915)
    data_0916 = fetch_data_from_database(db_info_0916)

    # データを辞書形式に変換して比較を容易にする
    dict_0915 = {item['cleaned_uri']: item['total_count'] for item in data_0915}
    dict_0916 = {item['cleaned_uri']: item['total_count'] for item in data_0916}

    # 両方のデータベースで同じcleaned_uriを持つものを対象とし、total_countの差分を計算
    target_articles = []
    for uri in dict_0915.keys():
        if uri in dict_0916:
            diff = dict_0916[uri] - dict_0915[uri]
            target_articles.append((uri, diff))

    # 差分の大きい順に並べ替えて上位20%を取得
    target_articles = sorted(target_articles, key=lambda x: x[1], reverse=True)
    threshold_index = max(1, int(len(target_articles) * 0.2))
    top_20_percent = target_articles[:threshold_index]

    return top_20_percent

# ページ閲覧数の差分を計算し、上位20%のページIDを返す関数
def calculate_differences():
    published_posts_0915 = fetch_all_items('posts', api_url_0915)
    published_posts_0916 = fetch_all_items('posts', api_url_0916)

    views_0915 = {}
    views_0916 = {}

    for post in published_posts_0915:
        # カスタムフィールド 'view_count' を取得する
        view_count = post.get('meta', {}).get('view_count', 0)
        views_0915[post['id']] = view_count

    for post in published_posts_0916:
        # カスタムフィールド 'view_count' を取得する
        view_count = post.get('meta', {}).get('view_count', 0)
        views_0916[post['id']] = view_count

    differences = {}
    for post_id in views_0915.keys():
        if post_id in views_0916:
            diff = views_0916[post_id] - views_0915[post_id]
            differences[post_id] = diff

    sorted_differences = sorted(differences.items(), key=lambda x: x[1], reverse=True)
    threshold_index = max(1, int(len(sorted_differences) * 0.2))
    top_20_percent = sorted_differences[:threshold_index]

    return top_20_percent

# 上位20%のページに対してチェックを実施
@log_time
def check_top_pages_content(top_pages):
    for post_id, diff in top_pages:
        # 修正: API経由でなく、/archives/{post_id}形式でアクセスする
        archive_url = f'http://c0a21099-website-0916.a910.tak-cslab.org{post_id}'
        response = requests.get(archive_url, auth=auth, headers=headers)
        
        if response.status_code == 200:
            content = response.text
            logging.info('Top post "%s" is accessible. View count difference: %s', post_id, diff)
            print(f'Top post "{post_id}" is accessible. View count difference: {diff}')
            check_images_in_content(content)  # ページ内の画像もチェック
        else:
            logging.error('Failed to access top post "%s". Status Code: %s', post_id, response.status_code)
            print(f'Failed to access top post "/archives/{post_id}". Status Code: {response.status_code}')


# 新しい記事が作成できるか
@log_time
def create_post(title, content):
    data = {
        'title': title,
        'content': content,
        'status': 'publish'
    }
    response = requests.post(f'{api_url_0916}/posts', json=data, auth=auth, headers=headers)
    if response.status_code == 201:
        logging.info('Post created successfully: Title "%s"', title)
        print(f'Post created successfully: Title "{title}"')
        return response.json().get('id')  # 作成した記事のIDを返す
    else:
        logging.error('Failed to create post: Title "%s". Status Code: %s', title, response.status_code)
        print(f'Failed to create post: Title "{title}". Status Code: {response.status_code}')
        return None  # エラー時はNoneを返す

# 記事が削除できるか
@log_time
def delete_post(post_id):
    response = requests.delete(f'{api_url_0915}/posts/{post_id}?force=true', auth=auth, headers=headers)
    if response.status_code == 200:
        logging.info('Post deleted successfully: ID %s', post_id)
        print(f'Post deleted successfully: ID {post_id}')
    else:
        logging.error('Failed to delete post: ID %s. Status Code: %s', post_id, response.status_code)
        print(f'Failed to delete post: ID {post_id}. Status Code: {response.status_code}')

# メイン実行部分
if __name__ == "__main__":
    check_top_page()

    # データベースから対象記事を取得
    target_articles = get_target_articles_from_database()

    # 取得した記事に対してAPIでチェックを実施
    check_top_pages_content(target_articles)

    # 新しい記事の作成
    new_post_title = "New Post Title"
    new_post_content = "This is the content of the new post."
    new_post_id = create_post(new_post_title, new_post_content)  # 記事IDを取得

    # 記事の削除 (削除する記事のIDを指定)
    if new_post_id is not None:  # 作成に成功した場合のみ削除を実行
        delete_post(new_post_id)

    # サマリーを表示
    print("\nExecution Times Summary:")
    total_execution_time = sum(exec_time for _, exec_time in execution_times)
    
    # サマリーをログに記録
    for func_name, exec_time in execution_times:
        log_message = f"{func_name}: {exec_time:.2f} seconds"
        print(log_message)
        logging.info(log_message)  # ログファイルにも書き込む
    
    # 合計実行時間をログに記録
    total_time_message = f"Total execution time: {total_execution_time:.2f} seconds"
    print(total_time_message)
    logging.info(total_time_message)
