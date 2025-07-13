// 页面切换
function showPage(page) {
    document.getElementById('page-home').style.display = page === 'home' ? '' : 'none';
    document.getElementById('page-create').style.display = page === 'create' ? '' : 'none';
    document.getElementById('page-join').style.display = page === 'join' ? '' : 'none';
    document.getElementById('page-chat').style.display = page === 'chat' ? '' : 'none';
    if (page === 'chat') {
        document.getElementById('user-input').focus();
    }
}

// 全局状态
let roomCode = '';
let nickname = '';
let isOwner = false;
let polling = null;
let isUploading = false;

// 当前题目信息缓存
let currentStoryInfo = null;
let isAnswerRevealed = false;

// ========== 无AI群聊相关 ==========
let chatPolling = null;
let onlinePolling = null;

// 创建房间
const createBtn = document.getElementById('create-room-btn');
createBtn.onclick = async function() {
    const nick = document.getElementById('create-nickname').value.trim();
    const base_url = document.getElementById('create-base-url').value.trim();
    const api_key = document.getElementById('create-api-key').value.trim();
    const model = document.getElementById('create-model').value.trim();
    if (!nick || !base_url || !api_key || !model) {
        document.getElementById('create-error').textContent = '请填写完整信息';
        return;
    }
    createBtn.disabled = true;
    document.getElementById('create-error').textContent = '';
    try {
        const res = await fetch('/api/create_room', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({nickname: nick, base_url, api_key, model})
        });
        const data = await res.json();
        if (data.code) {
            roomCode = data.code;
            nickname = nick;
            isOwner = true;
            enterChat();
        } else {
            document.getElementById('create-error').textContent = data.error || '创建失败';
        }
    } catch (e) {
        document.getElementById('create-error').textContent = '网络错误';
    }
    createBtn.disabled = false;
};

// 加入房间
const joinBtn = document.getElementById('join-room-btn');
joinBtn.onclick = async function() {
    const nick = document.getElementById('join-nickname').value.trim();
    const code = document.getElementById('join-code').value.trim().toUpperCase();
    if (!nick || !code) {
        document.getElementById('join-error').textContent = '请填写完整信息';
        return;
    }
    joinBtn.disabled = true;
    document.getElementById('join-error').textContent = '';
    try {
        const res = await fetch('/api/join_room', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({nickname: nick, code})
        });
        const data = await res.json();
        if (data.success) {
            roomCode = code;
            nickname = nick;
            isOwner = false;
            enterChat(data.room);
        } else {
            document.getElementById('join-error').textContent = data.error || '加入失败';
        }
    } catch (e) {
        document.getElementById('join-error').textContent = '网络错误';
    }
    joinBtn.disabled = false;
};

// 进入群聊页
function enterChat(roomInfo) {
    showPage('chat');
    document.getElementById('invite-code').textContent = roomCode;
    document.getElementById('room-info-text').textContent = roomInfo ? `房主: ${roomInfo.owner} | 模型: ${roomInfo.model}` : '';
    window.roomOwner = roomInfo ? roomInfo.owner : '';
    document.getElementById('delete-room-btn').style.display = isOwner ? '' : 'none';
    document.getElementById('user-input').value = '';
    document.getElementById('chat-box').innerHTML = '';
    document.getElementById('story-ops').style.display = isOwner ? '' : 'none';
    fetchCurrentStory();
    startPolling();
    saveSession();
    pollChatMessages();
    pollOnlineUsers();
    if (chatPolling) clearInterval(chatPolling);
    if (onlinePolling) clearInterval(onlinePolling);
    chatPolling = setInterval(pollChatMessages, 2000);
    onlinePolling = setInterval(pollOnlineUsers, 5000);
    startHeartbeat();
}

// 发送消息
const sendBtn = document.getElementById('send-btn');
sendBtn.onclick = async function() {
    const content = document.getElementById('user-input').value.trim();
    if (!content) return;
    sendBtn.disabled = true;
    document.getElementById('user-input').disabled = true;
    try {
        await fetch('/api/send_message', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({code: roomCode, nickname, content})
        });
        document.getElementById('user-input').value = '';
        await pollMessages();
    } catch (e) {}
    sendBtn.disabled = false;
    document.getElementById('user-input').disabled = false;
    document.getElementById('user-input').focus();
};

document.getElementById('user-input').addEventListener('keydown', function(e) {
    if (e.key === 'Enter') {
        sendBtn.click();
    }
});

// 轮询消息
function startPolling() {
    if (polling) clearInterval(polling);
    pollMessages();
    polling = setInterval(pollMessages, 2000);
}
async function pollMessages() {
    if (!roomCode) return;
    try {
        const res = await fetch('/api/get_messages', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({code: roomCode})
        });
        const data = await res.json();
        if (data.messages) {
            renderMessages(data.messages);
        }
    } catch (e) {}
}
function renderMessages(msgs) {
    const chatBox = document.getElementById('chat-box');
    chatBox.innerHTML = '';
    for (const msg of msgs) {
        if (msg.role === 'system') {
            const div = document.createElement('div');
            div.style = 'text-align:center;color:#94a3b8;font-size:13px;margin:6px 0;';
            div.innerHTML = escapeHtml(msg.content);
            chatBox.appendChild(div);
            continue;
        }
        const div = document.createElement('div');
        div.className = 'bubble ' + (msg.role === 'user' ? 'msg-user' : 'msg-ai');
        div.innerHTML = `<span class=\"msg-nickname\">${msg.nickname}</span>: ${escapeHtml(msg.content)}`;
        chatBox.appendChild(div);
    }
    chatBox.scrollTop = chatBox.scrollHeight;
}
function escapeHtml(text) {
    if (!text) return '';
    return text.replace(/[&<>"']/g, function(c) {
        return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];
    }).replace(/\n/g, '<br>');
}

// 删除房间
const deleteBtn = document.getElementById('delete-room-btn');
deleteBtn.onclick = async function() {
    if (!confirm('确定要删除房间吗？')) return;
    try {
        await fetch('/api/delete_room', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({code: roomCode, nickname})
        });
        alert('房间已删除');
        leaveRoom();
    } catch (e) {}
};

// 退出房间
function leaveRoom() {
    if (polling) clearInterval(polling);
    roomCode = '';
    nickname = '';
    isOwner = false;
    localStorage.removeItem('haigui_room');
    showPage('home');
}

// 新增：上传题目、切换题目、显示当前题面
function renderStory(story) {
    currentStoryInfo = story;
    isAnswerRevealed = !!(story && story.answer && story.answer.length > 0);
    const storyDiv = document.getElementById('current-story');
    let html = '';
    if (!story) {
        html = '<em>暂无题目，请房主上传海龟汤题目</em>';
    } else {
        html += `<div style=\"margin-bottom:8px;\"><b>汤面：</b>${escapeHtml(story.surface || '')}</div>`;
        if (story.victory_condition) {
            html += `<div style=\"color:#64748b;\"><b>胜利条件：</b>${escapeHtml(story.victory_condition)}</div>`;
        }
        if (story.answer && story.answer.length > 0) {
            html += `<div style=\"color:#f87171;margin-top:8px;\"><b>答案揭晓：</b>${escapeHtml(story.answer)}</div>`;
        }
    }
    // 房主操作区
    if (isOwner && story) {
        html += `<div style=\"margin-top:10px;\">`;
        if (!story.answer || story.answer.length === 0) {
            html += `<button class=\"btn\" id=\"reveal-answer-btn\">揭晓答案</button>`;
        }
        html += `</div>`;
    }
    storyDiv.innerHTML = html;
    // 绑定房主操作按钮
    if (isOwner && story) {
        const revealBtn = document.getElementById('reveal-answer-btn');
        if (revealBtn) {
            revealBtn.onclick = async function() {
                if (!confirm('确定要揭晓答案吗？')) return;
                await fetch('/api/reveal_answer', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({code: roomCode, nickname})
                });
                await fetchCurrentStory();
                await pollMessages();
            };
        }
    }
    updateInputStatus();
}

function updateInputStatus() {
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    if (!currentStoryInfo) {
        userInput.disabled = true;
        sendBtn.disabled = true;
        return;
    }
    if (isAnswerRevealed) {
        userInput.disabled = true;
        sendBtn.disabled = true;
        return;
    }
    userInput.disabled = false;
    sendBtn.disabled = false;
}

async function fetchCurrentStory() {
    if (!roomCode) return;
    try {
        const res = await fetch('/api/get_current_story', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({code: roomCode})
        });
        const data = await res.json();
        if (data.surface !== undefined) {
            renderStory({surface: data.surface, additional: data.additional});
        } else {
            renderStory(null);
        }
    } catch (e) {
        renderStory(null);
    }
}

// 上传题目
function setupUploadBtn() {
    const uploadBtn = document.getElementById('upload-story-btn');
    const fileInput = document.getElementById('upload-story-input');
    uploadBtn.onclick = function() {
        fileInput.click();
    };
    fileInput.onchange = async function() {
        if (!fileInput.files.length || isUploading) return;
        isUploading = true;
        uploadBtn.disabled = true;
        const formData = new FormData();
        formData.append('code', roomCode);
        formData.append('nickname', nickname);
        for (let i = 0; i < fileInput.files.length; i++) {
            formData.append('file', fileInput.files[i]);
        }
        try {
            const res = await fetch('/api/upload_story', {
                method: 'POST',
                body: formData
            });
            const data = await res.json();
            if (data.success) {
                await fetchCurrentStory();
                await fetchStoryList();
                alert('题目上传成功');
            } else {
                alert(data.error || '上传失败');
            }
        } catch (e) {
            alert('上传失败');
        }
        fileInput.value = '';
        isUploading = false;
        uploadBtn.disabled = false;
    };
}

// 获取题库列表并渲染切换下拉框
async function fetchStoryList() {
    if (!roomCode || !isOwner) return;
    try {
        const res = await fetch('/api/get_current_story', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({code: roomCode})
        });
        // 题库数量通过上传后返回的count，前端需维护
        // 这里简化为每次上传/切换后刷新页面即可
    } catch (e) {}
}

// 切换题目
async function setStoryIndex(idx) {
    if (!roomCode || !isOwner) return;
    try {
        const res = await fetch('/api/set_story', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({code: roomCode, nickname, index: idx})
        });
        const data = await res.json();
        if (data.success) {
            await fetchCurrentStory();
            await pollMessages();
            saveSession();
        } else {
            alert(data.error || '切换失败');
        }
    } catch (e) {
        alert('切换失败');
    }
}

// 页面初始化，插入题目上传和切换控件
(function(){
    const chatPage = document.getElementById('page-chat');
    const storyOps = document.createElement('div');
    storyOps.id = 'story-ops';
    storyOps.style = 'margin-bottom:12px;display:none;text-align:center;';
    storyOps.innerHTML = `
        <input type="file" id="upload-story-input" accept=".json" multiple style="display:none">
        <button class="btn" id="upload-story-btn" style="margin-bottom:8px;">上传题目（json）</button>
        <select id="story-index-select" style="display:none;margin-left:8px;"></select>
    `;
    chatPage.insertBefore(storyOps, chatPage.firstChild);
    // 当前题目展示区
    const storyDiv = document.createElement('div');
    storyDiv.id = 'current-story';
    storyDiv.style = 'background:#f1f5f9;border-radius:10px;padding:12px 10px;margin-bottom:12px;min-height:48px;';
    chatPage.insertBefore(storyDiv, storyOps.nextSibling);
    setupUploadBtn();
})();

// 保持刷新后页面还在群聊页
function saveSession() {
    if (roomCode && nickname) {
        localStorage.setItem('haigui_room', JSON.stringify({roomCode, nickname, isOwner}));
    }
}
function loadSession() {
    const data = localStorage.getItem('haigui_room');
    if (data) {
        try {
            const obj = JSON.parse(data);
            roomCode = obj.roomCode;
            nickname = obj.nickname;
            isOwner = obj.isOwner;
            enterChat();
        } catch (e) {}
    }
}

// 页面加载时自动恢复
window.addEventListener('DOMContentLoaded', loadSession);

// 默认显示首页
showPage('home');

function renderChatMessages(msgs) {
    const box = document.getElementById('chat-box-chat');
    box.innerHTML = '';
    for (const msg of msgs) {
        let html = `<span class='msg-nickname' style='color:#3b82f6;'>${escapeHtml(msg.nickname)}</span>: `;
        let content = escapeHtml(msg.content);
        // @高亮
        const users = (currentOnlineUsers || []);
        users.forEach(u => {
            if (u && content.includes('@' + u)) {
                content = content.replaceAll('@' + u, `<span style='background:yellow;color:#d97706;padding:1px 4px;border-radius:4px;'>@${u}</span>`);
            }
        });
        html += content;
        const div = document.createElement('div');
        div.style = 'margin:2px 0;line-height:1.7;';
        div.innerHTML = html;
        box.appendChild(div);
    }
    box.scrollTop = box.scrollHeight;
}

let currentOnlineUsers = [];
function renderOnlineUsers(users) {
    currentOnlineUsers = users;
    // 渲染新用户列表
    const userList = document.getElementById('user-list');
    userList.innerHTML = '';
    users.forEach(u => {
        const div = document.createElement('div');
        div.style = 'display:flex;align-items:center;padding:6px 16px 6px 12px;margin-bottom:2px;border-radius:8px;transition:background 0.2s;cursor:pointer;';
        if (u === nickname) {
            div.style.background = '#dbeafe';
        } else {
            div.onmouseover = () => div.style.background = '#e0e7ff';
            div.onmouseout = () => div.style.background = '';
        }
        // 头像（首字母圆形）
        const avatar = document.createElement('div');
        avatar.textContent = u[0].toUpperCase();
        avatar.style = 'width:32px;height:32px;background:#3b82f6;color:#fff;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:bold;font-size:18px;margin-right:10px;box-shadow:0 2px 8px 0 rgba(59,130,246,0.08);';
        div.appendChild(avatar);
        // 昵称
        const nameSpan = document.createElement('span');
        nameSpan.textContent = u;
        nameSpan.style = 'font-size:15px;font-weight:500;color:#334155;';
        div.appendChild(nameSpan);
        // 标签
        const tag = document.createElement('span');
        tag.style = 'margin-left:10px;padding:2px 8px;border-radius:8px;font-size:12px;font-weight:bold;';
        if (u === window.roomOwner) {
            tag.textContent = '房主';
            tag.style.background = '#fef3c7';
            tag.style.color = '#b45309';
        } else {
            tag.textContent = '成员';
            tag.style.background = '#e0e7ff';
            tag.style.color = '#2563eb';
        }
        div.appendChild(tag);
        userList.appendChild(div);
    });
}

async function pollChatMessages() {
    if (!roomCode) return;
    try {
        const res = await fetch('/api/get_chat_messages', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({code: roomCode})
        });
        const data = await res.json();
        if (data.messages) renderChatMessages(data.messages);
    } catch (e) {}
}

async function pollOnlineUsers() {
    if (!roomCode) return;
    try {
        const res = await fetch('/api/get_online_users', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({code: roomCode})
        });
        const data = await res.json();
        if (data.users) renderOnlineUsers(data.users);
    } catch (e) {}
}

// 发送无AI群聊消息
const chatSendBtn = document.getElementById('chat-send-btn');
chatSendBtn.onclick = async function() {
    const input = document.getElementById('chat-input');
    const content = input.value.trim();
    if (!content) return;
    chatSendBtn.disabled = true;
    input.disabled = true;
    try {
        await fetch('/api/send_chat_message', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({code: roomCode, nickname, content})
        });
        input.value = '';
        await pollChatMessages();
    } catch (e) {}
    chatSendBtn.disabled = false;
    input.disabled = false;
    input.focus();
};
document.getElementById('chat-input').addEventListener('keydown', function(e) {
    if (e.key === 'Enter') {
        chatSendBtn.click();
    }
});

// 心跳机制
function startHeartbeat() {
    setInterval(async () => {
        if (!roomCode || !nickname) return;
        await fetch('/api/heartbeat', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({code: roomCode, nickname})
        });
    }, 30000);
} 