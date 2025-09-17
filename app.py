from flask import Flask, request, jsonify, render_template_string
from openai import OpenAI
from flask_cors import CORS
import json, uuid, time, os
from concurrent.futures import ThreadPoolExecutor
import datetime

app = Flask(__name__)
CORS(app)
app.secret_key = 'chemical-turtle-soup-secret-key'

# 加载配置
with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# AI配置
AI_BASE_URL = config.get('ai_settings', {}).get('base_url', 'http://api.0ha.top/v1')
AI_API_KEY = config.get('ai_settings', {}).get('api_key', '')
AI_MODEL = config.get('ai_settings', {}).get('model', 'gpt-4o-mini')

# 游戏配置
SESSION_TIMEOUT = config.get('game_settings', {}).get('session_timeout', 3600)
MAX_HINTS = config.get('game_settings', {}).get('max_hints', 3)

# 线程池
ai_executor = ThreadPoolExecutor(max_workers=4)

# 内存数据存储
active_sessions = {}
chemistry_problems = []
categories = {}

# 加载化学题库
def load_chemistry_problems():
    global chemistry_problems, categories
    try:
        with open('data/chemistry_problems.json', 'r', encoding='utf-8') as f:
            chemistry_problems = json.load(f)
        with open('data/categories.json', 'r', encoding='utf-8') as f:
            categories = json.load(f)
        print(f"已加载 {len(chemistry_problems)} 个化学题目")
    except FileNotFoundError:
        print("警告: 化学题库文件不存在，将使用内置题库")
        load_builtin_problems()

# 内置化学题库
def load_builtin_problems():
    global chemistry_problems, categories
    chemistry_problems = [
        {
            "id": "chem_001",
            "title": "蓝瓶子实验",
            "surface": "一位学生将两种无色溶液混合，溶液突然变成了鲜艳的蓝色，但几分钟后又变回无色。这是为什么？",
            "answer": "这是经典的蓝瓶子实验。学生混合的是含有亚甲基蓝指示剂的碱性葡萄糖溶液和空气（氧气）。葡萄糖作为还原剂使亚甲基蓝褪色为无色，振荡时氧气氧化亚甲基蓝又变回蓝色。这是一个氧化还原反应的可逆过程。",
            "victory_condition": "玩家需要识别出这是亚甲基蓝的氧化还原反应，理解葡萄糖的还原作用和氧气的氧化作用，以及颜色的可逆变化原理。",
            "hints": [
                "提示1：这涉及到氧化还原反应",
                "提示2：亚甲基蓝是一种常用的氧化还原指示剂",
                "提示3：葡萄糖在这个反应中充当还原剂",
                "提示4：振荡过程中氧气参与反应"
            ],
            "difficulty": 2,
            "category": "氧化还原反应",
            "subcategory": "指示剂反应",
            "keywords": ["亚甲基蓝", "氧化还原", "葡萄糖", "氧气", "指示剂"],
            "related_concepts": ["氧化还原反应", "化学指示剂", "反应动力学"],
            "time_limit": 600,
            "success_rate": 0.75,
            "play_count": 100
        },
        {
            "id": "chem_002",
            "title": "神秘的银镜",
            "surface": "一位化学家在试管中加入一种无色溶液，然后加入另一种液体，轻轻摇晃后，试管内壁竟然出现了一层明亮的银镜。这是怎么回事？",
            "answer": "这是银镜反应。化学家在硝酸银溶液中加入了氨水形成银氨络离子，然后加入葡萄糖或甲醛等还原剂。还原剂将银离子还原为单质银，沉积在试管内壁形成银镜。这是一个典型的氧化还原反应，用于检测醛基的存在。",
            "victory_condition": "玩家需要识别出银镜反应，理解银氨络离子的形成以及还原剂将银离子还原为银单质的过程。",
            "hints": [
                "提示1：这是一种用于检测醛基的经典反应",
                "提示2：反应涉及到银离子的还原",
                "提示3：需要先形成银氨络离子",
                "提示4：葡萄糖或甲醛可以作为还原剂"
            ],
            "difficulty": 3,
            "category": "氧化还原反应",
            "subcategory": "银镜反应",
            "keywords": ["银镜反应", "银离子", "还原剂", "醛基", "银氨络离子"],
            "related_concepts": ["氧化还原反应", "定性分析", "有机化学检测"],
            "time_limit": 480,
            "success_rate": 0.65,
            "play_count": 85
        },
        {
            "id": "chem_003",
            "title": "变色魔术师",
            "surface": "实验桌上放着三瓶无色溶液：A、B、C。学生将A倒入B中，溶液变为红色；再将混合液倒入C中，红色立即消失，变为无色。这三种溶液分别是什么？",
            "answer": "这是酸碱指示剂反应。A是酚酞溶液（无色），B是氢氧化钠溶液（碱性），C是盐酸溶液（酸性）。酚酞在碱性环境中变为红色，在酸性环境中无色。当酚酞遇到氢氧化钠时显红色，再加入盐酸中和碱性后，酚酞恢复无色。",
            "victory_condition": "玩家需要识别出酚酞作为酸碱指示剂的性质，以及碱性环境下显红色、酸性环境下无色的特性。",
            "hints": [
                "提示1：这涉及到酸碱指示剂的性质",
                "提示2：酚酞是一种常用的酸碱指示剂",
                "提示3：需要考虑溶液的酸碱性变化",
                "提示4：A应该是指示剂，B是碱性溶液，C是酸性溶液"
            ],
            "difficulty": 2,
            "category": "酸碱反应",
            "subcategory": "指示剂变色",
            "keywords": ["酚酞", "酸碱指示剂", "氢氧化钠", "盐酸", "酸碱性"],
            "related_concepts": ["酸碱反应", "指示剂", "pH值", "中和反应"],
            "time_limit": 420,
            "success_rate": 0.80,
            "play_count": 120
        }
    ]
    
    categories = {
        "氧化还原反应": {
            "id": "redox",
            "description": "涉及电子转移的化学反应",
            "subcategories": {
                "指示剂反应": ["chem_001"],
                "银镜反应": ["chem_002"]
            }
        },
        "酸碱反应": {
            "id": "acid_base",
            "description": "酸碱中和及相关反应",
            "subcategories": {
                "指示剂变色": ["chem_003"]
            }
        }
    }

# 清理过期会话
def cleanup_expired_sessions():
    current_time = time.time()
    expired_sessions = [
        session_id for session_id, session in active_sessions.items()
        if current_time - session.get('start_time', 0) > SESSION_TIMEOUT
    ]
    for session_id in expired_sessions:
        del active_sessions[session_id]
    if expired_sessions:
        print(f"清理了 {len(expired_sessions)} 个过期会话")

# AI提示词管理
class ChemistryPromptManager:
    @staticmethod
    def build_system_prompt(problem_data, hints_used=0):
        chemical_context = {
            "氧化还原反应": "氧化还原反应是涉及电子转移的化学反应，特征是元素氧化态的变化。常见的氧化剂包括氧气、高锰酸钾等，还原剂包括金属、氢气、葡萄糖等。",
            "酸碱反应": "酸碱反应涉及质子(H+)的转移，酸提供质子，碱接受质子。常用指示剂包括酚酞、甲基橙等，在不同pH环境下显示不同颜色。"
        }
        
        prompt = f"""你是化学海龟汤游戏的主持人。当前题目：

【题目】{problem_data['surface']}
【分类】{problem_data['category']}
【难度】{problem_data['difficulty']}/5

【化学背景】{chemical_context.get(problem_data['category'], '')}

游戏规则：
1. 你只能回答"是"、"不是"或"不重要"
2. 当玩家以"开始故事还原："开头时，你只能回复以下三种之一：故事还原错误、故事还原正确、故事还原大致正确
3. 当玩家回复"整理线索"时，你需要整理之前所有AI回答中有用的线索和不重要的线索
4. 绝对不能直接给出答案，只能通过是/否回答引导玩家思考

请严格按照规则回答问题。"""
        
        return prompt

# ==================== API接口 ====================

@app.route('/api/game/start', methods=['POST'])
def start_game():
    """开始新的化学海龟汤游戏"""
    try:
        data = request.get_json() or {}
        category = data.get('category')
        difficulty = data.get('difficulty')
        problem_id = data.get('problem_id')
        
        # 选择题目
        problem = None
        if problem_id:
            problem = next((p for p in chemistry_problems if p['id'] == problem_id), None)
        else:
            # 根据条件筛选题目
            candidates = chemistry_problems
            if category:
                candidates = [p for p in candidates if p['category'] == category]
            if difficulty:
                candidates = [p for p in candidates if p['difficulty'] == difficulty]
            
            if candidates:
                problem = candidates[0]  # 简化处理，取第一个符合的题目
            else:
                problem = chemistry_problems[0]  # 默认第一个题目
        
        if not problem:
            return jsonify({'error': '未找到合适的题目'}), 404
        
        # 创建会话
        session_id = str(uuid.uuid4())
        active_sessions[session_id] = {
            'session_id': session_id,
            'current_problem': problem['id'],
            'problem_data': problem,
            'conversation_history': [
                {
                    'role': 'system',
                    'content': '欢迎来到化学海龟汤游戏！你可以通过提问是/否问题来推理出化学现象背后的原理。',
                    'timestamp': datetime.datetime.now().isoformat()
                }
            ],
            'hints_used': 0,
            'start_time': time.time(),
            'status': 'playing',
            'attempts': 0,
            'questions_asked': 0
        }
        
        return jsonify({
            'session_id': session_id,
            'problem': {
                'id': problem['id'],
                'title': problem['title'],
                'surface': problem['surface'],
                'category': problem['category'],
                'difficulty': problem['difficulty'],
                'hints_available': len(problem.get('hints', []))
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/game/ask', methods=['POST'])
def ask_question():
    """用户向AI提问"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        question = data.get('question', '').strip()
        
        if not session_id or not question:
            return jsonify({'error': '参数不完整'}), 400
        
        session = active_sessions.get(session_id)
        if not session:
            return jsonify({'error': '会话不存在或已过期'}), 404
        
        # 添加用户问题到对话历史
        user_message = {
            'role': 'user',
            'content': question,
            'timestamp': datetime.datetime.now().isoformat()
        }
        session['conversation_history'].append(user_message)
        session['questions_asked'] += 1
        
        # 构建AI请求
        problem_data = session['problem_data']
        system_prompt = ChemistryPromptManager.build_system_prompt(problem_data, session['hints_used'])
        
        messages = [{'role': 'system', 'content': system_prompt}]
        for msg in session['conversation_history']:
            if msg['role'] == 'user':
                messages.append({'role': 'user', 'content': msg['content']})
            elif msg['role'] == 'assistant':
                messages.append({'role': 'assistant', 'content': msg['content']})
        
        # 异步调用AI
        def get_ai_response():
            try:
                client = OpenAI(base_url=AI_BASE_URL, api_key=AI_API_KEY)
                completion = client.chat.completions.create(
                    model=AI_MODEL,
                    messages=messages
                )
                return completion.choices[0].message.content
            except Exception as e:
                return f"[AI错误] {str(e)}"
        
        future = ai_executor.submit(get_ai_response)
        ai_response = future.result(timeout=30)
        
        # 添加AI回复到对话历史
        ai_message = {
            'role': 'assistant',
            'content': ai_response,
            'timestamp': datetime.datetime.now().isoformat()
        }
        session['conversation_history'].append(ai_message)
        
        # 检查是否还原成功
        if ai_response in ['故事还原正确', '故事还原大致正确']:
            session['status'] = 'completed'
            session['attempts'] += 1
        
        return jsonify({
            'response': ai_response,
            'message_id': str(uuid.uuid4()),
            'status': session['status'],
            'questions_asked': session['questions_asked']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/game/hint', methods=['POST'])
def get_hint():
    """获取提示"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        
        if not session_id:
            return jsonify({'error': '参数不完整'}), 400
        
        session = active_sessions.get(session_id)
        if not session:
            return jsonify({'error': '会话不存在或已过期'}), 404
        
        problem = session['problem_data']
        hints = problem.get('hints', [])
        
        if session['hints_used'] >= len(hints):
            return jsonify({'error': '没有更多提示了'}), 400
        
        if session['hints_used'] >= MAX_HINTS:
            return jsonify({'error': '已达到最大提示次数'}), 400
        
        hint_text = hints[session['hints_used']]
        session['hints_used'] += 1
        
        return jsonify({
            'hint': hint_text,
            'hints_remaining': len(hints) - session['hints_used'],
            'hints_used': session['hints_used']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/game/status', methods=['GET'])
def get_game_status():
    """获取游戏状态"""
    try:
        session_id = request.args.get('session_id')
        if not session_id:
            return jsonify({'error': '参数不完整'}), 400
        
        session = active_sessions.get(session_id)
        if not session:
            return jsonify({'error': '会话不存在或已过期'}), 404
        
        return jsonify({
            'status': session['status'],
            'questions_asked': session['questions_asked'],
            'hints_used': session['hints_used'],
            'time_elapsed': int(time.time() - session['start_time'])
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/categories', methods=['GET'])
def get_categories():
    """获取化学题目分类"""
    try:
        return jsonify({'categories': categories})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/problems', methods=['GET'])
def get_problems():
    """获取题目列表"""
    try:
        category = request.args.get('category')
        difficulty = request.args.get('difficulty', type=int)
        
        problems = chemistry_problems
        if category:
            problems = [p for p in problems if p['category'] == category]
        if difficulty:
            problems = [p for p in problems if p['difficulty'] == difficulty]
        
        # 简化题目列表，只返回基本信息
        problem_list = []
        for p in problems:
            problem_list.append({
                'id': p['id'],
                'title': p['title'],
                'category': p['category'],
                'difficulty': p['difficulty'],
                'keywords': p.get('keywords', [])
            })
        
        return jsonify({
            'problems': problem_list,
            'total': len(problem_list)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/problems/random', methods=['GET'])
def get_random_problem():
    """随机获取题目"""
    try:
        category = request.args.get('category')
        difficulty = request.args.get('difficulty', type=int)
        
        candidates = chemistry_problems
        if category:
            candidates = [p for p in candidates if p['category'] == category]
        if difficulty:
            candidates = [p for p in candidates if p['difficulty'] == difficulty]
        
        if candidates:
            import random
            problem = random.choice(candidates)
            return jsonify({'problem': problem})
        else:
            return jsonify({'error': '未找到符合条件的题目'}), 404
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({'status': 'ok', 'active_sessions': len(active_sessions)})

@app.route('/test')
def api_test_page():
    """API测试页面"""
    return render_template_string('''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>化学海龟汤 API 测试</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .header p {
            font-size: 1.1em;
            opacity: 0.9;
        }
        
        .main-content {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            padding: 30px;
        }
        
        .left-panel, .right-panel {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }
        
        .card {
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
            border: 1px solid #e2e8f0;
        }
        
        .card h2 {
            color: #2d3748;
            margin-bottom: 15px;
            font-size: 1.4em;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .card h2::before {
            content: '';
            width: 4px;
            height: 24px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 2px;
        }
        
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            font-size: 1em;
            cursor: pointer;
            transition: all 0.3s ease;
            font-weight: 600;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        
        .btn:disabled {
            background: #cbd5e0;
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
        }
        
        .btn-secondary {
            background: #48bb78;
        }
        
        .btn-danger {
            background: #f56565;
        }
        
        .input-group {
            margin-bottom: 15px;
        }
        
        .input-group label {
            display: block;
            margin-bottom: 5px;
            color: #4a5568;
            font-weight: 600;
        }
        
        .input-group input, .input-group select, .input-group textarea {
            width: 100%;
            padding: 10px 15px;
            border: 2px solid #e2e8f0;
            border-radius: 8px;
            font-size: 1em;
            transition: border-color 0.3s ease;
        }
        
        .input-group input:focus, .input-group select:focus, .input-group textarea:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .input-group textarea {
            resize: vertical;
            min-height: 100px;
        }
        
        .status-box {
            background: #f7fafc;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 15px;
        }
        
        .status-item {
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
        }
        
        .status-item:last-child {
            margin-bottom: 0;
        }
        
        .status-label {
            color: #718096;
        }
        
        .status-value {
            font-weight: 600;
            color: #2d3748;
        }
        
        .problem-display {
            background: #edf2f7;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 15px;
            border-left: 4px solid #667eea;
        }
        
        .problem-title {
            font-size: 1.2em;
            font-weight: 600;
            color: #2d3748;
            margin-bottom: 10px;
        }
        
        .problem-content {
            color: #4a5568;
            line-height: 1.6;
        }
        
        .chat-history {
            max-height: 400px;
            overflow-y: auto;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 15px;
            background: #f7fafc;
        }
        
        .chat-message {
            margin-bottom: 15px;
            padding: 10px 15px;
            border-radius: 8px;
        }
        
        .chat-message.user {
            background: #667eea;
            color: white;
            margin-left: 20px;
        }
        
        .chat-message.ai {
            background: #e2e8f0;
            color: #2d3748;
            margin-right: 20px;
        }
        
        .chat-message.system {
            background: #fbd38d;
            color: #744210;
            text-align: center;
            font-style: italic;
        }
        
        .chat-message .role {
            font-size: 0.8em;
            opacity: 0.8;
            margin-bottom: 5px;
        }
        
        .api-log {
            max-height: 300px;
            overflow-y: auto;
            background: #1a202c;
            color: #e2e8f0;
            border-radius: 8px;
            padding: 15px;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 0.9em;
        }
        
        .api-log-item {
            margin-bottom: 10px;
            padding-bottom: 10px;
            border-bottom: 1px solid #2d3748;
        }
        
        .api-log-item:last-child {
            border-bottom: none;
        }
        
        .api-log-request {
            color: #68d391;
        }
        
        .api-log-response {
            color: #63b3ed;
        }
        
        .api-log-error {
            color: #fc8181;
        }
        
        .hint-box {
            background: #fef5e7;
            border: 1px solid #f6ad55;
            border-radius: 8px;
            padding: 15px;
            margin-top: 10px;
        }
        
        .controls {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        
        .success {
            color: #48bb78;
            font-weight: 600;
        }
        
        .error {
            color: #f56565;
            font-weight: 600;
        }
        
        @media (max-width: 768px) {
            .main-content {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧪 化学海龟汤 API 测试</h1>
            <p>单机版化学海龟汤游戏服务器接口测试工具</p>
        </div>
        
        <div class="main-content">
            <div class="left-panel">
                <!-- 游戏控制 -->
                <div class="card">
                    <h2>🎮 游戏控制</h2>
                    <div class="input-group">
                        <label>选择分类（可选）</label>
                        <select id="categorySelect">
                            <option value="">随机分类</option>
                            <option value="氧化还原反应">氧化还原反应</option>
                            <option value="酸碱反应">酸碱反应</option>
                        </select>
                    </div>
                    <div class="input-group">
                        <label>选择难度（可选）</label>
                        <select id="difficultySelect">
                            <option value="">随机难度</option>
                            <option value="1">初级 (1)</option>
                            <option value="2">中级 (2)</option>
                            <option value="3">高级 (3)</option>
                        </select>
                    </div>
                    <div class="controls">
                        <button class="btn" onclick="startGame()">开始新游戏</button>
                        <button class="btn btn-secondary" onclick="getGameStatus()">刷新状态</button>
                        <button class="btn btn-danger" onclick="clearSession()">清除会话</button>
                    </div>
                </div>
                
                <!-- 游戏状态 -->
                <div class="card">
                    <h2>📊 游戏状态</h2>
                    <div class="status-box">
                        <div class="status-item">
                            <span class="status-label">会话ID:</span>
                            <span class="status-value" id="sessionId">-</span>
                        </div>
                        <div class="status-item">
                            <span class="status-label">游戏状态:</span>
                            <span class="status-value" id="gameStatus">未开始</span>
                        </div>
                        <div class="status-item">
                            <span class="status-label">问题数量:</span>
                            <span class="status-value" id="questionCount">0</span>
                        </div>
                        <div class="status-item">
                            <span class="status-label">已用提示:</span>
                            <span class="status-value" id="hintsUsed">0</span>
                        </div>
                        <div class="status-item">
                            <span class="status-label">游戏时间:</span>
                            <span class="status-value" id="gameTime">0秒</span>
                        </div>
                    </div>
                </div>
                
                <!-- 当前题目 -->
                <div class="card" id="problemCard" style="display: none;">
                    <h2>📝 当前题目</h2>
                    <div class="problem-display">
                        <div class="problem-title" id="problemTitle">-</div>
                        <div class="problem-content" id="problemContent">-</div>
                        <div style="margin-top: 10px; font-size: 0.9em; color: #718096;">
                            分类: <span id="problemCategory">-</span> | 
                            难度: <span id="problemDifficulty">-</span> |
                            可用提示: <span id="hintsAvailable">-</span>
                        </div>
                    </div>
                    <button class="btn btn-secondary" onclick="getHint()">获取提示 💡</button>
                </div>
            </div>
            
            <div class="right-panel">
                <!-- AI对话 -->
                <div class="card">
                    <h2>💬 AI对话</h2>
                    <div class="chat-history" id="chatHistory">
                        <div class="chat-message system">
                            <div class="role">系统</div>
                            <div>点击"开始新游戏"开始你的化学海龟汤之旅！</div>
                        </div>
                    </div>
                    <div style="margin-top: 15px;">
                        <div class="input-group">
                            <textarea id="questionInput" placeholder="输入你的问题（只能回答是/否/不重要）..." disabled></textarea>
                        </div>
                        <button class="btn" onclick="askQuestion()" id="askButton" disabled>发送问题</button>
                    </div>
                </div>
                
                <!-- 提示历史 -->
                <div class="card" id="hintCard" style="display: none;">
                    <h2>💡 提示历史</h2>
                    <div id="hintHistory"></div>
                </div>
                
                <!-- API日志 -->
                <div class="card">
                    <h2>📋 API日志</h2>
                    <button class="btn btn-secondary" onclick="clearLog()" style="margin-bottom: 10px;">清空日志</button>
                    <div class="api-log" id="apiLog"></div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        let currentSessionId = null;
        let gameStartTime = null;
        let gameTimer = null;
        
        // 从localStorage恢复会话
        window.onload = function() {
            const savedSessionId = localStorage.getItem('testSessionId');
            if (savedSessionId) {
                currentSessionId = savedSessionId;
                document.getElementById('sessionId').textContent = savedSessionId;
                getGameStatus();
            }
        };
        
        // 开始新游戏
        async function startGame() {
            const category = document.getElementById('categorySelect').value;
            const difficulty = document.getElementById('difficultySelect').value;
            
            const requestBody = {};
            if (category) requestBody.category = category;
            if (difficulty) requestBody.difficulty = parseInt(difficulty);
            
            try {
                const response = await fetch('/api/game/start', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(requestBody)
                });
                
                const data = await response.json();
                logAPI('POST /api/game/start', requestBody, data);
                
                if (data.session_id) {
                    currentSessionId = data.session_id;
                    localStorage.setItem('testSessionId', currentSessionId);
                    gameStartTime = Date.now();
                    
                    // 更新UI
                    document.getElementById('sessionId').textContent = currentSessionId;
                    document.getElementById('gameStatus').textContent = '进行中';
                    document.getElementById('questionCount').textContent = '0';
                    document.getElementById('hintsUsed').textContent = '0';
                    
                    // 显示题目
                    document.getElementById('problemCard').style.display = 'block';
                    document.getElementById('problemTitle').textContent = data.problem.title;
                    document.getElementById('problemContent').textContent = data.problem.surface;
                    document.getElementById('problemCategory').textContent = data.problem.category;
                    document.getElementById('problemDifficulty').textContent = data.problem.difficulty;
                    document.getElementById('hintsAvailable').textContent = data.problem.hints_available;
                    
                    // 启用输入
                    document.getElementById('questionInput').disabled = false;
                    document.getElementById('askButton').disabled = false;
                    
                    // 清空聊天记录
                    document.getElementById('chatHistory').innerHTML = `
                        <div class="chat-message system">
                            <div class="role">系统</div>
                            <div>欢迎来到化学海龟汤游戏！你可以通过提问是/否问题来推理出化学现象背后的原理。</div>
                        </div>
                    `;
                    
                    // 启动计时器
                    startGameTimer();
                    
                    // 清空提示历史
                    document.getElementById('hintHistory').innerHTML = '';
                    document.getElementById('hintCard').style.display = 'none';
                }
            } catch (error) {
                logAPI('POST /api/game/start', requestBody, {error: error.message}, true);
            }
        }
        
        // 提问
        async function askQuestion() {
            const question = document.getElementById('questionInput').value.trim();
            if (!question || !currentSessionId) return;
            
            try {
                const response = await fetch('/api/game/ask', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        session_id: currentSessionId,
                        question: question
                    })
                });
                
                const data = await response.json();
                logAPI('POST /api/game/ask', {session_id: currentSessionId, question}, data);
                
                if (data.response) {
                    // 添加到聊天记录
                    addChatMessage('user', question);
                    addChatMessage('ai', data.response);
                    
                    // 更新状态
                    document.getElementById('questionCount').textContent = data.questions_asked;
                    document.getElementById('gameStatus').textContent = data.status;
                    
                    // 清空输入框
                    document.getElementById('questionInput').value = '';
                    
                    // 如果游戏结束
                    if (data.status === 'completed') {
                        document.getElementById('questionInput').disabled = true;
                        document.getElementById('askButton').disabled = true;
                        stopGameTimer();
                    }
                }
            } catch (error) {
                logAPI('POST /api/game/ask', {session_id: currentSessionId, question}, {error: error.message}, true);
            }
        }
        
        // 获取提示
        async function getHint() {
            if (!currentSessionId) return;
            
            try {
                const response = await fetch('/api/game/hint', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        session_id: currentSessionId
                    })
                });
                
                const data = await response.json();
                logAPI('POST /api/game/hint', {session_id: currentSessionId}, data);
                
                if (data.hint) {
                    // 添加提示到历史
                    const hintDiv = document.createElement('div');
                    hintDiv.className = 'hint-box';
                    hintDiv.innerHTML = `<strong>提示 ${data.hints_used}:</strong> ${data.hint}`;
                    document.getElementById('hintHistory').appendChild(hintDiv);
                    
                    // 显示提示卡片
                    document.getElementById('hintCard').style.display = 'block';
                    
                    // 更新提示计数
                    document.getElementById('hintsUsed').textContent = data.hints_used;
                }
            } catch (error) {
                logAPI('POST /api/game/hint', {session_id: currentSessionId}, {error: error.message}, true);
            }
        }
        
        // 获取游戏状态
        async function getGameStatus() {
            if (!currentSessionId) return;
            
            try {
                const response = await fetch(`/api/game/status?session_id=${currentSessionId}`);
                const data = await response.json();
                logAPI('GET /api/game/status', {session_id: currentSessionId}, data);
                
                if (data.status) {
                    document.getElementById('gameStatus').textContent = data.status;
                    document.getElementById('questionCount').textContent = data.questions_asked;
                    document.getElementById('hintsUsed').textContent = data.hints_used;
                }
            } catch (error) {
                logAPI('GET /api/game/status', {session_id: currentSessionId}, {error: error.message}, true);
            }
        }
        
        // 清除会话
        function clearSession() {
            currentSessionId = null;
            localStorage.removeItem('testSessionId');
            
            // 重置UI
            document.getElementById('sessionId').textContent = '-';
            document.getElementById('gameStatus').textContent = '未开始';
            document.getElementById('questionCount').textContent = '0';
            document.getElementById('hintsUsed').textContent = '0';
            document.getElementById('gameTime').textContent = '0秒';
            
            // 隐藏题目
            document.getElementById('problemCard').style.display = 'none';
            
            // 禁用输入
            document.getElementById('questionInput').disabled = true;
            document.getElementById('askButton').disabled = true;
            
            // 清空聊天记录
            document.getElementById('chatHistory').innerHTML = `
                <div class="chat-message system">
                    <div class="role">系统</div>
                    <div>会话已清除，点击"开始新游戏"开始你的化学海龟汤之旅！</div>
                </div>
            `;
            
            // 停止计时器
            stopGameTimer();
        }
        
        // 游戏计时器
        function startGameTimer() {
            if (gameTimer) clearInterval(gameTimer);
            
            gameTimer = setInterval(() => {
                if (gameStartTime) {
                    const elapsed = Math.floor((Date.now() - gameStartTime) / 1000);
                    document.getElementById('gameTime').textContent = elapsed + '秒';
                }
            }, 1000);
        }
        
        function stopGameTimer() {
            if (gameTimer) {
                clearInterval(gameTimer);
                gameTimer = null;
            }
        }
        
        // 添加聊天消息
        function addChatMessage(role, content) {
            const chatHistory = document.getElementById('chatHistory');
            const messageDiv = document.createElement('div');
            messageDiv.className = `chat-message ${role}`;
            messageDiv.innerHTML = `
                <div class="role">${role === 'user' ? '玩家' : role === 'ai' ? 'AI' : '系统'}</div>
                <div>${content}</div>
            `;
            chatHistory.appendChild(messageDiv);
            chatHistory.scrollTop = chatHistory.scrollHeight;
        }
        
        // API日志
        function logAPI(request, data, response, isError = false) {
            const log = document.getElementById('apiLog');
            const time = new Date().toLocaleTimeString();
            
            const logItem = document.createElement('div');
            logItem.className = 'api-log-item';
            
            const requestStr = JSON.stringify(data, null, 2);
            const responseStr = JSON.stringify(response, null, 2);
            
            logItem.innerHTML = `
                <div>[${time}] ${request}</div>
                <div class="api-log-request">Request: ${requestStr}</div>
                <div class="${isError ? 'api-log-error' : 'api-log-response'}">Response: ${responseStr}</div>
            `;
            
            log.appendChild(logItem);
            log.scrollTop = log.scrollHeight;
        }
        
        function clearLog() {
            document.getElementById('apiLog').innerHTML = '';
        }
        
        // Enter键发送消息
        document.getElementById('questionInput').addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                askQuestion();
            }
        });
    </script>
</body>
</html>
    ''')

# ==================== 初始化 ====================

if __name__ == '__main__':
    # 创建数据目录
    os.makedirs('data', exist_ok=True)
    
    # 加载题库
    load_chemistry_problems()
    
    # 启动清理线程
    def cleanup_task():
        while True:
            time.sleep(600)  # 每10分钟清理一次
            cleanup_expired_sessions()
    
    import threading
    threading.Thread(target=cleanup_task, daemon=True).start()
    
    # 启动服务器
    port = int(os.environ.get('PORT', 5002))
    print(f"化学海龟汤服务器启动在端口 {port}")
    app.run(host='0.0.0.0', port=port, debug=False)