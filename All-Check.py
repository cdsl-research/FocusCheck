import requests
from requests.auth import HTTPBasicAuth
import logging
from datetime import datetime
import time
import re
import random

# WordPressサイトのログイン情報
url_base = 'http://c0a21099-website-0915.a910.tak-cslab.org'
api_url = f'{url_base}/wp-json/wp/v2'
username = 'your-name'
application_password = 'your-password'
auth = HTTPBasicAuth(username, application_password)

# 日付を取得
date_str = datetime.now().strftime("%Y-%m-%d")

# ログファイルの設定
log_file = f'/home/nissy/website/0915/log/alllog-{date_str}.log'
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s %(message)s')

# キャッシュ無効化のヘッダー
headers = {
    'Cache-Control': 'no-store, no-cache, must-revalidate, proxy-revalidate',
    'Pragma': 'no-cache',
    'Expires': '0'  # または 'Wed, 11 Jan 1984 05:00:00 GMT'
}

# 実行時間を計測してサマリーを作成するためのリスト
execution_times = []
item_counts = []  # 記事や固定ページの件数を記録するリスト

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

# Publishになっている固定ページと記事がすべて表示できるか
def check_published_items(endpoint, item_type):
    def fetch_all_items(endpoint):
        items = []
        page = 1
        while True:
            # ランダムなクエリパラメータを追加してキャッシュバスティング
            random_param = f'r={random.random()}'
            logging.info('Fetching items from: %s?page=%s&%s', f'{api_url}/{endpoint}', page, random_param)
            response = requests.get(f'{api_url}/{endpoint}?per_page=100&page={page}&{random_param}', auth=auth, headers=headers)

            if response.status_code == 200:
                data = response.json()
                if not data:  # データがない場合はループを終了
                    break
                items.extend(data)
                page += 1
            else:
                logging.error('Failed to fetch %s. Status Code: %s, Response: %s', endpoint, response.status_code, response.text)
                print(f'Failed to fetch {endpoint}. Status Code: {response.status_code}, Response: {response.text}')
                break

        return items

    items = fetch_all_items(endpoint)

    # 件数をサマリー用リストに追加
    item_counts.append((item_type, len(items)))

    logging.info('Total number of published %s: %s', item_type, len(items))
    print(f'Total number of published {item_type}: {len(items)}')

    for item in items:
        if item['status'] == 'publish':
            response = requests.get(item['link'], headers=headers)
            if response.status_code == 200:
                logging.info('Published %s "%s" is accessible.', item_type[:-1], item['title']['rendered'])
                print(f'Published {item_type[:-1]} "{item["title"]["rendered"]}" is accessible.')
                check_images_in_content(item['content']['rendered'])
            else:
                logging.error('Failed to access published %s "%s". Status Code: %s', item_type[:-1], item['title']['rendered'], response.status_code)
                print(f'Failed to access published {item_type[:-1]} "{item["title"]["rendered"]}". Status Code: {response.status_code}')

@log_time
def check_published_pages():
    check_published_items('pages', 'pages')

@log_time
def check_published_posts():
    check_published_items('posts', 'posts')

# 記事に紐づいている画像が表示されているか
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

# ログインページにアクセスできるか
@log_time
def check_login_page():
    response = requests.get(f'{url_base}/10gin_cds1', headers=headers)
    if response.status_code == 200:
        logging.info('Login page is accessible.')
        print('Login page is accessible.')
    else:
        logging.error('Failed to access login page. Status Code: %s', response.status_code)
        print(f'Failed to access login page. Status Code: {response.status_code}')

# 新しい記事が作成できるか
@log_time
def create_post(title, content):
    post_data = {
        'title': title,
        'content': content,
        'status': 'private'  # 記事のステータスをprivateに設定
    }
    response = requests.post(f'{api_url}/posts', json=post_data, auth=auth, headers=headers)
    if response.status_code == 201:
        logging.info('Post created successfully: %s', title)
        print(f'Post created successfully: {title}')
        return response.json()['id']
    else:
        logging.error('Failed to create post: %s', response.content)
        logging.error('Status Code: %s', response.status_code)
        print(f'Failed to create post: {response.content}')
        print(f'Status Code: {response.status_code}')
        return None

# 作成された記事が編集できるか
@log_time
def edit_post(post_id, new_content):
    post_data = {
        'content': new_content
    }
    response = requests.post(f'{api_url}/posts/{post_id}', json=post_data, auth=auth, headers=headers)
    if response.status_code == 200:
        logging.info('Post edited successfully: ID %s', post_id)
        print(f'Post edited successfully: ID {post_id}')
    else:
        logging.error('Failed to edit post: ID %s, %s', post_id, response.content)
        logging.error('Status Code: %s', response.status_code)
        print(f'Failed to edit post: ID {post_id}, {response.content}')
        print(f'Status Code: {response.status_code}')

# 作成した記事が削除できるか
@log_time
def delete_post(post_id):
    response = requests.delete(f'{api_url}/posts/{post_id}?force=true', auth=auth, headers=headers)
    if response.status_code == 200:
        logging.info('Post deleted successfully: ID %s', post_id)
        print(f'Post deleted successfully: ID {post_id}')
    else:
        logging.error('Failed to delete post: ID %s, %s', post_id, response.content)
        logging.error('Status Code: %s', response.status_code)
        print(f'Failed to delete post: ID {post_id}, {response.content}')
        print(f'Status Code: {response.status_code}')

# 実行時間と件数のサマリーを出力する関数
def print_summary():
    print("\nExecution Time Summary:")
    logging.info("\nExecution Time Summary:")
    total_time = 0  # 合計実行時間を計算するための変数
    for func_name, exec_time in execution_times:
        print(f"{func_name}: {exec_time:.2f} seconds")
        logging.info(f"{func_name}: {exec_time:.2f} seconds")
        total_time += exec_time  # 実行時間を合計

    # 合計実行時間を表示
    print(f"\nTotal Execution Time: {total_time:.2f} seconds")
    logging.info(f"\nTotal Execution Time: {total_time:.2f} seconds")

    print("\nItem Counts Summary:")
    logging.info("\nItem Counts Summary:")
    for item_type, count in item_counts:
        print(f"Total number of {item_type}: {count}")
        logging.info(f"Total number of {item_type}: {count}")

# テストの実行
check_top_page()
check_login_page()
check_published_pages()
check_published_posts()
new_post_id = create_post('Test Post', 'This is a test post.')
if new_post_id:
    edit_post(new_post_id, 'Updated content for the test post.')
    delete_post(new_post_id)

# サマリーを出力
print_summary()