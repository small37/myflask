# coding=UTF-8
from flask import Flask, request, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
import os, sys, time, logging
from multiprocessing import Process

logging.basicConfig(level=logging.NOTSET)
# logging.basicConfig(format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s',level=logging.DEBUG)

'''==========config============'''
global config
config = {
    "flover": 11
    , "sync_timeout": 5 * 60  # 账号超时%分钟释放
    , "ver": 1.0
    , "webkey1": "7a7a1f9ff866b2559c0455edc3c3324aaff53b9bdb9ec0a7"
    , "webkey2": "c1a7c2a6c3a5c7a2"
    , "maxlower": 500
}

app = Flask(__name__)

if sys.platform.startswith("win"):
    prefix = 'sqlite:///'
else:
    prefix = 'sqlite:////'
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'xxxxx'

# app.config["SQLALCHEMY_ECHO"] = True #显示原始sql
db = SQLAlchemy(app)


class Task_account(db.Model):
    __tablename__ = "task_account"
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer)
    user = db.Column(db.String(22), unique=True)
    password = db.Column(db.String(22))
    uidd = db.Column(db.String(22))
    lv = db.Column(db.Integer)
    level = db.Column(db.Integer)
    accesstoken = db.Column(db.String(500))
    bin = db.Column(db.Integer)
    servername = db.Column(db.String(50))
    ip = db.Column(db.String(15))
    last_time = db.Column(db.Integer)
    number = db.Column(db.Integer)
    number_max = db.Column(db.Integer)
    change_name = db.Column(db.Integer)
    room_s = db.Column(db.String(500))
    cookie = db.Column(db.String(500))

    def getonline_rooms(self):  # 返回在线账号数值
        # pp1 = self.query.filter(self.id != "13908").count()
        pp1 = self.query.filter(Task_account.servername != "").count()
        return pp1


class Task_list(db.Model):
    __tablename__ = "task_list"
    id = db.Column(db.Integer, primary_key=True)
    is_pause = db.Column(db.Integer, default=0)
    webtype = db.Column(db.Integer, default=0)
    userlevel = db.Column(db.Integer, default=0)
    uid = db.Column(db.Integer)
    roomid = db.Column(db.Integer, unique=False, nullable=False)
    max = db.Column(db.Integer)
    starttime = db.Column(db.Integer, default="")
    endtime = db.Column(db.Integer)
    offtime = db.Column(db.Text)
    first = db.Column(db.Integer)
    tel = db.Column(db.String(40))
    baktxt = db.Column(db.Text)
    maxflower = db.Column(db.Integer, default=0)
    maxflower_time = db.Column(db.Integer, default=0)


'''=========================================='''


@app.route('/')
def index():
    # Task_account().getonline_rooms()
    # sync_ac_task()
    # unquest_key('@timeout')  # 定期释放超时账号
    return "我是一个主页"


# 信息更新专用
@app.route('/updata/<_class>/<data>')
def updata(_class, data):
    if _class == "account":
        return data
    elif _class == "roominfo":
        return data

    return ""


#  et_my_task  同步账号最新任务
@app.route('/syn_mytask/<servername>')
def syn_mytask(servername):
    rs = Task_account.query.filter(
        Task_account.servername == servername).all()
    bb = list()
    # print(rs)
    for x in rs:  # type:Task_account
        x.last_time = int(time.time())
        aa = {
            'user': x.user,
            'password': x.password,
            'cookie': x.cookie,
            'accesstoken': x.accesstoken,
            'change_name': x.change_name,
            'room_s': x.room_s,  # 任务房间集合 格式 7008888,7000333,
            'lv': x.lv,  # 账号真实等级
            'md5key1': config["webkey1"],
            'md5key2': config["webkey2"],
            'ver': config["ver"],
            'flover': config["flover"]

        }
        bb.append(aa)
    db.session.commit()
    return jsonify(bb)


# 获取客户端ip
@app.route('/ip')
def ip():
    return jsonify({"ip": request.remote_addr})


# 请求分配一个账号 给客户端 servername=客户端标识，level账号分类等级
@app.route('/request_key/<servername>/<level>/<num>')
def request_key(servername, level, num=3):
    rs = Task_account.query.filter(
        Task_account.servername == "", Task_account.bin == 0, Task_account.level == level
    ).limit(num).all()
    bb = list()
    for x in rs:  # type:Task_account
        x.servername = servername
        x.last_time = int(time.time())
        x.ip = request.remote_addr
        aa = {
            'user': x.user,
            'password': x.password,
            'cookie': x.cookie,
            'accesstoken': x.accesstoken,
            'number': x.number,
            'number_max': x.number_max,
            'room_s': x.room_s,  # 任务房间集合 格式 7008888,7000333,
            'lv': x.lv  # 账号真实等级

        }
        bb.append(aa)
    db.session.commit()
    return jsonify(bb)


# 立即释放标识客户端账号
@app.route('/unquest_key/<servername>')
def unquest_key(servername):
    if servername == "@all":
        rs = Task_account.query.filter(Task_account.servername != '')
        for _rs in rs.all():  # type:Task_account
            _rs.room_s = ''
            _rs.servername = ''
        db.session.commit()
        return jsonify('全部释放-ok')
    if servername == "@timeout":
        rs = Task_account.query.filter(Task_account.servername != "")
        for _rs in rs.all():  # type:Task_account
            t = int(time.time()) - _rs.last_time

            if int(t) > int(config["sync_timeout"]):
                _rs.room_s = ''
                _rs.servername = ''
                _rs.ip = ''
        db.session.commit()
        return ""
    else:
        rs = Task_account.query.filter(Task_account.servername == servername)
        # print(rs.count(), servername)
        for _rs in rs.all():  # type:Task_account
            _rs.room_s = ''
            _rs.servername = ''
            _rs.ip = ''
        db.session.commit()
        return jsonify("释放了")


# 获取房间列表
@app.route('/getrooms')
def get_rooms():
    aaa = Task_list.query.filter(Task_list.is_pause >= 0).all()
    bb = list()
    for x in aaa:
        # print(x.roomid)
        aa = {
            'roomid': x.roomid,
            'is_pause': x.is_pause,
            'offtime': x.offtime,
            'maxflower': x.maxflower,
            'maxflower_time': x.maxflower_time

        }
        bb.append(aa)

    return jsonify(bb)


# 房间自动补号,自动剔除下播房间
def sync_ac_task():
    _tem_coun = 0
    # rs = Task_list.query.filter(Task_list.is_pause == 1).all()
    rs = Task_list.query.filter(Task_list.is_pause >= 0).all()
    for x in rs:
        if x.is_pause == 0:
            rs1 = Task_account.query.filter(Task_account.room_s.like("%," + str(x.roomid) + "%"))  # 所有包含该房间的
            for _rs1 in rs1.all():
                # print('_rs1.room_s', _rs1.room_s, x.roomid)
                _room_s = _rs1.room_s.split(',')
                _room_s.remove(str(x.roomid))
                _rs1.room_s = ",".join(_room_s)
                _tem_coun += 1
            db.session.commit()
        else:
            # continue
            rs1 = Task_account.query.filter(Task_account.servername != "").all()  # type:Task_account
            _in_max = 0  # 房间以挂账号数

            for _rs1 in rs1:  # type:Task_account
                if str(x.roomid) in _rs1.room_s: _in_max += 1
            _cha = x.max - _in_max  # 得出需要补充差值
            # print(">>>", _cha)
            if _cha > 0:
                counter = 0
                for _rs1 in rs1:  # type:Task_account
                    if str(x.roomid) not in _rs1.room_s:
                        # print(x.roomid, "补+1", _rs1.room_s)
                        room_s = _rs1.room_s.split(',')
                        room_s.append(str(x.roomid))
                        _rs1.room_s = ",".join(room_s)
                        counter += 1
                        if counter >= _cha:
                            break
                db.session.commit()
                # print("补了>>", counter)


# 定式任务多进程,可以作为 房间状态检测
def thread_run(time1=10):
    while True:
        t = f'[定式任务]>>>{time1}秒一次'
        sync_ac_task()
        app.logger.info("TimeDef>>sync_ac_task()")
        unquest_key("@timeout")  # 定期释放超时账号
        app.logger.info('unquest_key("@timeout")')
        time.sleep(int(time1))


if __name__ == '__main__':
    app.logger.info("服务器启动.....")
    p = Process(target=thread_run, args=(60,))
    p.start()  # 定式任务进程
    # handler = logging.FileHandler('flask.log')
    # app.logger.addHandler(handler)
    app.run('0.0.0.0', 88)
