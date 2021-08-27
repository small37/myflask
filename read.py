from flask import Flask, request, render_template
from main import Task_list, Task_account, db
import json

# aaa = Task_list.query.filter(Task_list.max == 27).all()
# bb = list()
# for x in aaa:
#     print(x.roomid)
#     aa = {
#         'roomid': x.roomid,
#         'is_pause': x.is_pause,
#         'offtime': x.offtime,
#         'maxflower': x.maxflower,
#         'maxflower_time': x.maxflower_time
#
#     }
#     bb.append(aa)
#
# # print(bb)
# print(json.dumps(bb))

# is_pause

import time





# print(room_control.is_pause("7036515", 1633116132, ""))
