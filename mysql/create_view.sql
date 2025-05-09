CREATE VIEW ActiveFriends AS
SELECT user_id, friend_id
FROM Friends
WHERE status = 1;


CREATE VIEW UserFriendsCount AS
SELECT u.user_id, u.username, COUNT(f.friendship_id) AS friend_count
FROM Users u
JOIN Friends f ON u.user_id = f.user_id AND f.status = 1
GROUP BY u.user_id, u.username;


CREATE VIEW UserActivityInfo AS
SELECT 
    user_id,
    username,
    created_at,
    DATEDIFF(NOW(), created_at) AS days_since_join,
    CONCAT('已注册 ', FLOOR(DATEDIFF(NOW(), created_at)/365), ' 年') AS join_years
FROM Users;