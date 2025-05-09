-- 插入用户数据
INSERT INTO Users (username, nickname, phone, password, avatar_url) VALUES
('user1', '用户1', '13800000001', 'password1', 'avatar1.jpg'),
('user2', '用户2', '13800000002', 'password2', 'avatar2.jpg'),
('user3', '用户3', '13800000003', 'password3', 'avatar3.jpg'),
('user4', '用户4', '13800000004', 'password4', 'avatar4.jpg'),
('user5', '用户5', '13800000005', 'password5', 'avatar5.jpg');

-- 插入好友关系
INSERT INTO Friends (user_id, friend_id, remark, status) VALUES
(1, 2, '好友2', 1),
(1, 3, '好友3', 1),
(2, 1, '好友1', 1),
(2, 4, '好友4', 1),
(3, 1, '好友1', 1),
(4, 2, '好友2', 1),
(5, 1, '好友1', 0); -- 待通过的好友请求

-- 插入群组数据
INSERT INTO `Groups` (group_name, owner_id, group_avatar) VALUES
('技术交流群', 1, 'group1.jpg'),
('学习小组', 2, 'group2.jpg'),
('闲聊群', 3, 'group3.jpg');

-- 插入群成员数据
INSERT INTO Group_Members (group_id, user_id, role) VALUES
(1, 1, 2), -- 群主
(1, 2, 1), -- 管理员
(1, 3, 0), -- 普通成员
(2, 2, 2), -- 群主
(2, 4, 0), -- 普通成员
(3, 3, 2), -- 群主
(3, 1, 0), -- 普通成员
(3, 5, 0); -- 普通成员

-- 插入消息数据
INSERT INTO Messages (sender_id, receiver_id, group_id, content, message_type) VALUES
-- 私聊消息
(1, 2, NULL, '你好，在吗？', 0),
(2, 1, NULL, '在的，有什么事吗？', 0),
(1, 3, NULL, '周末一起吃饭吗？', 0),
-- 群聊消息
(1, NULL, 1, '大家好，欢迎加入技术交流群', 1),
(2, NULL, 1, '谢谢群主', 1),
(3, NULL, 1, '新人报到', 1),
(3, NULL, 3, '今天天气真好', 2),
(5, NULL, 3, '是啊，适合出去玩', 2);

-- 插入消息附件
INSERT INTO Message_Attachments (message_id, file_url, file_type) VALUES
(4, 'http://example.com/file1.jpg', 'image'),
(7, 'http://example.com/file2.pdf', 'file');