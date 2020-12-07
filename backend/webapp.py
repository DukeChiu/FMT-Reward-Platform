from application.app import app, db, logger
from application.configration import app_config
from flask import request, make_response, jsonify
from sqlalchemy import and_
from models.user import User
from models.task import Task
from models.apply import Apply
from models.apply_task import ApplyTask
from tools import code
from tools import crypto
from tools import redis_operation
from tools import send_email
import random
import os
from tools import check

front = '/webapp/'


def resp(cookie=None, data=None):
    response = make_response(jsonify(data))
    if cookie:
        for i in cookie:
            response.set_cookie(i, cookie[i])
    return response


def auth_judge(req, second: int) -> str:
    res_c = ''
    if 'auth' in req.cookies:
        res = redis_operation.redis_exist_prolong(req.cookies.get('auth'), second)
        # print(res)
        if res == '-1':
            redis_operation.redis_exist_del(req.cookies.get('auth'))
            # redis_operation.redis_exist_del(redis_operation.redis_get(request.cookies.get('auth')))
        elif res:
            redis_operation.redis_exist_prolong(redis_operation.redis_get(req.cookies.get('auth')), second)
        if res:
            return res
    return ''


@app.route(front + 'vcode', methods=['get'])
def v_code():
    try:
        cookie = request.cookies['jsonverify']
    except Exception as e:
        pass
    else:
        redis_operation.redis_del(cookie)
    # this is for redis operation, remove the cookies in redis
    key, img = code.v_key()
    ecode_key = crypto.md5_encode(key)
    response = make_response(img)
    response.headers['content-type'] = 'image/png'
    response.set_cookie('jsonverify', ecode_key)
    if redis_operation.redis_set(ecode_key, key, 90):
        return response
    return ''


@app.route(front + 'auth', methods=['POST'])
def auth():
    res = auth_judge(request, 600)
    data = {'code': 0, 'msg': {'errmsg': '登录失效'}}
    if res and res != '-1':
        data['code'] = 1
        data['msg']['errmsg'] = '成功'
    elif res == '-1':
        data['code'] = -2
        data['msg']['errmsg'] = '异地登录'
    return resp(data=data)


@app.route(front + 'getInfo', methods=['POST'])
def get_info():
    res = auth_judge(request, 600)
    data = {'code': 0, 'msg': {'errmsg': '失效'}}
    if res and res != '-1':
        try:
            user = User.query.filter_by(id=res).first()
        except Exception as e:
            logger.error(str(e))
            # return resp(data={'code': 0, 'msg': {'errmsg': '拉取信息失败！'}})
            data['code'] = 0
            data['msg']['errmsg'] = '拉取信息失败'
        else:
            data = {'code': 1, 'msg': {'errmsg': 'ok', 'info': {'user': user.to_json()}}}
    return resp(data=data)


@app.route(front + 'logout', methods=['POST'])
def logout():
    if 'auth' in request.cookies:
        if redis_operation.redis_exist_del(request.cookies.get('auth')) and \
                redis_operation.redis_exist_del(redis_operation.redis_get(request.cookies.get('auth'))):
            return resp(data={'code': 1, 'msg': {'errmsg': '退出成功！'}})
    return resp(data={'code': 0, 'msg': {'errmsg': '无效请求'}})


@app.route(front + 'login', methods=['POST'])
def login():
    try:
        cookie = request.cookies['jsonverify']
    except Exception as e:
        return resp(data={'code': -1, 'msg': {'errmsg': '无效请求'}})
    if not redis_operation.redis_exist_del(cookie):
        return resp(data={'code': -1, 'msg': {'errmsg': '无效请求'}})
    params = request.values if request.values else request.json
    if params is None:
        return resp(data={'code': -1, 'msg': {'errmsg': '缺少参数'}})
    if 'email' not in params or 'pwd' not in params or 'code' not in params:
        return resp(data={'code': -1, 'msg': {'errmsg': '缺少参数'}})
    if crypto.md5_encode(params['code']) != cookie:
        return resp(data={'code': -1, 'msg': {'errmsg': '无效验证码'}})
    try:
        user = User.query.filter_by(email=params['email']).first()
    except Exception as e:
        logger.error(str(e))
        return resp(data={'code': -1, 'msg': {'errmsg': '无法拉取信息'}})
    if user is None:
        return resp(data={'code': 0, 'msg': {'errmsg': '用户未注册'}})
    encode_pwd = crypto.md5_encode(params['pwd'])
    if user.pwd == encode_pwd:
        if user.is_on:
            cookies = {'auth': crypto.md5_encode(crypto.rsa_encode(params['email']))}
            redis_operation.redis_set(cookies['auth'], user.id, 600)
            res = redis_operation.redis_get_set(user.id, cookies['auth'], 600)
            # print(res)
            redis_operation.redis_set(res, '-1', 600)
            return resp(cookie=cookies, data={'code': 1, 'msg': {'errmsg': '成功'}})
        return resp(data={'code': 0, 'msg': {'errmsg': '账号尚未完成注册'}})
    return resp(data={'code': 0, 'msg': {'errmsg': '密码错误！'}})


@app.route(front + 'register', methods=['POST'])
def register():
    try:
        cookie = request.cookies['jsonverify']
    except Exception as e:
        return resp(data={'code': -1, 'msg': {'errmsg': '无效请求'}})
    params = request.values if request.values else request.json
    if params is None:
        return resp(data={'code': -1, 'msg': {'errmsg': '缺少参数'}})
    if 'email' not in params or 'pwd' not in params or 'username' not in params:
        return resp(data={'code': 0, 'msg': {'errmsg': '缺少参数'}})
    try:
        user = User.query.filter_by(email=params['email']).first()
    except Exception as e:
        logger.error(str(e))
        return resp(data={'code': 0, 'msg': {'errmsg': '获取信息失败'}})
    if user:
        return resp(data={'code': 0, 'msg': {'errmsg': '邮箱已注册'}})
    icons = os.listdir('media/icon')
    icon = random.choice(icons)
    user = User(params['email'], crypto.md5_encode(params['pwd']), params['username'], 0, icon)
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        logger.error(str(e))
        return resp(data={'code': 0, 'msg': {'errmsg': '注册失败'}})
    encode = crypto.rsa_encode(params['email'])
    # print(encode)
    if send_email.send({'email': params['email'], 'url': app_config.base_host + encode}):
        return resp(data={'code': 1, 'msg': {'errmsg': '注册成功，等待邮箱验证'}})
    return resp(data={'code': 0, 'msg': {'errmsg': '无效邮箱或验证信息发送失败'}})


@app.route(front + 'verifyEmail', methods=['POST'])
def verify_email():
    params = request.values if request.values else request.json
    if params is None:
        return resp(data={'code': 0, 'msg': {'errmsg': '缺少参数'}})
    if 'code' not in params:
        return resp(data={'code': 0, 'msg': {'errmsg': '无效请求'}})
    else:
        # print(params['code'])
        res = crypto.rsa_decode(params['code'])
        # print(res)
        if res:
            try:
                user = User.query.filter_by(email=res).first()
                if user.is_on:
                    return resp(data={'code': -1, 'msg': {'errmsg': '已验证'}})
                else:
                    user.is_on = True
                    db.session.commit()
                    return resp(data={'code': 1, 'msg': {'errmsg': '验证成功'}})
            except Exception as e:
                logger.error(str(e))
                return resp(data={'code': 0, 'msg': {'errmsg': '验证失败'}})
        return resp(data={'code': 0, 'msg': {'errmsg': '无效验证'}})



@app.route(front + 'getAll', methods=['POST'])
def get_all():
    params = request.values if request.values else request.json
    if params is None or 'page' not in params or 'model' not in params:
        page = 1000000000
        model = 'time'
    else:
        page = int(params['page'])
        model = params['model']
    # print(page)
    # print(params['model'])
    # res = auth_judge(request, 600)
    if model == 'time':
        try:
            task = db.session.query(Task).filter(and_(
                Task.id.notin_(db.session.query(Apply.task).filter(Apply.is_on == True)), Task.id < page)).order_by(
                Task.id.desc()).limit(10)
        except Exception as e:
            logger.error(str(e))
            return resp(data={'code': 0, 'msg': {'errmsg': '查询失败'}})
    else:
        try:
            task1 = db.session.query(Task).filter(and_(
                Task.id.notin_(db.session.query(Apply.task).filter(Apply.is_on == True)), Task.price.like(str(page)+'%'),
                                                                                          Task.id > int(params[
                                                                                                            'model']))).order_by(
                Task.price.desc()).limit(10)
            task2 = db.session.query(Task).filter(and_(
                Task.id.notin_(db.session.query(Apply.task).filter(Apply.is_on == True)), Task.price < page)).order_by(
                Task.price.desc()).limit(10)
            task = task1.union(task2)
        except Exception as e:
            logger.error(str(e))
            return resp(data={'code': 0, 'msg': {'errmsg': '查询失败'}})
    info = [i.to_json() for i in task]
    # print(task)
    return resp(data={'code': 1, 'msg': {'errmsg': '成功', 'info': info}})


@app.route(front + 'getTaskDetails', methods=['POST'])
def get_task_details():
    res = auth_judge(request, 600)
    if res and res != '-1':
        params = request.values if request.values else request.json
        if params is None or 'task' not in params:
            return resp(data={'code': 0, 'msg': {'errmsg': '缺少参数'}})
        try:
            task = Task.query.filter_by(id=params['task']).first()
            apply = Apply.query.filter_by(task=params['task'], apply_user=res).first()
            apply_on = Apply.query.filter_by(task=params['task'], is_on=True).first()
            if task:
                user = User.query.filter_by(id=task.initiator).first()
        except Exception as e:
            logger.error(str(e))
            return resp(data={'code': 0, 'msg': {'errmsg': '获取失败'}})
        info = {'apply': 1, 'contact': '', 'user': ''}
        if task is None:
            return resp(data={'code': 0, 'msg': {'errmsg': '任务不存在'}})
        if user:
            info['user'] = user.to_json()
        # print(res)
        # print(task.initiator)
        if res == str(task.initiator):
            info['apply'] = 0
            info['contact'] = task.contact
        elif apply:
            info['apply'] = -1
            if apply.is_on:
                info['contact'] = task.contact
            elif apply_on:
                info['apply'] = 999
        return resp(data={'code': 1, 'msg': {'errmsg': '成功', 'info': info}})
    return resp(data={'code': -1, 'msg': {'errmsg': '登录失效'}})


@app.route(front + 'getApplyDetails', methods=['POST'])
def get_apply_details():
    res = auth_judge(request, 600)
    if res and res != '-1':
        params = request.values if request.values else request.json
        if params is None or 'task' not in params:
            return resp(data={'code': 0, 'msg': {'errmsg': '缺少参数'}})
        try:
            task = Task.query.filter_by(id=params['task']).first()
        except Exception as e:
            logger.error(str(e))
            return resp(data={'code': 0, 'msg': {'errmsg': '获取失败'}})
        if task is None:
            return resp(data={'code': 0, 'msg': {'errmsg': '任务不存在'}})
        if str(task.initiator) != res:
            return resp(data={'code': 0, 'msg': {'errmsg': '用户无权限'}})
        try:
            user = db.session.query(Apply.is_on, User, Apply.rate).filter_by(task=params['task']).join(User,
                                                                                                       Apply.apply_user == User.id).order_by(
                Apply.is_on.desc()).all()
        except Exception as e:
            logger.error(str(e))
            return resp(data={'code': 0, 'msg': {'errmsg': '获取失败'}})
        info = []
        for i in user:
            if i[0]:
                info.insert(0,
                            {'is_on': i[0], 'user': i[1].to_json(), 'rate': -1 if i[2] == -1 or i[2] is None else i[2]})
            else:
                info.append({'is_on': i[0], 'user': i[1].to_json(), 'rate': -1})
        return resp(data={'code': 1, 'msg': {'errmsg': '成功', 'info': info}})
    return resp(data={'code': -1, 'msg': {'errmsg': '登录失效'}})


@app.route(front + 'getSelf', methods=['POST'])
def get_self():
    res = auth_judge(request, 600)
    print(res)
    if res and res != '-1':
        try:
            task = Task.query.filter_by(initiator=res).order_by(Task.id.desc()).all()
            apply = db.session.query(Task).filter(
                Task.id.in_(db.session.query(Apply.task).filter_by(apply_user=int(res)))).order_by(
                Task.id.desc()).all()
        except Exception as e:
            logger.error(str(e))
            return resp(data={'code': 0, 'msg': {'errmsg': '获取失败'}})
        print(task, apply)
        info = {'task': [i.to_json() for i in task], 'apply': [j.to_json() for j in apply]}
        return resp(data={'code': 1, 'msg': {'errmsg': '成功', 'info': info}})
    return resp(data={'code': -1, 'msg': {'errmsg': '登录失效'}})


@app.route(front + 'createTask', methods=['POST'])
def create_task():
    res = auth_judge(request, 600)
    if res and res != '-1':
        params = request.values if request.values else request.json
        if params is None or 'title' not in params or 'disc' not in params or 'price' not in params or 'contact' not in params:
            return resp(data={'code': 0, 'msg': {'errmsg': '缺少参数'}})
        if check.get_res(params['title']) == -1 or check.get_res(params['disc']) == -1:
            return resp(data={'code': 0, 'msg': {'errmsg': '发布内容中含违禁内容， 请谨慎操作'}})
        try:
            task = Task(params['title'], params['disc'], params['price'], params['contact'], res)
            db.session.add(task)
            db.session.commit()
        except Exception as e:
            logger.error(str(e))
            return resp(data={'code': 0, 'msg': {'errmsg': '添加失败'}})
        return resp(data={'code': 1, 'msg': {'errmsg': '添加成功'}})
    return resp(data={'code': -1, 'msg': {'errmsg': '登录失效'}})


@app.route(front + 'delTask', methods=['POST'])
def del_task():
    res = auth_judge(request, 600)
    if res and res != '-1':
        params = request.values if request.values else request.json
        if params is None or 'id' not in params:
            return resp(data={'code': 0, 'msg': {'errmsg': '缺少参数'}})
        try:
            task = Task.query.filter_by(id=params['id']).first()
        except Exception as e:
            logger.error(str(e))
            return resp(data={'code': 0, 'msg': {'errmsg': '删除失败'}})
        if task is None:
            return resp(data={'code': 0, 'msg': {'errmsg': '任务不存在'}})
        if str(task.initiator) != res:
            return resp(data={'code': 0, 'msg': {'errmsg': '用户无权限'}})
        try:
            apply = Apply.query.filter_by(task=params['id']).all()
            for i in apply:
                db.session.delete(i)  # 级联删除
            db.session.delete(task)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error(str(e))
            return resp(data={'code': 0, 'msg': {'errmsg': '删除失败'}})
        return resp(data={'code': 1, 'msg': {'errmsg': '删除成功'}})
    return resp(data={'code': -1, 'msg': {'errmsg': '登录失效'}})


@app.route(front + 'apply', methods=['POST'])
def task_apply():
    res = auth_judge(request, 600)
    if res and res != '-1':
        params = request.values if request.values else request.json
        if params is None or 'task' not in params:
            return resp(data={'code': 0, 'msg': {'errmsg': '缺少参数'}})
        try:
            task = Task.query.filter_by(id=params['task']).first()
            apply = Apply.query.filter_by(task=params['task'], apply_user=res).first()
        except Exception as e:
            logger.error(str(e))
            return resp(data={'code': 0, 'msg': {'errmsg': '申请失败'}})
        if task is None:
            return resp(data={'code': 0, 'msg': {'errmsg': '任务不存在'}})
        if str(task.initiator) == res:
            return resp(data={'code': 0, 'msg': {'errmsg': '不能申请自己的任务'}})
        if apply:
            return resp(data={'code': 0, 'msg': {'errmsg': '已经申请过了'}})
        apply = Apply(params['task'], res)
        try:
            db.session.add(apply)
            db.session.commit()
        except Exception as e:
            logger.error(str(e))
            return resp(data={'code': 0, 'msg': {'errmsg': '申请失败'}})
        return resp(data={'code': 1, 'msg': {'errmsg': '申请成功'}})
    return resp(data={'code': -1, 'msg': {'errmsg': '登录失效'}})


@app.route(front + 'agree', methods=['POST'])
def agree():
    res = auth_judge(request, 600)
    if res and res != '-1':
        params = request.values if request.values else request.json
        if params is None or 'task' not in params or 'apply_user' not in params:
            return resp(data={'code': 0, 'msg': {'errmsg': '缺少参数'}})
        try:
            task = Task.query.filter_by(id=params['task'], initiator=res).first()
        except Exception as e:
            logger.error(str(e))
            return resp(data={'code': 0, 'msg': {'errmsg': '失败'}})
        if task is None:
            return resp(data={'code': 0, 'msg': {'errmsg': '用户无权限'}})
        try:
            apply = Apply.query.filter_by(task=params['task'], is_on=True).first()
        except Exception as e:
            logger.error(str(e))
            return resp(data={'code': 0, 'msg': {'errmsg': '失败'}})
        if apply:
            return resp(data={'code': 0, 'msg': {'errmsg': '无法更改'}})
        try:
            apply = Apply.query.filter_by(task=params['task'], apply_user=params['apply_user']).first()
        except Exception as e:
            logger.error(str(e))
            return resp(data={'code': 0, 'msg': {'errmsg': '失败'}})
        if apply is None:
            return resp(data={'code': 0, 'msg': {'errmsg': '非法操作'}})
        try:
            apply.is_on = True
            db.session.commit()
        except Exception as e:
            logger.error(str(e))
            return resp(data={'code': 0, 'msg': {'errmsg': '失败'}})
        return resp(data={'code': 1, 'msg': {'errmsg': '成功'}})
    return resp(data={'code': -1, 'msg': {'errmsg': '登录失效'}})


# TODO(duke) to resolve the deadlock of delete
# TODO!!!
# TODO!!!
@app.route(front + 'delApply', methods=['POST'])
def del_apply():
    res = auth_judge(request, 600)
    if res and res != '-1':
        params = request.values if request.values else request.json
        if params is None or 'task' not in params:
            return resp(data={'code': 0, 'msg': {'errmsg': '缺少参数'}})
        try:
            apply = Apply.query.filter_by(task=params['task'], apply_user=res).first()
        except Exception as e:
            logger.error(str(e))
            return resp(data={'code': 0, 'msg': {'errmsg': '取消失败'}})
        if apply is None:
            return resp(data={'code': 0, 'msg': {'errmsg': '无效请求'}})
        try:
            db.session.delete(apply)
            db.session.commit()
        except Exception as e:
            logger.error(str(e))
            return resp(data={'code': 0, 'msg': {'errmsg': '取消失败'}})
        return resp(data={'code': 1, 'msg': {'errmsg': '成功'}})
    return resp(data={'code': -1, 'msg': {'errmsg': '登录失效'}})


@app.route(front + 'rate', methods=['POST'])
def rate():
    res = auth_judge(request, 600)
    if res and res != '-1':
        params = request.values if request.values else request.json
        if 'task' not in params or 'rate' not in params:
            return resp(data={'code': 0, 'msg': {'errmsg': '缺少参数'}})
        try:
            apply_task = ApplyTask.query.filter_by(task_id=params['task']).first()
        except Exception as e:
            logger.error(str(e))
            return resp(data={'code': 0, 'msg': {'errmsg': '评价失败'}})
        if apply_task is None:
            return resp(data={'code': 0, 'msg': {'errmsg': '无法评价'}})
        if str(apply_task.initiator) != res:
            return resp(data={'code': 0, 'msg': {'errmsg': '无权访问'}})
        if apply_task.rate is not None and apply_task.rate != -1:
            return resp(data={'code': 0, 'msg': {'errmsg': '已经评价过了'}})
        try:
            apply = Apply.query.filter_by(task=params['task'], is_on=True).first()
        except Exception as e:
            logger.error(str(e))
            return resp(data={'code': 0, 'msg': {'errmsg': '评价失败'}})
        if apply is None:
            return resp(data={'code': 0, 'msg': {'errmsg': '无法评价'}})
        try:
            apply.rate = float(params['rate'])
            db.session.commit()
        except Exception as e:
            logger.error(str(e))
            return resp(data={'code': 0, 'msg': {'errmsg': '评价失败'}})
        return resp(data={'code': 1, 'msg': {'errmsg': '评价成功'}})
    return resp(data={'code': -1, 'msg': {'errmsg': '登录失效'}})


if __name__ == '__main__':
    app.run(port=5000, debug=True, host='0.0.0.0')
