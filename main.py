
import requests
import subprocess
import sys
import os


base_params = {
    'app': 'web',
    'kav': '100',
    'av': '100',
    'hav': '100',
    'version': '3.0.0.0'}

# 要下载题目的省份
locations = ["江西", "重庆"]

# 粉笔账号密码
username = ''
password = ''


def get_js_pwd(password):

    script_dir = sys.path[0]
    # 指定要调用的 JavaScript 文件
    js_file = os.path.join(script_dir, "script.js")

    # 构建命令行参数
    args = ["node", js_file, password]

    # 执行命令并捕获输出
    result = subprocess.run(args, capture_output=True)

    return result.stdout.decode('utf-8').replace('\n', '')


def login(user, pwd, s: requests.Session):
    params = {
        'kav': '12',
        'app': 'web',
    }
    data = {
        'password': get_js_pwd(pwd),
        'persistent': 'true',
        'app': 'web',
        'phone': user,
    }
    response = s.post('https://login.fenbi.com/api/users/loginV2?kav=12&app=web&av=80', params=params,
                      data=data)
    data = response.json()
    return data


def get_label_ids(s: requests.Session):
    # 获取试卷列表
    url = 'https://tiku.fenbi.com/api/xingce/subLabels'
    params = base_params
    r = s.get(url, params=params)
    return r.json()


def get_papers(location, label_id, page_size, s: requests.Session):
    # 获取试卷列表
    params = {'toPage': '0',
              'pageSize':  page_size,
              'labelId': label_id,
              'app': 'web',
              'kav': '100',
              'av': '100',
              'hav': '1',
              'version': '3.0.0.0'}

    url = 'https://tiku.fenbi.com/api/xingce/papers/'
    r = s.get(url, params=params)

    data = r.json()

    ls = data.get('list')
    for l in ls:
        name = l.get('name')
        exercise = l.get('exercise')
        form = {
            'type': '1',
            'paperId': l.get('id'),
            'exerciseTimeMode': '2'
        }
        if exercise is None:
            r = s.post(
                'https://tiku.fenbi.com/api/xingce/exercises', params=params, data=form)
            data = r.json()
            exercise_id = data.get('id')
        else:
            exercise_id = exercise.get('id')
        download_paper(os.path.join(
            location, name.replace('/', '_')), exercise_id, s)

    return


def download_paper(path, exercise_id, s: requests.Session):
    url = 'https://urlimg.fenbi.com/api/pdf/tiku/xingce/exercise/' + \
        str(exercise_id)

    params = base_params
    r = s.get(url, params=params)
    with open(path+'.pdf', 'wb') as f:
        f.write(r.content)
    f.close()


def mkfile():
    for location in locations:
        if not os.path.exists(location):
            os.mkdir(location)


def main():
    mkfile()
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36',
    }
    s = requests.session()
    s.headers = headers
    data = login(username, password, s)
    code = data.get('code')
    if not code == 1:
        print('登陆失败', data.get('msg'))
        return
    data = get_label_ids(s)
    for d in data:
        location = d.get('name')
        if location in locations:
            label_meta = d.get('labelMeta')
            page_size = label_meta.get('paperCount')
            label_id = label_meta.get('id')

            get_papers(location, label_id, page_size,  s)


if __name__ == '__main__':
    main()
