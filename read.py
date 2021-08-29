from flask import Flask, request, render_template

task_list = Task_list
from main import task_list, Task_account, db
import json

aaa = task_list.query.filter(task_list.max == 27).all()
bb = list()
for x in aaa:
    print(x.roomid)
    aa = {
        'roomid': x.roomid,
        'is_pause': x.is_pause,
        'offtime': x.offtime,
        'maxflower': x.maxflower,
        'maxflower_time': x.maxflower_time

    }
    bb.append(aa)
# print(bb)
import time
print(json.dumps(bb))

task_list.query.get(1)



# print(room_control.is_pause("7036515", 1633116132, ""))
