import datetime

def get_now():
    return datetime.datetime.utcnow()

# 其他可扩展工具函数 

if __name__ == '__main__':
    now = get_now()
    print("当前UTC时间：", now)
    input("按回车退出")