from flask import Flask, render_template, request, jsonify, session
from openai import OpenAI
from flask_cors import CORS
import random, string, threading, json, time

app = Flask(__name__)
CORS(app)
app.secret_key = 'haiguitang-secret-key'  # 用于session

# 内存房间存储
rooms = {}
rooms_lock = threading.Lock()

def gen_code(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/create_room', methods=['POST'])
def create_room():
    data = request.json
    nickname = data.get('nickname')
    base_url = data.get('base_url')
    api_key = data.get('api_key')
    model = data.get('model')
    if not (nickname and base_url and api_key and model):
        return jsonify({'error': '参数不完整'}), 400
    code = gen_code()
    with rooms_lock:
        while code in rooms:
            code = gen_code()
        rooms[code] = {
            'owner': nickname,
            'base_url': base_url,
            'api_key': api_key,
            'model': model,
            'messages': [],
            'members': {nickname: {'nickname': nickname}}
        }
    session['nickname'] = nickname
    session['room_code'] = code
    return jsonify({'code': code})

@app.route('/api/join_room', methods=['POST'])
def join_room():
    data = request.json
    nickname = data.get('nickname')
    code = data.get('code')
    if not (nickname and code):
        return jsonify({'error': '参数不完整'}), 400
    with rooms_lock:
        room = rooms.get(code)
        if not room:
            return jsonify({'error': '房间不存在'}), 404
        if nickname in room['members']:
            return jsonify({'error': '昵称已存在'}), 400
        room['members'][nickname] = {'nickname': nickname}
        # 新增：加入在线用户
        if 'online_users' not in room:
            room['online_users'] = {}
        room['online_users'][nickname] = time.time()
        # 新增：初始化无AI群聊消息
        if 'chat_messages' not in room:
            room['chat_messages'] = []
    session['nickname'] = nickname
    session['room_code'] = code
    return jsonify({'success': True, 'room': {'owner': room['owner'], 'model': room['model']}})

@app.route('/api/heartbeat', methods=['POST'])
def heartbeat():
    data = request.json
    code = data.get('code')
    nickname = data.get('nickname')
    if not (code and nickname):
        return jsonify({'error': '参数不完整'}), 400
    with rooms_lock:
        room = rooms.get(code)
        if not room or nickname not in room['members']:
            return jsonify({'error': '房间或用户不存在'}), 404
        if 'online_users' not in room:
            room['online_users'] = {}
        room['online_users'][nickname] = time.time()
    return jsonify({'success': True})

@app.route('/api/get_online_users', methods=['POST'])
def get_online_users():
    data = request.json
    code = data.get('code')
    if not code:
        return jsonify({'error': '参数不完整'}), 400
    now = time.time()
    with rooms_lock:
        room = rooms.get(code)
        if not room or 'online_users' not in room:
            return jsonify({'users': []})
        # 1分钟无心跳视为下线
        users = [u for u, t in room['online_users'].items() if now - t < 60]
    return jsonify({'users': users})

@app.route('/api/send_chat_message', methods=['POST'])
def send_chat_message():
    data = request.json
    code = data.get('code')
    nickname = data.get('nickname')
    content = data.get('content')
    if not (code and nickname and content):
        return jsonify({'error': '参数不完整'}), 400
    with rooms_lock:
        room = rooms.get(code)
        if not room or nickname not in room['members']:
            return jsonify({'error': '房间或用户不存在'}), 404
        if 'chat_messages' not in room:
            room['chat_messages'] = []
        room['chat_messages'].append({'nickname': nickname, 'content': content, 'time': int(time.time())})
        # 只保留最新100条
        if len(room['chat_messages']) > 100:
            room['chat_messages'] = room['chat_messages'][-100:]
    return jsonify({'success': True})

@app.route('/api/get_chat_messages', methods=['POST'])
def get_chat_messages():
    data = request.json
    code = data.get('code')
    if not code:
        return jsonify({'error': '参数不完整'}), 400
    with rooms_lock:
        room = rooms.get(code)
        if not room or 'chat_messages' not in room:
            return jsonify({'messages': []})
        return jsonify({'messages': room['chat_messages']})

@app.route('/api/send_message', methods=['POST'])
def send_message():
    data = request.json
    code = data.get('code')
    nickname = data.get('nickname')
    content = data.get('content')
    if not (code and nickname and content):
        return jsonify({'error': '参数不完整'}), 400
    with rooms_lock:
        room = rooms.get(code)
        if not room:
            return jsonify({'error': '房间不存在'}), 404
        if nickname not in room['members']:
            return jsonify({'error': '未加入房间'}), 403
        room['messages'].append({'role': 'user', 'content': content, 'nickname': nickname})
        # 题目预设
        preset = ''
        if 'stories' in room and room.get('current_story') is not None:
            story = room['stories'][room['current_story']]
            additional = story.get('additional', '')
            victory_condition = story.get('victory_condition', '')
            preset = f"你现在是海龟汤推理游戏的主持人。当前题目如下：\n\n汤面：{story.get('surface', '')}\n\n游戏规则：出题者先给出不完整的'汤面'（题目），让猜题者提出各种可能性的问题，而出题者只能回答'是'、'不是'或'不重要'。猜题者在有限的线索中推理出事件的始末，拼出故事的全貌，凑出一个'汤底'（答案）。你只需根据规则回答问题，不要直接给出答案。同时会给出胜利条件，由你来决定是否过关。\n\n补充说明（仅供AI参考）：{additional}\n\n胜利条件：{victory_condition}"
        else:
            preset = "当前房间还没有上传题目，请房主上传海龟汤题目（json文件）。"
        messages = [
            {'role': 'system', 'content': preset}
        ]
        for msg in room['messages']:
            if msg['role'] == 'user':
                messages.append({'role': 'user', 'content': f"{msg['nickname']}: {msg['content']}"})
            elif msg['role'] == 'assistant':
                messages.append({'role': 'assistant', 'content': msg['content']})
        try:
            client = OpenAI(base_url=room['base_url'], api_key=room['api_key'])
            completion = client.chat.completions.create(
                model=room['model'],
                messages=messages
            )
            reply = completion.choices[0].message.content
            room['messages'].append({'role': 'assistant', 'content': reply, 'nickname': 'AI'})
            return jsonify({'reply': reply})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

@app.route('/api/get_messages', methods=['POST'])
def get_messages():
    data = request.json
    code = data.get('code')
    if not code:
        return jsonify({'error': '参数不完整'}), 400
    with rooms_lock:
        room = rooms.get(code)
        if not room:
            return jsonify({'error': '房间不存在'}), 404
        return jsonify({'messages': room['messages']})

@app.route('/api/delete_room', methods=['POST'])
def delete_room():
    data = request.json
    code = data.get('code')
    nickname = data.get('nickname')
    if not (code and nickname):
        return jsonify({'error': '参数不完整'}), 400
    with rooms_lock:
        room = rooms.get(code)
        if not room:
            return jsonify({'error': '房间不存在'}), 404
        if room['owner'] != nickname:
            return jsonify({'error': '只有房主可以删除房间'}), 403
        del rooms[code]
    return jsonify({'success': True})

# 保留单人对话接口
@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    base_url = data.get('base_url')
    api_key = data.get('api_key')
    model = data.get('model')
    messages = data.get('messages')
    if not (base_url and api_key and model and messages):
        return jsonify({'error': '参数不完整'}), 400
    try:
        client = OpenAI(base_url=base_url, api_key=api_key)
        completion = client.chat.completions.create(
            model=model,
            messages=messages
        )
        reply = completion.choices[0].message.content
        return jsonify({'reply': reply})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/upload_story', methods=['POST'])
def upload_story():
    code = request.form.get('code')
    nickname = request.form.get('nickname')
    if not (code and nickname):
        return jsonify({'error': '参数不完整'}), 400
    with rooms_lock:
        room = rooms.get(code)
        if not room:
            return jsonify({'error': '房间不存在'}), 404
        if room['owner'] != nickname:
            return jsonify({'error': '只有房主可以上传题目'}), 403
        if 'stories' not in room:
            room['stories'] = []
        files = request.files.getlist('file')
        for file in files:
            try:
                story = json.load(file)
                if isinstance(story, list):
                    room['stories'].extend(story)
                else:
                    room['stories'].append(story)
            except Exception as e:
                return jsonify({'error': f'文件解析失败: {str(e)}'}), 400
        # 默认切换到最新上传的题目
        room['current_story'] = len(room['stories']) - 1 if room['stories'] else None
        # 初始化揭晓标志
        if room['current_story'] is not None:
            room['reveal_answer_flag'] = False
    return jsonify({'success': True, 'count': len(room['stories'])})

@app.route('/api/set_story', methods=['POST'])
def set_story():
    data = request.json
    code = data.get('code')
    nickname = data.get('nickname')
    idx = data.get('index')
    if not (code and nickname and isinstance(idx, int)):
        return jsonify({'error': '参数不完整'}), 400
    with rooms_lock:
        room = rooms.get(code)
        if not room:
            return jsonify({'error': '房间不存在'}), 404
        if room['owner'] != nickname:
            return jsonify({'error': '只有房主可以切换题目'}), 403
        if 'stories' not in room or not room['stories']:
            return jsonify({'error': '题库为空'}), 400
        if not (0 <= idx < len(room['stories'])):
            return jsonify({'error': '题目索引超出范围'}), 400
        room['current_story'] = idx
        # 插入系统消息
        room['messages'].append({'role': 'system', 'content': '房主已切换其他题目', 'nickname': '系统'})
        # 初始化揭晓标志
        room['reveal_answer_flag'] = False
    return jsonify({'success': True})

@app.route('/api/get_current_story', methods=['POST'])
def get_current_story():
    data = request.json
    code = data.get('code')
    if not code:
        return jsonify({'error': '参数不完整'}), 400
    with rooms_lock:
        room = rooms.get(code)
        if not room or 'stories' not in room or room.get('current_story') is None:
            return jsonify({'error': '暂无题目'}), 404
        story = room['stories'][room['current_story']]
        victory_condition = story.get('victory_condition', '')
        answer = story.get('answer', '') if room.get('reveal_answer_flag') else ''
        return jsonify({
            'surface': story.get('surface', ''),
            'victory_condition': victory_condition,
            'answer': answer
        })

@app.route('/api/reveal_answer', methods=['POST'])
def reveal_answer():
    data = request.json
    code = data.get('code')
    nickname = data.get('nickname')
    if not (code and nickname):
        return jsonify({'error': '参数不完整'}), 400
    with rooms_lock:
        room = rooms.get(code)
        if not room:
            return jsonify({'error': '房间不存在'}), 404
        if room['owner'] != nickname:
            return jsonify({'error': '只有房主可以揭晓答案'}), 403
        room['reveal_answer_flag'] = True
        # 插入系统消息
        story = room['stories'][room['current_story']]
        room['messages'].append({'role': 'system', 'content': f"房主已揭晓答案：{story.get('answer', '')}", 'nickname': '系统'})
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 