-- 创建数据库
CREATE DATABASE IF NOT EXISTS kaguchat;
USE kaguchat;

-- 创建 Users 表
CREATE TABLE Users (
    user_id BIGINT PRIMARY KEY AUTO_INCREMENT,  -- 实体完整性：主键唯一且非空
    username VARCHAR(50) NOT NULL,
    nickname VARCHAR(50),
    phone VARCHAR(20) NOT NULL,
    password VARCHAR(255) NOT NULL,
    avatar_url VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uk_phone UNIQUE (phone),  -- 内容完整性：phone 唯一，命名约束
    CONSTRAINT chk_phone_format CHECK (phone REGEXP '^[0-9]{11}$')  -- 内容完整性：11位数字，命名约束
);

-- 创建 Friends 表
CREATE TABLE Friends (
    friendship_id BIGINT PRIMARY KEY AUTO_INCREMENT,  -- 实体完整性
    user_id BIGINT NOT NULL,
    friend_id BIGINT NOT NULL,
    remark VARCHAR(50),
    status TINYINT DEFAULT 1,    -- 0:待通过, 1:好友
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,  -- 参照完整性：级联删除
    FOREIGN KEY (friend_id) REFERENCES Users(user_id) ON DELETE CASCADE,  -- 参照完整性：级联删除
    CONSTRAINT chk_status_value CHECK (status IN (0, 1)),  -- 内容完整性：status 值域，命名约束
    CONSTRAINT uk_user_friend UNIQUE (user_id, friend_id)  -- 内容完整性：避免重复好友关系，命名约束
);

-- 创建 Groups 表
CREATE TABLE `Groups` (
    group_id BIGINT PRIMARY KEY AUTO_INCREMENT,  -- 实体完整性
    group_name VARCHAR(100) NOT NULL,
    owner_id BIGINT NOT NULL,
    group_avatar VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (owner_id) REFERENCES Users(user_id) ON DELETE CASCADE,  -- 参照完整性
    CONSTRAINT uk_group_name UNIQUE (group_name)  -- 内容完整性：群名唯一，命名约束
);

-- 创建 Group_Members 表
CREATE TABLE Group_Members (
    member_id BIGINT PRIMARY KEY AUTO_INCREMENT,  -- 实体完整性
    group_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    role TINYINT DEFAULT 0,    -- 0:普通成员, 1:管理员, 2:群主
    join_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (group_id) REFERENCES `Groups`(group_id) ON DELETE CASCADE,  -- 参照完整性
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,  -- 参照完整性
    CONSTRAINT chk_role_value CHECK (role IN (0, 1, 2)),  -- 内容完整性：role 值域，命名约束
    CONSTRAINT uk_group_user UNIQUE (group_id, user_id)  -- 内容完整性：避免重复成员，命名约束
);

-- 创建 Messages 表
CREATE TABLE Messages (
    message_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    sender_id BIGINT NOT NULL,
    receiver_id BIGINT,
    group_id BIGINT,
    content TEXT NOT NULL,
    message_type TINYINT DEFAULT 0,
    sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sender_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (receiver_id) REFERENCES Users(user_id) ON DELETE RESTRICT,  -- 改为 RESTRICT
    FOREIGN KEY (group_id) REFERENCES `Groups`(group_id) ON DELETE RESTRICT,  -- 改为 RESTRICT
    CONSTRAINT chk_message_type CHECK (message_type IN (0, 1, 2)),
    CONSTRAINT chk_receiver_or_group CHECK (receiver_id IS NOT NULL OR group_id IS NOT NULL),
    INDEX idx_sent_at (sent_at)
);

-- 创建 Message_Attachments 表
CREATE TABLE Message_Attachments (
    attachment_id BIGINT PRIMARY KEY AUTO_INCREMENT,  -- 实体完整性
    message_id BIGINT NOT NULL,
    file_url VARCHAR(255) NOT NULL,
    file_type VARCHAR(50),
    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (message_id) REFERENCES Messages(message_id) ON DELETE CASCADE,  -- 参照完整性
    CONSTRAINT chk_file_type CHECK (file_type IN ('image', 'file', NULL))  -- 内容完整性：file_type 值域，命名约束
);

-- 视图1：行列子集视图 ContactListView
CREATE VIEW ContactListView AS
-- 好友列表
SELECT 
    f.friend_id AS contact_id,
    'friend' AS type,
    u.nickname AS name,
    u.avatar_url,
    (SELECT m.content 
     FROM Messages m 
     WHERE (m.sender_id = f.user_id AND m.receiver_id = f.friend_id) 
        OR (m.sender_id = f.friend_id AND m.receiver_id = f.user_id) 
     ORDER BY m.sent_at DESC 
     LIMIT 1) AS last_message,
    (SELECT m.sent_at 
     FROM Messages m 
     WHERE (m.sender_id = f.user_id AND m.receiver_id = f.friend_id) 
        OR (m.sender_id = f.friend_id AND m.receiver_id = f.user_id) 
     ORDER BY m.sent_at DESC 
     LIMIT 1) AS last_message_time
FROM Friends f
JOIN Users u ON f.friend_id = u.user_id
WHERE f.status = 1  -- 仅显示已通过的好友
  AND f.user_id = 1  -- 当前用户ID（示例为1）

UNION

-- 群聊列表
SELECT 
    g.group_id AS contact_id,
    'group' AS type,
    g.group_name AS name,
    g.group_avatar AS avatar_url,
    (SELECT m.content 
     FROM Messages m 
     WHERE m.group_id = g.group_id 
     ORDER BY m.sent_at DESC 
     LIMIT 1) AS last_message,
    (SELECT m.sent_at 
     FROM Messages m 
     WHERE m.group_id = g.group_id 
     ORDER BY m.sent_at DESC 
     LIMIT 1) AS last_message_time
FROM `Groups` g
JOIN Group_Members gm ON g.group_id = gm.group_id
WHERE gm.user_id = 1;  -- 当前用户ID（示例为1）

-- 视图2：带表达式的视图 ChatHistoryView
CREATE VIEW ChatHistoryView AS
SELECT 
    m.message_id,
    m.sender_id,
    u.nickname AS sender_nickname,
    u.avatar_url AS sender_avatar,
    m.content,
    CASE 
        WHEN m.receiver_id IS NOT NULL THEN 'Private'
        WHEN m.group_id IS NOT NULL THEN 'Group'
        ELSE 'Unknown'
    END AS chat_type,
    CASE m.message_type 
        WHEN 0 THEN 'Text'
        WHEN 1 THEN 'Image'
        WHEN 2 THEN 'File'
        ELSE 'Unknown'
    END AS message_type_desc,
    m.sent_at,
    -- 显示接收方信息
    CASE
        WHEN m.receiver_id IS NOT NULL THEN (SELECT nickname FROM Users WHERE user_id = m.receiver_id)
        WHEN m.group_id IS NOT NULL THEN (SELECT group_name FROM `Groups` WHERE group_id = m.group_id)
        ELSE 'Unknown'
    END AS receiver_name
FROM Messages m
JOIN Users u ON m.sender_id = u.user_id
WHERE m.sender_id = 1  -- 只显示用户1发送的消息
ORDER BY m.sent_at ASC;

-- 视图3：分组视图 GroupMessageStatsView
CREATE VIEW GroupMessageStatsView AS
SELECT 
    g.group_id,
    g.group_name,
    COUNT(m.message_id) AS message_count
FROM `Groups` g
JOIN Group_Members gm ON g.group_id = gm.group_id 
                     AND gm.user_id = 1 
                     AND gm.role IN (1, 2)
LEFT JOIN Messages m ON g.group_id = m.group_id 
                    AND m.sender_id = 1  -- 添加：只统计用户1发送的消息
GROUP BY g.group_id, g.group_name;