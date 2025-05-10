-- MySQL dump 10.13  Distrib 9.2.0, for macos14.7 (arm64)
--
-- Host: 127.0.0.1    Database: kaguchat
-- ------------------------------------------------------
-- Server version	9.2.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Current Database: `kaguchat`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `kaguchat` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;

USE `kaguchat`;

--
-- Temporary view structure for view `activefriends`
--

DROP TABLE IF EXISTS `activefriends`;
/*!50001 DROP VIEW IF EXISTS `activefriends`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `activefriends` AS SELECT 
 1 AS `user_id`,
 1 AS `friend_id`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `chathistoryview`
--

DROP TABLE IF EXISTS `chathistoryview`;
/*!50001 DROP VIEW IF EXISTS `chathistoryview`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `chathistoryview` AS SELECT 
 1 AS `message_id`,
 1 AS `sender_id`,
 1 AS `sender_nickname`,
 1 AS `sender_avatar`,
 1 AS `content`,
 1 AS `chat_type`,
 1 AS `message_type_desc`,
 1 AS `sent_at`,
 1 AS `receiver_name`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `contactlistview`
--

DROP TABLE IF EXISTS `contactlistview`;
/*!50001 DROP VIEW IF EXISTS `contactlistview`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `contactlistview` AS SELECT 
 1 AS `user_id`,
 1 AS `contact_id`,
 1 AS `type`,
 1 AS `name`,
 1 AS `avatar_url`,
 1 AS `last_message`,
 1 AS `last_message_time`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `Friends`
--

DROP TABLE IF EXISTS `Friends`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Friends` (
  `friendship_id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `friend_id` bigint NOT NULL,
  `remark` varchar(50) DEFAULT NULL,
  `status` tinyint DEFAULT '1',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`friendship_id`),
  UNIQUE KEY `uk_user_friend` (`user_id`,`friend_id`),
  KEY `friend_id` (`friend_id`),
  CONSTRAINT `friends_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `Users` (`user_id`) ON DELETE CASCADE,
  CONSTRAINT `friends_ibfk_2` FOREIGN KEY (`friend_id`) REFERENCES `Users` (`user_id`) ON DELETE CASCADE,
  CONSTRAINT `chk_status_value` CHECK ((`status` in (0,1)))
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Friends`
--

LOCK TABLES `Friends` WRITE;
/*!40000 ALTER TABLE `Friends` DISABLE KEYS */;
INSERT INTO `Friends` VALUES (1,1,2,'好友2',1,'2025-04-21 16:26:28'),(2,1,3,'好友3',1,'2025-04-21 16:26:28'),(3,2,1,'好友1',1,'2025-04-21 16:26:28'),(4,2,4,'好友4',1,'2025-04-21 16:26:28'),(5,3,1,'好友1',1,'2025-04-21 16:26:28'),(6,4,2,'好友2',0,'2025-04-21 16:26:28');
/*!40000 ALTER TABLE `Friends` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Group_Members`
--

DROP TABLE IF EXISTS `Group_Members`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Group_Members` (
  `member_id` bigint NOT NULL AUTO_INCREMENT,
  `group_id` bigint NOT NULL,
  `user_id` bigint NOT NULL,
  `role` tinyint DEFAULT '0',
  `join_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`member_id`),
  UNIQUE KEY `uk_group_user` (`group_id`,`user_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `group_members_ibfk_1` FOREIGN KEY (`group_id`) REFERENCES `Groups` (`group_id`) ON DELETE CASCADE,
  CONSTRAINT `group_members_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `Users` (`user_id`) ON DELETE CASCADE,
  CONSTRAINT `chk_role_value` CHECK ((`role` in (0,1,2)))
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Group_Members`
--

LOCK TABLES `Group_Members` WRITE;
/*!40000 ALTER TABLE `Group_Members` DISABLE KEYS */;
INSERT INTO `Group_Members` VALUES (1,1,1,2,'2025-04-21 16:26:28'),(2,1,2,1,'2025-04-21 16:26:28'),(3,1,3,0,'2025-04-21 16:26:28'),(4,2,2,2,'2025-04-21 16:26:28'),(5,2,4,0,'2025-04-21 16:26:28'),(6,3,3,2,'2025-04-21 16:26:28'),(7,3,1,0,'2025-04-21 16:26:28');
/*!40000 ALTER TABLE `Group_Members` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Temporary view structure for view `groupmessagestatsview`
--

DROP TABLE IF EXISTS `groupmessagestatsview`;
/*!50001 DROP VIEW IF EXISTS `groupmessagestatsview`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `groupmessagestatsview` AS SELECT 
 1 AS `group_id`,
 1 AS `group_name`,
 1 AS `message_count`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `Groups`
--

DROP TABLE IF EXISTS `Groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Groups` (
  `group_id` bigint NOT NULL AUTO_INCREMENT,
  `group_name` varchar(100) NOT NULL,
  `owner_id` bigint NOT NULL,
  `group_avatar` varchar(255) DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`group_id`),
  UNIQUE KEY `uk_group_name` (`group_name`),
  KEY `owner_id` (`owner_id`),
  CONSTRAINT `groups_ibfk_1` FOREIGN KEY (`owner_id`) REFERENCES `Users` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Groups`
--

LOCK TABLES `Groups` WRITE;
/*!40000 ALTER TABLE `Groups` DISABLE KEYS */;
INSERT INTO `Groups` VALUES (1,'技术交流群',1,'group1.jpg','2025-04-21 16:26:28'),(2,'学习小组',2,'group2.jpg','2025-04-21 16:26:28'),(3,'闲聊',3,'group3.jpg','2025-04-21 16:26:28');
/*!40000 ALTER TABLE `Groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Message_Attachments`
--

DROP TABLE IF EXISTS `Message_Attachments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Message_Attachments` (
  `attachment_id` bigint NOT NULL AUTO_INCREMENT,
  `message_id` bigint NOT NULL,
  `file_url` varchar(255) NOT NULL,
  `file_type` varchar(50) DEFAULT NULL,
  `uploaded_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`attachment_id`),
  KEY `message_id` (`message_id`),
  CONSTRAINT `message_attachments_ibfk_1` FOREIGN KEY (`message_id`) REFERENCES `Messages` (`message_id`) ON DELETE CASCADE,
  CONSTRAINT `chk_file_type` CHECK ((`file_type` in (_utf8mb4'image',_utf8mb4'file',NULL)))
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Message_Attachments`
--

LOCK TABLES `Message_Attachments` WRITE;
/*!40000 ALTER TABLE `Message_Attachments` DISABLE KEYS */;
INSERT INTO `Message_Attachments` VALUES (1,4,'http://example.com/file1.jpg','image','2025-04-21 16:26:28'),(2,7,'http://example.com/file2.pdf','file','2025-04-21 16:26:28');
/*!40000 ALTER TABLE `Message_Attachments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Messages`
--

DROP TABLE IF EXISTS `Messages`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Messages` (
  `message_id` bigint NOT NULL AUTO_INCREMENT,
  `sender_id` bigint NOT NULL,
  `receiver_id` bigint DEFAULT NULL,
  `group_id` bigint DEFAULT NULL,
  `content` text NOT NULL,
  `message_type` tinyint DEFAULT '0',
  `sent_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`message_id`),
  KEY `sender_id` (`sender_id`),
  KEY `receiver_id` (`receiver_id`),
  KEY `group_id` (`group_id`),
  KEY `idx_sent_at` (`sent_at`),
  CONSTRAINT `messages_ibfk_1` FOREIGN KEY (`sender_id`) REFERENCES `Users` (`user_id`) ON DELETE CASCADE,
  CONSTRAINT `messages_ibfk_2` FOREIGN KEY (`receiver_id`) REFERENCES `Users` (`user_id`) ON DELETE RESTRICT,
  CONSTRAINT `messages_ibfk_3` FOREIGN KEY (`group_id`) REFERENCES `Groups` (`group_id`) ON DELETE RESTRICT,
  CONSTRAINT `chk_message_type` CHECK ((`message_type` in (0,1,2))),
  CONSTRAINT `chk_receiver_or_group` CHECK (((`receiver_id` is not null) or (`group_id` is not null)))
) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Messages`
--

LOCK TABLES `Messages` WRITE;
/*!40000 ALTER TABLE `Messages` DISABLE KEYS */;
INSERT INTO `Messages` VALUES (1,1,2,NULL,'你好，在吗？',0,'2025-04-21 16:26:28'),(2,2,1,NULL,'buzai，有什么事吗？',0,'2025-04-21 16:26:28'),(3,1,3,NULL,'周末一起吃饭吗？',0,'2025-04-21 16:26:28'),(4,1,NULL,1,'大家好，欢迎加入技术交流群',1,'2025-04-21 16:26:28'),(5,2,NULL,1,'谢谢群主',1,'2025-04-21 16:26:28'),(6,3,NULL,1,'新人报到',1,'2025-04-21 16:26:28'),(7,3,NULL,3,'今天天气真huai',2,'2025-04-21 16:26:28'),(9,2,1,NULL,'你好',0,'2025-05-03 03:07:23'),(10,1,2,NULL,'你好',0,'2025-05-03 03:08:37'),(11,2,1,NULL,'你好',0,'2025-05-04 01:09:26'),(12,1,2,NULL,'我是user1',0,'2025-05-04 01:09:35'),(13,2,1,NULL,'我是user2',0,'2025-05-04 01:09:44'),(14,1,2,NULL,'再见',0,'2025-05-04 01:09:51'),(15,2,1,NULL,'再见',0,'2025-05-04 01:10:01'),(16,2,1,NULL,'额',0,'2025-05-07 14:27:42'),(17,1,2,NULL,'nihao',0,'2025-05-07 14:27:46'),(18,2,1,NULL,'niko',0,'2025-05-07 14:28:06'),(19,1,2,NULL,'nima',0,'2025-05-07 14:28:15');
/*!40000 ALTER TABLE `Messages` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Temporary view structure for view `useractivityinfo`
--

DROP TABLE IF EXISTS `useractivityinfo`;
/*!50001 DROP VIEW IF EXISTS `useractivityinfo`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `useractivityinfo` AS SELECT 
 1 AS `user_id`,
 1 AS `username`,
 1 AS `created_at`,
 1 AS `days_since_join`,
 1 AS `join_years`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `userfriendscount`
--

DROP TABLE IF EXISTS `userfriendscount`;
/*!50001 DROP VIEW IF EXISTS `userfriendscount`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `userfriendscount` AS SELECT 
 1 AS `user_id`,
 1 AS `username`,
 1 AS `friend_count`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `Users`
--

DROP TABLE IF EXISTS `Users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Users` (
  `user_id` bigint NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `nickname` varchar(50) DEFAULT NULL,
  `phone` varchar(20) NOT NULL,
  `password` varchar(255) NOT NULL,
  `avatar_url` varchar(255) DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `uk_phone` (`phone`),
  CONSTRAINT `chk_phone_format` CHECK (regexp_like(`phone`,_utf8mb4'^[0-9]{11}$'))
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Users`
--

LOCK TABLES `Users` WRITE;
/*!40000 ALTER TABLE `Users` DISABLE KEYS */;
INSERT INTO `Users` VALUES (1,'user1','用户10086','13800000001','password1','avatar1.jpg','2025-04-21 16:26:28'),(2,'user2','用户2','13800000002','password2','avatar2.jpg','2025-04-21 16:26:28'),(3,'user3','用户3','13800000003','password3','avatar3.jpg','2025-04-21 16:26:28'),(4,'user4','用户4','13800000004','password4','avatar4.jpg','2025-04-21 16:26:28'),(8,'kagu','kagu','18636530081','w','','2025-04-30 14:45:28'),(9,'Slight','YourF4u1t','15801373697','password2',NULL,'2025-05-07 14:28:53'),(10,'user5','1','12345678901','pass123',NULL,'2025-05-08 17:52:26');
/*!40000 ALTER TABLE `Users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Current Database: `kaguchat`
--

USE `kaguchat`;

--
-- Final view structure for view `activefriends`
--

/*!50001 DROP VIEW IF EXISTS `activefriends`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `activefriends` AS select `friends`.`user_id` AS `user_id`,`friends`.`friend_id` AS `friend_id` from `friends` where (`friends`.`status` = 1) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `chathistoryview`
--

/*!50001 DROP VIEW IF EXISTS `chathistoryview`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `chathistoryview` AS select `m`.`message_id` AS `message_id`,`m`.`sender_id` AS `sender_id`,`u`.`nickname` AS `sender_nickname`,`u`.`avatar_url` AS `sender_avatar`,`m`.`content` AS `content`,(case when (`m`.`receiver_id` is not null) then 'Private' when (`m`.`group_id` is not null) then 'Group' else 'Unknown' end) AS `chat_type`,(case `m`.`message_type` when 0 then 'Text' when 1 then 'Image' when 2 then 'File' else 'Unknown' end) AS `message_type_desc`,`m`.`sent_at` AS `sent_at`,(case when (`m`.`receiver_id` is not null) then (select `users`.`nickname` from `users` where (`users`.`user_id` = `m`.`receiver_id`)) when (`m`.`group_id` is not null) then (select `groups`.`group_name` from `groups` where (`groups`.`group_id` = `m`.`group_id`)) else 'Unknown' end) AS `receiver_name` from (`messages` `m` join `users` `u` on((`m`.`sender_id` = `u`.`user_id`))) where (`m`.`sender_id` = 1) order by `m`.`sent_at` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `contactlistview`
--

/*!50001 DROP VIEW IF EXISTS `contactlistview`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `contactlistview` AS select `f`.`user_id` AS `user_id`,`u`.`user_id` AS `contact_id`,'friend' AS `type`,`u`.`nickname` AS `name`,`u`.`avatar_url` AS `avatar_url`,(select `m`.`content` from `messages` `m` where ((`m`.`sender_id` = `u`.`user_id`) and (`m`.`receiver_id` = `f`.`user_id`)) order by `m`.`sent_at` desc limit 1) AS `last_message`,(select `m`.`sent_at` from `messages` `m` where ((`m`.`sender_id` = `u`.`user_id`) and (`m`.`receiver_id` = `f`.`user_id`)) order by `m`.`sent_at` desc limit 1) AS `last_message_time` from (`users` `u` join `friends` `f` on((`u`.`user_id` = `f`.`friend_id`))) where (`f`.`status` = 1) union select `gm`.`user_id` AS `user_id`,`g`.`group_id` AS `contact_id`,'group' AS `type`,`g`.`group_name` AS `name`,`g`.`group_avatar` AS `avatar_url`,(select `m`.`content` from `messages` `m` where (`m`.`group_id` = `g`.`group_id`) order by `m`.`sent_at` desc limit 1) AS `last_message`,(select `m`.`sent_at` from `messages` `m` where (`m`.`group_id` = `g`.`group_id`) order by `m`.`sent_at` desc limit 1) AS `last_message_time` from (`groups` `g` join `group_members` `gm` on((`g`.`group_id` = `gm`.`group_id`))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `groupmessagestatsview`
--

/*!50001 DROP VIEW IF EXISTS `groupmessagestatsview`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `groupmessagestatsview` AS select `g`.`group_id` AS `group_id`,`g`.`group_name` AS `group_name`,count(`m`.`message_id`) AS `message_count` from ((`groups` `g` join `group_members` `gm` on(((`g`.`group_id` = `gm`.`group_id`) and (`gm`.`user_id` = 1) and (`gm`.`role` in (1,2))))) left join `messages` `m` on(((`g`.`group_id` = `m`.`group_id`) and (`m`.`sender_id` = 1)))) group by `g`.`group_id`,`g`.`group_name` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `useractivityinfo`
--

/*!50001 DROP VIEW IF EXISTS `useractivityinfo`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `useractivityinfo` AS select `users`.`user_id` AS `user_id`,`users`.`username` AS `username`,`users`.`created_at` AS `created_at`,(to_days(now()) - to_days(`users`.`created_at`)) AS `days_since_join`,concat('已注册 ',floor(((to_days(now()) - to_days(`users`.`created_at`)) / 365)),' 年') AS `join_years` from `users` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `userfriendscount`
--

/*!50001 DROP VIEW IF EXISTS `userfriendscount`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `userfriendscount` AS select `u`.`user_id` AS `user_id`,`u`.`username` AS `username`,count(`f`.`friendship_id`) AS `friend_count` from (`users` `u` join `friends` `f` on(((`u`.`user_id` = `f`.`user_id`) and (`f`.`status` = 1)))) group by `u`.`user_id`,`u`.`username` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-05-10 17:06:48
