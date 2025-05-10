CREATE OR REPLACE VIEW ContactListView AS
SELECT
    f.user_id AS user_id,  -- 新增：输出 user_id 列
    u.user_id AS contact_id,
    'friend' AS type,
    u.nickname AS name,
    u.avatar_url,
    (SELECT m.content
     FROM Messages m
     WHERE m.sender_id = u.user_id
       AND m.receiver_id = f.user_id
     ORDER BY m.sent_at DESC
     LIMIT 1) AS last_message,
    (SELECT m.sent_at
     FROM Messages m
     WHERE m.sender_id = u.user_id
       AND m.receiver_id = f.user_id
     ORDER BY m.sent_at DESC
     LIMIT 1) AS last_message_time
FROM Users u
         JOIN Friends f ON u.user_id = f.friend_id
WHERE f.status = 1

UNION

SELECT
    gm.user_id AS user_id,  -- 新增：输出 user_id 列
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
         JOIN Group_Members gm ON g.group_id = gm.group_id;