import os

def collect_files(dir):
    filelist = []
    for parent, dirnames, filenames in os.walk(dir):
        for filename in filenames:
            if filename.endswith('.py'):
                filelist.append(os.path.join(parent, filename))
    return filelist

def calc_linenum(file):
    with open(file) as fp:
        content_list = fp.readlines()
        code_num = 0
        for content in content_list:
            content = content.strip()
            if content != '':
                code_num += 1
    return code_num

if __name__ == '__main__':
    base_path = './manimlib'  # 代码目录
    files = collect_files(base_path)
    total_code_num = 0
    for file in files:
        total_code_num += calc_linenum(file)
    print('总代码行数：', total_code_num)