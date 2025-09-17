# 海龟汤游戏平台 - API接口文档

## 1. 接口概览

### 1.1 基本信息
- **Base URL**: `http://127.0.0.1:5001` (开发环境)
- **协议**: HTTP/HTTPS
- **数据格式**: JSON
- **字符编码**: UTF-8

### 1.2 通用规范

#### 1.2.1 请求头
```http
Content-Type: application/json
Accept: application/json
```

#### 1.2.2 响应格式
```json
// 成功响应
{
  "success": true,
  "data": {...},
  "message": "操作成功"
}

// 错误响应  
{
  "error": "错误信息描述"
}
```

#### 1.2.3 通用错误码
| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 400 | 请求参数错误 |
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

---

## 2. 房间管理 API

### 2.1 创建房间

**接口说明**: 创建游戏房间，返回邀请码

**请求信息**:
- **Method**: `POST`
- **URL**: `/api/create_room`

**请求参数**:
```json
{
  "nickname": "string, 必填, 用户昵称",
  "base_url": "string, 必填, OpenAI API地址", 
  "api_key": "string, 必填, OpenAI API密钥",
  "model": "string, 必填, AI模型名称"
}
```

**响应数据**:
```json
// 成功
{
  "code": "ABCD12" // 6位邀请码
}

// 失败
{
  "error": "参数不完整"
}
```

**示例**:
```javascript
// 请求
fetch('/api/create_room', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    nickname: "房主小明",
    base_url: "http://api.0ha.top/v1",
    api_key: "sk-xxxx",
    model: "gpt-4o-mini"
  })
})

// 响应
{
  "code": "ABCD12"
}
```

### 2.2 加入房间

**接口说明**: 通过邀请码加入已存在的房间

**请求信息**:
- **Method**: `POST`
- **URL**: `/api/join_room`

**请求参数**:
```json
{
  "nickname": "string, 必填, 用户昵称",
  "code": "string, 必填, 6位邀请码"
}
```

**响应数据**:
```json
// 成功
{
  "success": true,
  "room": {
    "owner": "房主昵称",
    "model": "AI模型名称"
  }
}

// 失败
{
  "error": "房间不存在" // 或 "昵称已存在"
}
```

### 2.3 删除房间

**接口说明**: 房主删除房间（仅房主可操作）

**请求信息**:
- **Method**: `POST`
- **URL**: `/api/delete_room`

**请求参数**:
```json
{
  "code": "string, 必填, 房间邀请码",
  "nickname": "string, 必填, 操作者昵称"
}
```

**响应数据**:
```json
// 成功
{
  "success": true
}

// 失败
{
  "error": "只有房主可以删除房间"
}
```

---

## 3. 用户状态 API

### 3.1 心跳检测

**接口说明**: 维持用户在线状态，定期调用

**请求信息**:
- **Method**: `POST`
- **URL**: `/api/heartbeat`

**请求参数**:
```json
{
  "code": "string, 必填, 房间邀请码",
  "nickname": "string, 必填, 用户昵称"
}
```

**响应数据**:
```json
{
  "success": true
}
```

### 3.2 获取在线用户

**接口说明**: 获取房间内在线用户列表

**请求信息**:
- **Method**: `POST`
- **URL**: `/api/get_online_users`

**请求参数**:
```json
{
  "code": "string, 必填, 房间邀请码"
}
```

**响应数据**:
```json
{
  "users": ["用户1", "用户2", "用户3"]
}
```

---

## 4. 消息系统 API

### 4.1 发送AI对话消息

**接口说明**: 向AI主持人发送问题，异步处理

**请求信息**:
- **Method**: `POST`
- **URL**: `/api/send_message`

**请求参数**:
```json
{
  "code": "string, 必填, 房间邀请码",
  "nickname": "string, 必填, 发送者昵称", 
  "content": "string, 必填, 消息内容"
}
```

**响应数据**:
```json
{
  "msg_id": "uuid-string", // 消息ID，用于获取AI回复
  "status": "pending"
}
```

### 4.2 获取AI回复

**接口说明**: 通过消息ID获取AI异步处理结果

**请求信息**:
- **Method**: `POST`
- **URL**: `/api/get_ai_reply`

**请求参数**:
```json
{
  "msg_id": "string, 必填, 消息ID"
}
```

**响应数据**:
```json
// 处理中
{
  "status": "pending"
}

// 处理完成
{
  "reply": "AI回复内容",
  "popup": "恭喜过关" // 可选，胜利提示
}

// 错误
{
  "error": "无效的消息ID"
}
```

### 4.3 获取消息列表

**接口说明**: 获取房间内所有AI对话消息历史

**请求信息**:
- **Method**: `POST`
- **URL**: `/api/get_messages`

**请求参数**:
```json
{
  "code": "string, 必填, 房间邀请码"
}
```

**响应数据**:
```json
{
  "messages": [
    {
      "role": "user", // user/assistant/system
      "content": "消息内容",
      "nickname": "发送者昵称"
    }
  ],
  "passed": false // 是否已通关
}
```

### 4.4 发送群聊消息

**接口说明**: 发送无AI参与的群聊消息

**请求信息**:
- **Method**: `POST`
- **URL**: `/api/send_chat_message`

**请求参数**:
```json
{
  "code": "string, 必填, 房间邀请码",
  "nickname": "string, 必填, 发送者昵称",
  "content": "string, 必填, 消息内容"
}
```

**响应数据**:
```json
{
  "success": true
}
```

### 4.5 获取群聊消息

**接口说明**: 获取房间群聊消息列表

**请求信息**:
- **Method**: `POST`
- **URL**: `/api/get_chat_messages`

**请求参数**:
```json
{
  "code": "string, 必填, 房间邀请码"
}
```

**响应数据**:
```json
{
  "messages": [
    {
      "nickname": "发送者昵称",
      "content": "消息内容", 
      "time": 1694780800 // Unix时间戳
    }
  ]
}
```

---

## 5. 故事管理 API

### 5.1 上传故事文件

**接口说明**: 房主上传故事JSON文件到房间

**请求信息**:
- **Method**: `POST`
- **URL**: `/api/upload_story`
- **Content-Type**: `multipart/form-data`

**请求参数**:
```
code: string, 必填, 房间邀请码
nickname: string, 必填, 操作者昵称
file: file[], 必填, JSON格式故事文件(可多个)
```

**文件格式要求**:
- 文件类型: JSON
- 文件大小: 最大20MB
- 数据结构:
```json
// 单个故事
{
  "surface": "故事题目",
  "answer": "完整答案",
  "victory_condition": "获胜条件",
  "additional": "补充说明"
}

// 批量故事
[
  {...}, {...}
]
```

**响应数据**:
```json
// 成功
{
  "success": true,
  "count": 3 // 上传故事数量
}

// 失败  
{
  "error": "文件大小不能超过20MB"
}
```

### 5.2 切换当前故事

**接口说明**: 房主切换房间当前使用的故事

**请求信息**:
- **Method**: `POST`
- **URL**: `/api/set_story`

**请求参数**:
```json
{
  "code": "string, 必填, 房间邀请码",
  "nickname": "string, 必填, 操作者昵称",
  "index": "number, 必填, 故事索引(从0开始)"
}
```

**响应数据**:
```json
{
  "success": true
}
```

### 5.3 获取当前故事

**接口说明**: 获取房间当前故事信息

**请求信息**:
- **Method**: `POST`
- **URL**: `/api/get_current_story`

**请求参数**:
```json
{
  "code": "string, 必填, 房间邀请码"
}
```

**响应数据**:
```json
// 成功
{
  "surface": "故事题目",
  "victory_condition": "获胜条件",
  "answer": "完整答案" // 只有已揭晓时才返回
}

// 无故事
{
  "error": "暂无题目"
}
```

### 5.4 揭晓答案

**接口说明**: 房主手动揭晓当前故事答案

**请求信息**:
- **Method**: `POST`
- **URL**: `/api/reveal_answer`

**请求参数**:
```json
{
  "code": "string, 必填, 房间邀请码",
  "nickname": "string, 必填, 操作者昵称"
}
```

**响应数据**:
```json
{
  "success": true
}
```

---

## 6. 故事广场 API

### 6.1 获取广场故事列表

**接口说明**: 获取已发布的故事广场列表

**请求信息**:
- **Method**: `GET`
- **URL**: `/api/get_plaza_stories`

**响应数据**:
```json
{
  "stories": [
    {
      "name": "故事名称",
      "id": "#00001", // 故事编号
      "surface": "故事题目",
      "filename": "uuid.json" // 内部文件名
    }
  ]
}
```

### 6.2 上传故事到广场

**接口说明**: 用户上传故事文件到广场（待审核）

**请求信息**:
- **Method**: `POST`
- **URL**: `/api/upload_to_plaza`
- **Content-Type**: `multipart/form-data`

**请求参数**:
```
name: string, 必填, 故事名称
file: file, 必填, JSON格式故事文件
```

**响应数据**:
```json
// 成功
{
  "success": true,
  "message": "故事已上传，等待管理员审核"
}

// 失败
{
  "error": "只支持JSON文件"
}
```

### 6.3 在线编辑提交故事

**接口说明**: 在线编辑并提交故事到广场（待审核）

**请求信息**:
- **Method**: `POST`
- **URL**: `/api/submit_story_online`

**请求参数**:
```json
{
  "name": "string, 必填, 故事名称",
  "surface": "string, 必填, 故事题目",
  "answer": "string, 必填, 完整答案", 
  "victory_condition": "string, 必填, 获胜条件",
  "additional": "string, 可选, 补充说明"
}
```

**响应数据**:
```json
{
  "success": true,
  "message": "故事已提交，等待管理员审核",
  "id": "#00005" // 分配的故事编号
}
```

### 6.4 从广场加载故事

**接口说明**: 房主从故事广场加载故事到房间

**请求信息**:
- **Method**: `POST`
- **URL**: `/api/load_story_from_plaza`

**请求参数**:
```json
{
  "code": "string, 必填, 房间邀请码",
  "nickname": "string, 必填, 操作者昵称",
  "filename": "string, 必填, 故事文件名"
}
```

**响应数据**:
```json
{
  "success": true,
  "count": 1 // 加载故事数量
}
```

---

## 7. 管理员 API

### 7.1 管理员登录

**接口说明**: 管理员登录后台

**请求信息**:
- **Method**: `POST`
- **URL**: `/admin`
- **Content-Type**: `application/x-www-form-urlencoded`

**请求参数**:
```
username: string, 必填, 管理员用户名
password: string, 必填, 管理员密码
```

**响应数据**:
登录成功后设置session，重定向到管理面板页面

### 7.2 获取待审核故事

**接口说明**: 获取待审核的故事列表（需管理员权限）

**请求信息**:
- **Method**: `GET`
- **URL**: `/api/get_pending_stories`

**权限要求**: 需要管理员session

**响应数据**:
```json
{
  "stories": [
    {
      "name": "故事名称",
      "id": "#00001",
      "surface": "故事题目", 
      "filename": "uuid.json"
    }
  ]
}
```

### 7.3 审核通过故事

**接口说明**: 管理员审核通过故事，发布到广场

**请求信息**:
- **Method**: `POST`
- **URL**: `/api/approve_story`
- **Content-Type**: `application/x-www-form-urlencoded`

**权限要求**: 需要管理员session

**请求参数**:
```
filename: string, 必填, 待审核故事文件名
```

**响应数据**:
```json
{
  "success": true
}
```

### 7.4 拒绝故事

**接口说明**: 管理员拒绝故事，删除待审核文件

**请求信息**:
- **Method**: `POST`
- **URL**: `/api/reject_story`
- **Content-Type**: `application/x-www-form-urlencoded`

**权限要求**: 需要管理员session

**请求参数**:
```
filename: string, 必填, 待审核故事文件名
```

**响应数据**:
```json
{
  "success": true
}
```

### 7.5 删除已发布故事

**接口说明**: 管理员删除已发布的故事

**请求信息**:
- **Method**: `POST`
- **URL**: `/api/delete_released_story`
- **Content-Type**: `application/x-www-form-urlencoded`

**权限要求**: 需要管理员session

**请求参数**:
```
filename: string, 必填, 已发布故事文件名
```

**响应数据**:
```json
{
  "success": true
}
```

### 7.6 管理员删除房间

**接口说明**: 管理员强制删除房间

**请求信息**:
- **Method**: `POST`
- **URL**: `/admin/delete_room`
- **Content-Type**: `application/x-www-form-urlencoded`

**权限要求**: 需要管理员session

**请求参数**:
```
code: string, 必填, 房间邀请码
```

**响应数据**:
```json
{
  "success": true
}
```

---

## 8. 系统配置 API

### 8.1 获取系统选项

**接口说明**: 获取系统配置的下拉选项

**请求信息**:
- **Method**: `GET`
- **URL**: `/api/get_options`

**响应数据**:
```json
{
  "options": {
    "models": ["gpt-4o-mini", "o3-mini-2025-01-31"],
    "base_urls": ["http://api.0ha.top/v1"],
    "api_keys": ["sk-xxxx"]
  }
}
```

### 8.2 保存系统选项

**接口说明**: 管理员保存系统配置选项

**请求信息**:
- **Method**: `POST`
- **URL**: `/api/save_options`

**权限要求**: 需要管理员session

**请求参数**:
```json
{
  "models": ["string array, AI模型列表"],
  "base_urls": ["string array, API地址列表"], 
  "api_keys": ["string array, API密钥列表"]
}
```

**响应数据**:
```json
{
  "success": true
}
```

### 8.3 获取公告

**接口说明**: 获取平台公告内容

**请求信息**:
- **Method**: `GET`
- **URL**: `/api/get_announcements`

**响应数据**:
```json
{
  "content": "公告内容文本"
}
```

### 8.4 保存公告

**接口说明**: 管理员保存平台公告

**请求信息**:
- **Method**: `POST`
- **URL**: `/api/save_announcements`

**权限要求**: 需要管理员session

**请求参数**:
```json
{
  "content": "string, 公告内容"
}
```

**响应数据**:
```json
{
  "success": true
}
```

---

## 9. 页面路由

### 9.1 静态页面
- `GET /` - 主页
- `GET /story_plaza` - 故事广场页面
- `GET /admin` - 管理员面板页面

---

## 10. 数据模型

### 10.1 消息对象
```typescript
interface Message {
  role: 'user' | 'assistant' | 'system';
  content: string;
  nickname: string;
  time?: number; // 群聊消息时间戳
}
```

### 10.2 故事对象
```typescript
interface Story {
  surface: string;         // 故事题目/汤面
  answer: string;          // 完整答案/汤底  
  victory_condition: string; // 获胜条件
  additional?: string;     // 补充说明
}
```

### 10.3 广场故事对象
```typescript
interface PlazaStory {
  name: string;      // 故事名称
  id: string;        // 编号 (#00001)
  surface: string;   // 故事题目
  filename: string;  // 文件名
  data?: Story;      // 完整故事数据
}
```

### 10.4 房间对象
```typescript
interface Room {
  owner: string;              // 房主昵称
  base_url: string;           // OpenAI API地址
  api_key: string;            // API密钥
  model: string;              // AI模型
  messages: Message[];        // 游戏消息历史
  members: Record<string, {nickname: string}>; // 成员
  stories: Story[];           // 故事列表
  current_story?: number;     // 当前故事索引
  chat_messages: Message[];   // 群聊消息
  online_users: Record<string, number>; // 在线用户心跳
  reveal_answer_flag: boolean; // 答案揭晓标志
  passed: boolean;            // 通关标志
}
```

---

## 11. 错误处理

### 11.1 常见错误码
```javascript
const ERROR_CODES = {
  PARAMS_INCOMPLETE: '参数不完整',
  ROOM_NOT_EXIST: '房间不存在', 
  ROOM_NOT_JOINED: '未加入房间',
  NICKNAME_EXISTS: '昵称已存在',
  PERMISSION_DENIED: '权限不足',
  FILE_TOO_LARGE: '文件大小不能超过20MB',
  FILE_FORMAT_ERROR: '只支持JSON文件',
  STORY_NOT_FOUND: '故事不存在',
  AI_ERROR: 'AI错误',
  UNAUTHORIZED: '未登录'
};
```

### 11.2 错误响应处理
```javascript
// 客户端错误处理示例
async function apiCall(url, options) {
  try {
    const response = await fetch(url, options);
    const data = await response.json();
    
    if (data.error) {
      throw new Error(data.error);
    }
    
    return data;
  } catch (error) {
    console.error('API调用失败:', error.message);
    // 统一错误处理逻辑
    handleError(error.message);
    throw error;
  }
}
```

---

## 12. 开发注意事项

### 12.1 Session管理
- 管理员登录后通过Flask session维持状态
- 移动端开发需要实现token机制替代session
- 注意跨域请求的凭证携带

### 12.2 轮询机制
- 消息轮询建议间隔2-3秒
- 心跳轮询建议间隔30秒
- 注意网络异常时的重试逻辑

### 12.3 文件上传
- 支持多文件上传
- 需要校验文件类型和大小
- FormData方式提交

### 12.4 异步处理
- AI对话采用异步处理机制
- 需要轮询获取处理结果
- 注意超时处理

### 12.5 移动端适配建议
- 实现用户登录体系
- 使用WebSocket替代轮询机制  
- 优化文件上传体验
- 添加离线缓存机制
- 实现推送通知

---

**文档版本**: v1.0  
**创建日期**: 2025-09-15  
**更新日期**: 2025-09-15  
**维护人员**: 技术团队