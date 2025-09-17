# 化学海龟汤服务器 API 文档

## 基本信息
- 服务器地址: http://localhost:5002
- 健康检查: GET /health

## 核心游戏接口

### 1. 开始新游戏
**POST** /api/game/start

请求体:
```json
{
  "category": "氧化还原反应",  // 可选，指定分类
  "difficulty": 2,             // 可选，指定难度1-5
  "problem_id": "chem_001"     // 可选，指定题目ID
}
```

响应:
```json
{
  "session_id": "uuid-string",
  "problem": {
    "id": "chem_001",
    "title": "蓝瓶子实验",
    "surface": "题目描述",
    "category": "氧化还原反应",
    "difficulty": 2,
    "hints_available": 4
  }
}
```

### 2. 提问
**POST** /api/game/ask

请求体:
```json
{
  "session_id": "session-uuid",
  "question": "这是氧化还原反应吗？"
}
```

响应:
```json
{
  "response": "是",
  "message_id": "uuid",
  "status": "playing",
  "questions_asked": 1
}
```

### 3. 获取提示
**POST** /api/game/hint

请求体:
```json
{
  "session_id": "session-uuid"
}
```

响应:
```json
{
  "hint": "提示1：这涉及到氧化还原反应",
  "hints_remaining": 3,
  "hints_used": 1
}
```

### 4. 查询游戏状态
**GET** /api/game/status?session_id=session-uuid

响应:
```json
{
  "status": "playing",
  "questions_asked": 3,
  "hints_used": 1,
  "time_elapsed": 120
}
```

## 题库管理接口

### 1. 获取分类
**GET** /api/categories

### 2. 获取题目列表
**GET** /api/problems?category=氧化还原反应&difficulty=2

### 3. 随机获取题目
**GET** /api/problems/random?category=氧化还原反应

## 内置题目

目前包含3个化学题目：

1. **蓝瓶子实验** (chem_001) - 氧化还原反应/指示剂反应
2. **神秘的银镜** (chem_002) - 氧化还原反应/银镜反应  
3. **变色魔术师** (chem_003) - 酸碱反应/指示剂变色

## 鸿蒙APP集成示例

### 开始游戏
```javascript
// 开始新游戏
async function startGame() {
  const response = await fetch('http://localhost:5002/api/game/start', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({})
  });
  const data = await response.json();
  return data;
}
```

### 提问交互
```javascript
// 向AI提问
async function askQuestion(sessionId, question) {
  const response = await fetch('http://localhost:5002/api/game/ask', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      session_id: sessionId,
      question: question
    })
  });
  return await response.json();
}
```

### 获取提示
```javascript
// 获取提示
async function getHint(sessionId) {
  const response = await fetch('http://localhost:5002/api/game/hint', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      session_id: sessionId
    })
  });
  return await response.json();
}
```