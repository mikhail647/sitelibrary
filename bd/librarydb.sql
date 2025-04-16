-- MySQL dump 10.13  Distrib 8.0.41, for Win64 (x86_64)
--
-- Host: localhost    Database: library_db
-- ------------------------------------------------------
-- Server version	8.0.41

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `book_author_relations`
--

DROP TABLE IF EXISTS `book_author_relations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `book_author_relations` (
  `book_id` int NOT NULL,
  `author_id` int NOT NULL,
  PRIMARY KEY (`book_id`,`author_id`),
  KEY `author_id` (`author_id`),
  CONSTRAINT `book_author_relations_ibfk_1` FOREIGN KEY (`book_id`) REFERENCES `book_catalog` (`book_id`),
  CONSTRAINT `book_author_relations_ibfk_2` FOREIGN KEY (`author_id`) REFERENCES `book_authors` (`author_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `book_author_relations`
--

LOCK TABLES `book_author_relations` WRITE;
/*!40000 ALTER TABLE `book_author_relations` DISABLE KEYS */;
INSERT INTO `book_author_relations` VALUES (1,1),(2,1),(3,1),(4,1),(5,1),(6,1),(7,1),(8,1),(9,1),(10,1),(11,1),(12,1),(13,1),(14,1),(15,1),(16,1),(17,1),(18,1),(19,1),(20,1),(1,2),(2,2),(3,2),(4,2),(5,2),(6,2),(7,2),(8,2),(9,2),(10,2),(11,2),(12,2),(13,2),(14,2),(15,2),(16,2),(17,2),(18,2),(19,2),(20,2),(1,3),(2,3),(3,3),(4,3),(5,3),(6,3),(7,3),(8,3),(9,3),(10,3),(11,3),(12,3),(13,3),(14,3),(15,3),(16,3),(17,3),(18,3),(19,3),(20,3),(1,4),(2,4),(3,4),(4,4),(5,4),(6,4),(7,4),(8,4),(9,4),(10,4),(11,4),(12,4),(13,4),(14,4),(15,4),(16,4),(17,4),(18,4),(19,4),(20,4),(1,5),(2,5),(3,5),(4,5),(5,5),(6,5),(7,5),(8,5),(9,5),(10,5),(11,5),(12,5),(13,5),(14,5),(15,5),(16,5),(17,5),(18,5),(19,5),(20,5);
/*!40000 ALTER TABLE `book_author_relations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `book_authors`
--

DROP TABLE IF EXISTS `book_authors`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `book_authors` (
  `author_id` int NOT NULL AUTO_INCREMENT,
  `first_name` varchar(50) NOT NULL,
  `last_name` varchar(50) NOT NULL,
  `middle_name` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`author_id`)
) ENGINE=InnoDB AUTO_INCREMENT=32 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `book_authors`
--

LOCK TABLES `book_authors` WRITE;
/*!40000 ALTER TABLE `book_authors` DISABLE KEYS */;
INSERT INTO `book_authors` VALUES (1,'Имя528','Фамилия417','Отчество502'),(2,'Имя261','Фамилия797','Отчество203'),(3,'Имя625','Фамилия517','Отчество710'),(4,'Имя998','Фамилия862','Отчество315'),(5,'Имя992','Фамилия14','Отчество93'),(6,'Имя426','Фамилия850','Отчество975'),(7,'Имя322','Фамилия689','Отчество477'),(8,'Имя317','Фамилия158','Отчество837'),(9,'Имя714','Фамилия56','Отчество141'),(10,'Имя537','Фамилия263','Отчество705'),(11,'Имя738','Фамилия573','Отчество654'),(12,'Имя551','Фамилия794','Отчество319'),(13,'Имя211','Фамилия98','Отчество857'),(14,'Имя994','Фамилия400','Отчество18'),(15,'Имя892','Фамилия403','Отчество343'),(16,'Имя503','Фамилия490','Отчество938'),(17,'Имя224','Фамилия305','Отчество853'),(18,'Имя349','Фамилия189','Отчество897'),(19,'Имя918','Фамилия902','Отчество755'),(20,'Имя70','Фамилия84','Отчество213');
/*!40000 ALTER TABLE `book_authors` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `book_catalog`
--

DROP TABLE IF EXISTS `book_catalog`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `book_catalog` (
  `book_id` int NOT NULL AUTO_INCREMENT,
  `book_title` varchar(200) NOT NULL,
  `isbn` varchar(13) DEFAULT NULL,
  `publication_year` int DEFAULT NULL,
  `publisher_name` varchar(100) DEFAULT NULL,
  `acquisition_date` date NOT NULL,
  `book_status` enum('available','lost','damaged') NOT NULL DEFAULT 'available',
  PRIMARY KEY (`book_id`),
  UNIQUE KEY `isbn` (`isbn`)
) ENGINE=InnoDB AUTO_INCREMENT=32 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `book_catalog`
--

LOCK TABLES `book_catalog` WRITE;
/*!40000 ALTER TABLE `book_catalog` DISABLE KEYS */;
INSERT INTO `book_catalog` VALUES (1,'Книга 932','978620216017',1985,'Издательство \"Мир\"','2024-11-16','lost'),(2,'Книга 798','978999694462',2000,'Издательство \"Наука\"','2025-01-04','available'),(3,'Книга 544','978923757378',2019,'Издательство \"Наука\"','2024-06-06','available'),(4,'Книга 114','978387235494',1999,'Издательство \"Академия\"','2025-01-06','available'),(5,'Книга 508','978977492712',1988,'Издательство \"Академия\"','2024-12-20','available'),(6,'Книга 504','978874249969',2012,'Издательство \"Мир\"','2024-07-10','available'),(7,'Книга 533','978398291644',1989,'Издательство \"Мир\"','2024-08-29','available'),(8,'Книга 121','978230718171',2009,'Издательство \"Просвещение\"','2024-05-07','available'),(9,'Книга 465','978783080016',1995,'Издательство \"Просвещение\"','2024-08-09','available'),(10,'Книга 7','978232413453',1976,'Издательство \"Академия\"','2024-09-10','available'),(11,'Книга 743','97830614641',2016,'Издательство \"Высшая школа\"','2024-06-14','available'),(12,'Книга 302','978851280277',1987,'Издательство \"Наука\"','2024-05-03','available'),(13,'Книга 634','978906739667',2001,'Издательство \"Высшая школа\"','2025-01-03','available'),(14,'Книга 332','978586782843',2016,'Издательство \"Академия\"','2024-06-10','available'),(15,'Книга 365','978710879048',1992,'Издательство \"Наука\"','2024-11-11','available'),(16,'Книга 638','978473924666',1992,'Издательство \"Академия\"','2024-05-20','available'),(17,'Книга 794','978295277291',1974,'Издательство \"Высшая школа\"','2024-08-23','available'),(18,'Книга 106','978338781263',1988,'Издательство \"Академия\"','2025-02-24','available'),(19,'Книга 970','978648922677',1986,'Издательство \"Мир\"','2024-08-31','available'),(20,'Книга 542','97891944867',2011,'Издательство \"Академия\"','2024-04-28','available');
/*!40000 ALTER TABLE `book_catalog` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `book_copies`
--

DROP TABLE IF EXISTS `book_copies`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `book_copies` (
  `copy_id` int NOT NULL AUTO_INCREMENT,
  `book_id` int NOT NULL,
  `location_id` int NOT NULL,
  `inventory_number` varchar(50) NOT NULL,
  `copy_status` enum('available','issued','lost','damaged') NOT NULL DEFAULT 'available',
  PRIMARY KEY (`copy_id`),
  UNIQUE KEY `inventory_number` (`inventory_number`),
  KEY `book_id` (`book_id`),
  KEY `location_id` (`location_id`),
  CONSTRAINT `book_copies_ibfk_1` FOREIGN KEY (`book_id`) REFERENCES `book_catalog` (`book_id`),
  CONSTRAINT `book_copies_ibfk_2` FOREIGN KEY (`location_id`) REFERENCES `library_locations` (`location_id`)
) ENGINE=InnoDB AUTO_INCREMENT=128 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `book_copies`
--

LOCK TABLES `book_copies` WRITE;
/*!40000 ALTER TABLE `book_copies` DISABLE KEYS */;
INSERT INTO `book_copies` VALUES (1,2,1,'INV814456','available'),(2,5,1,'INV710005','available'),(3,3,1,'INV159999','available'),(4,20,1,'INV649945','available'),(5,13,1,'INV908960','available'),(6,6,1,'INV420739','available'),(7,12,1,'INV813402','available'),(8,9,1,'INV667999','available'),(9,15,1,'INV371369','available'),(10,19,1,'INV44024','available'),(11,1,1,'INV494148','available'),(12,14,1,'INV992598','available'),(13,16,1,'INV412037','available'),(14,7,1,'INV895331','available'),(15,4,1,'INV302953','available'),(16,18,1,'INV698133','available'),(17,11,1,'INV537962','available'),(18,17,1,'INV938079','available'),(19,10,1,'INV981843','available'),(20,8,1,'INV212307','available'),(21,2,2,'INV197253','available'),(22,5,2,'INV837043','available'),(23,3,2,'INV128552','available'),(24,20,2,'INV909100','available'),(25,13,2,'INV115939','available'),(26,6,2,'INV20954','available'),(27,12,2,'INV354674','available'),(28,9,2,'INV550221','available'),(29,15,2,'INV262135','issued'),(30,19,2,'INV28584','available'),(31,1,2,'INV183878','available'),(32,14,2,'INV236428','available'),(33,16,2,'INV837230','available'),(34,7,2,'INV779523','available'),(35,4,2,'INV275870','available'),(36,18,2,'INV225822','available'),(37,11,2,'INV807797','available'),(38,17,2,'INV315756','issued'),(39,10,2,'INV729193','available'),(40,8,2,'INV12869','available'),(41,2,3,'INV681774','available'),(42,5,3,'INV837886','available'),(43,3,3,'INV783869','available'),(44,20,3,'INV352548','available'),(45,13,3,'INV643589','issued'),(46,6,3,'INV55268','available'),(47,12,3,'INV257792','available'),(48,9,3,'INV400642','available'),(49,15,3,'INV292077','available'),(50,19,3,'INV943697','available'),(51,1,3,'INV301558','available'),(52,14,3,'INV236327','available'),(53,16,3,'INV776201','issued'),(54,7,3,'INV620880','available'),(55,4,3,'INV810910','available'),(56,18,3,'INV819386','available'),(57,11,3,'INV270139','issued'),(58,17,3,'INV758170','available'),(59,10,3,'INV973986','available'),(60,8,3,'INV682202','available'),(61,2,4,'INV195965','available'),(62,5,4,'INV583530','available'),(63,3,4,'INV323390','issued'),(64,20,4,'INV892649','available'),(65,13,4,'INV49823','available'),(66,6,4,'INV912804','available'),(67,12,4,'INV894864','available'),(68,9,4,'INV787192','available'),(69,15,4,'INV902874','available'),(70,19,4,'INV69887','available'),(71,1,4,'INV201984','available'),(72,14,4,'INV208712','available'),(73,16,4,'INV147676','available'),(74,7,4,'INV927443','available'),(75,4,4,'INV292330','available'),(76,18,4,'INV207295','available'),(77,11,4,'INV307631','available'),(78,17,4,'INV979351','available'),(79,10,4,'INV838995','issued'),(80,8,4,'INV126757','available'),(81,2,5,'INV857422','available'),(82,5,5,'INV150207','available'),(83,3,5,'INV137148','available'),(84,20,5,'INV253951','available'),(85,13,5,'INV590735','available'),(86,6,5,'INV938414','available'),(87,12,5,'INV513253','available'),(88,9,5,'INV306094','available'),(89,15,5,'INV196504','available'),(90,19,5,'INV978746','available'),(91,1,5,'INV827646','available'),(92,14,5,'INV916564','available'),(93,16,5,'INV965902','available'),(94,7,5,'INV103065','available'),(95,4,5,'INV265127','issued'),(96,18,5,'INV109827','available'),(97,11,5,'INV700585','available'),(98,17,5,'INV322680','available'),(99,10,5,'INV825648','available'),(100,8,5,'INV783209','available');
/*!40000 ALTER TABLE `book_copies` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `book_loans`
--

DROP TABLE IF EXISTS `book_loans`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `book_loans` (
  `loan_id` int NOT NULL AUTO_INCREMENT,
  `reader_id` int NOT NULL,
  `copy_id` int NOT NULL,
  `location_id` int NOT NULL,
  `loan_date` date NOT NULL,
  `due_date` date NOT NULL,
  `return_date` date DEFAULT NULL,
  `loan_status` enum('active','returned','overdue','lost') NOT NULL DEFAULT 'active',
  PRIMARY KEY (`loan_id`),
  KEY `reader_id` (`reader_id`),
  KEY `copy_id` (`copy_id`),
  KEY `location_id` (`location_id`),
  CONSTRAINT `book_loans_ibfk_1` FOREIGN KEY (`reader_id`) REFERENCES `library_readers` (`reader_id`),
  CONSTRAINT `book_loans_ibfk_2` FOREIGN KEY (`copy_id`) REFERENCES `book_copies` (`copy_id`),
  CONSTRAINT `book_loans_ibfk_3` FOREIGN KEY (`location_id`) REFERENCES `library_locations` (`location_id`)
) ENGINE=InnoDB AUTO_INCREMENT=128 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `book_loans`
--

LOCK TABLES `book_loans` WRITE;
/*!40000 ALTER TABLE `book_loans` DISABLE KEYS */;
INSERT INTO `book_loans` VALUES (1,95,64,4,'2025-04-06','2025-05-21','2025-04-27','returned'),(2,44,52,3,'2025-03-20','2025-04-19','2025-04-07','returned'),(3,14,86,5,'2025-03-23','2025-05-22','2025-04-17','returned'),(4,80,39,2,'2025-04-06','2025-05-06','2025-04-15','returned'),(5,63,49,3,'2025-03-06','2025-04-20',NULL,'active'),(6,70,20,1,'2025-04-09','2025-06-08','2025-04-20','returned'),(7,88,44,3,'2025-03-08','2025-04-07','2025-04-12','returned'),(8,103,14,1,'2025-02-22','2025-04-08',NULL,'overdue'),(9,6,44,3,'2025-04-01','2025-05-31','2025-04-03','returned'),(10,88,71,4,'2025-03-26','2025-04-25','2025-04-07','returned'),(11,61,3,1,'2025-03-19','2025-05-03',NULL,'active'),(12,103,64,4,'2025-02-25','2025-04-11','2025-04-24','returned'),(13,64,99,5,'2025-02-14','2025-03-16','2025-03-25','returned'),(14,28,33,2,'2025-02-26','2025-03-28','2025-03-23','returned'),(15,104,78,4,'2025-03-02','2025-04-01','2025-03-09','returned'),(16,48,77,4,'2025-03-08','2025-04-07',NULL,'overdue'),(17,12,87,5,'2025-03-08','2025-04-07',NULL,'overdue'),(18,5,80,4,'2025-03-09','2025-04-23','2025-03-30','returned'),(19,44,82,5,'2025-03-18','2025-04-17',NULL,'active'),(20,20,16,1,'2025-03-28','2025-04-27','2025-04-22','returned'),(21,63,4,1,'2025-03-21','2025-05-05','2025-05-18','returned'),(22,52,78,4,'2025-03-21','2025-04-20','2025-03-22','returned'),(23,30,94,5,'2025-03-11','2025-05-10','2025-05-16','returned'),(24,6,71,4,'2025-02-14','2025-04-15','2025-04-21','returned'),(25,63,32,2,'2025-03-30','2025-05-14',NULL,'active'),(26,7,84,5,'2025-03-06','2025-04-20',NULL,'active'),(27,14,28,2,'2025-04-09','2025-06-08','2025-04-17','returned'),(28,70,98,5,'2025-03-24','2025-05-23','2025-03-31','returned'),(29,101,77,4,'2025-03-09','2025-04-23','2025-04-04','returned'),(30,36,65,4,'2025-02-19','2025-03-21','2025-02-27','returned'),(31,61,22,2,'2025-03-01','2025-04-15','2025-04-03','returned'),(32,15,32,2,'2025-04-02','2025-05-17','2025-05-13','returned'),(33,29,4,1,'2025-03-27','2025-05-11','2025-05-11','returned'),(34,40,22,2,'2025-03-29','2025-04-28',NULL,'active'),(35,52,22,2,'2025-03-21','2025-04-20','2025-03-29','returned'),(36,100,31,2,'2025-02-10','2025-03-12',NULL,'overdue'),(37,87,88,5,'2025-02-21','2025-04-07',NULL,'overdue'),(38,56,40,2,'2025-03-28','2025-04-27','2025-04-15','returned'),(39,56,81,5,'2025-03-26','2025-04-25','2025-04-03','returned'),(40,7,85,5,'2025-02-22','2025-04-08',NULL,'overdue'),(41,86,28,2,'2025-02-21','2025-04-22',NULL,'active'),(42,12,26,2,'2025-03-14','2025-04-13','2025-04-02','returned'),(43,104,35,2,'2025-02-11','2025-03-13',NULL,'overdue'),(44,28,44,3,'2025-03-15','2025-04-14','2025-03-23','returned'),(45,53,47,3,'2025-02-26','2025-04-12','2025-04-06','returned'),(46,16,21,2,'2025-04-06','2025-05-06','2025-04-19','returned'),(47,86,51,3,'2025-02-16','2025-04-17','2025-04-28','returned'),(48,4,31,2,'2025-03-28','2025-04-27','2025-04-24','returned'),(49,76,8,1,'2025-03-20','2025-04-19','2025-04-06','returned'),(50,12,1,1,'2025-03-28','2025-04-27','2025-04-15','returned'),(51,95,89,5,'2025-03-28','2025-05-12','2025-04-26','returned'),(52,30,2,1,'2025-02-26','2025-04-27','2025-04-02','returned'),(53,54,60,3,'2025-03-16','2025-05-15','2025-05-24','returned'),(54,92,84,5,'2025-04-06','2025-05-06','2025-04-08','returned'),(55,79,23,2,'2025-02-16','2025-04-02','2025-02-22','returned'),(56,70,87,5,'2025-02-12','2025-04-13','2025-03-22','returned'),(57,6,74,4,'2025-03-08','2025-05-07','2025-05-10','returned'),(58,96,30,2,'2025-04-06','2025-05-06','2025-04-09','returned'),(59,46,2,1,'2025-02-11','2025-04-12',NULL,'active'),(60,68,11,1,'2025-04-03','2025-05-03','2025-04-06','returned'),(61,62,7,1,'2025-03-18','2025-05-17',NULL,'active'),(62,7,100,5,'2025-03-06','2025-04-20',NULL,'active'),(63,71,43,3,'2025-03-25','2025-05-09','2025-04-22','returned'),(64,70,65,4,'2025-03-06','2025-05-05',NULL,'active'),(65,93,88,5,'2025-03-03','2025-04-17','2025-04-13','returned'),(66,96,8,1,'2025-02-19','2025-03-21','2025-03-26','returned'),(67,31,22,2,'2025-03-20','2025-05-04',NULL,'active'),(68,30,8,1,'2025-03-18','2025-05-17',NULL,'active'),(69,72,49,3,'2025-02-27','2025-03-29','2025-02-27','returned'),(70,69,39,2,'2025-03-12','2025-04-26','2025-03-20','returned'),(71,63,17,1,'2025-03-23','2025-05-07','2025-03-25','returned'),(72,54,25,2,'2025-03-14','2025-05-13','2025-04-15','returned'),(73,44,1,1,'2025-03-12','2025-04-11','2025-03-29','returned'),(74,24,84,5,'2025-03-11','2025-04-10','2025-04-09','returned'),(75,72,92,5,'2025-03-11','2025-04-10','2025-04-02','returned'),(76,53,90,5,'2025-03-30','2025-05-14',NULL,'active'),(77,79,34,2,'2025-03-25','2025-05-09','2025-05-01','returned'),(78,5,37,2,'2025-04-03','2025-05-18','2025-04-21','returned'),(79,92,86,5,'2025-02-19','2025-03-21','2025-03-30','returned'),(80,31,85,5,'2025-04-04','2025-05-19','2025-05-16','returned'),(81,86,49,3,'2025-02-27','2025-04-28','2025-03-10','returned'),(82,103,97,5,'2025-03-04','2025-04-18','2025-03-15','returned'),(83,94,2,1,'2025-02-16','2025-04-17','2025-04-22','returned'),(84,20,80,4,'2025-03-19','2025-04-18',NULL,'active'),(85,64,84,5,'2025-03-16','2025-04-15',NULL,'active'),(86,14,72,4,'2025-04-04','2025-06-03','2025-06-08','returned'),(87,94,59,3,'2025-02-11','2025-04-12',NULL,'active'),(88,16,96,5,'2025-04-02','2025-05-02','2025-04-30','returned'),(89,64,47,3,'2025-03-13','2025-04-12','2025-04-16','returned'),(90,92,92,5,'2025-03-11','2025-04-10','2025-04-02','returned'),(91,95,32,2,'2025-02-27','2025-04-13','2025-04-24','returned'),(92,60,90,5,'2025-03-04','2025-04-03','2025-03-15','returned'),(93,16,83,5,'2025-04-08','2025-05-08','2025-04-22','returned'),(94,80,27,2,'2025-03-12','2025-04-11','2025-03-18','returned'),(95,15,40,2,'2025-04-04','2025-05-19','2025-05-09','returned'),(96,36,23,2,'2025-02-16','2025-03-18','2025-03-31','returned'),(97,21,78,4,'2025-03-06','2025-04-20',NULL,'active'),(98,16,58,3,'2025-02-20','2025-03-22','2025-03-21','returned'),(99,84,44,3,'2025-02-23','2025-03-25',NULL,'overdue'),(100,5,97,5,'2025-03-14','2025-04-28','2025-04-15','returned');
/*!40000 ALTER TABLE `book_loans` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `interlibrary_requests`
--

DROP TABLE IF EXISTS `interlibrary_requests`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `interlibrary_requests` (
  `request_id` int NOT NULL AUTO_INCREMENT,
  `reader_id` int NOT NULL,
  `book_id` int NOT NULL,
  `request_date` date NOT NULL,
  `request_status` enum('pending','approved','received','returned') NOT NULL DEFAULT 'pending',
  PRIMARY KEY (`request_id`),
  KEY `reader_id` (`reader_id`),
  KEY `book_id` (`book_id`),
  CONSTRAINT `interlibrary_requests_ibfk_1` FOREIGN KEY (`reader_id`) REFERENCES `library_readers` (`reader_id`),
  CONSTRAINT `interlibrary_requests_ibfk_2` FOREIGN KEY (`book_id`) REFERENCES `book_catalog` (`book_id`)
) ENGINE=InnoDB AUTO_INCREMENT=128 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `interlibrary_requests`
--

LOCK TABLES `interlibrary_requests` WRITE;
/*!40000 ALTER TABLE `interlibrary_requests` DISABLE KEYS */;
INSERT INTO `interlibrary_requests` VALUES (1,8,2,'2025-04-03','pending'),(2,8,5,'2025-03-24','pending'),(3,8,3,'2025-03-19','approved'),(4,8,20,'2025-03-29','pending'),(5,8,13,'2025-04-05','received'),(6,8,6,'2025-03-26','received'),(7,8,12,'2025-03-17','returned'),(8,8,9,'2025-04-03','approved'),(9,8,15,'2025-04-05','received'),(10,8,19,'2025-03-17','returned'),(11,8,1,'2025-03-28','approved'),(12,8,14,'2025-04-08','approved'),(13,8,16,'2025-03-14','pending'),(14,8,7,'2025-03-31','pending'),(15,8,4,'2025-03-29','received'),(16,8,18,'2025-04-05','returned'),(17,8,11,'2025-03-19','pending'),(18,8,17,'2025-03-11','returned'),(19,8,10,'2025-04-05','approved'),(20,8,8,'2025-03-29','returned'),(21,16,2,'2025-03-16','received'),(22,16,5,'2025-03-14','approved'),(23,16,3,'2025-03-31','approved'),(24,16,20,'2025-04-08','pending'),(25,16,13,'2025-03-11','returned'),(26,16,6,'2025-04-09','received'),(27,16,12,'2025-03-24','received'),(28,16,9,'2025-04-05','pending'),(29,16,15,'2025-03-15','pending'),(30,16,19,'2025-03-13','approved'),(31,16,1,'2025-03-16','pending'),(32,16,14,'2025-03-12','received'),(33,16,16,'2025-04-07','received'),(34,16,7,'2025-03-16','approved'),(35,16,4,'2025-03-12','returned'),(36,16,18,'2025-03-28','received'),(37,16,11,'2025-03-25','returned'),(38,16,17,'2025-03-18','pending'),(39,16,10,'2025-03-13','returned'),(40,16,8,'2025-03-23','approved'),(41,24,2,'2025-03-19','received'),(42,24,5,'2025-03-27','pending'),(43,24,3,'2025-04-06','approved'),(44,24,20,'2025-03-29','returned'),(45,24,13,'2025-04-01','returned'),(46,24,6,'2025-03-14','pending'),(47,24,12,'2025-03-28','approved'),(48,24,9,'2025-04-06','pending'),(49,24,15,'2025-04-06','approved'),(50,24,19,'2025-04-01','approved'),(51,24,1,'2025-04-06','approved'),(52,24,14,'2025-03-19','approved'),(53,24,16,'2025-03-31','returned'),(54,24,7,'2025-03-14','pending'),(55,24,4,'2025-03-18','received'),(56,24,18,'2025-03-26','returned'),(57,24,11,'2025-03-28','returned'),(58,24,17,'2025-03-17','approved'),(59,24,10,'2025-03-14','pending'),(60,24,8,'2025-04-07','returned'),(61,32,2,'2025-03-25','received'),(62,32,5,'2025-03-13','approved'),(63,32,3,'2025-03-18','approved'),(64,32,20,'2025-04-07','received'),(65,32,13,'2025-03-14','approved'),(66,32,6,'2025-03-16','received'),(67,32,12,'2025-03-27','approved'),(68,32,9,'2025-04-05','pending'),(69,32,15,'2025-03-23','approved'),(70,32,19,'2025-03-21','approved'),(71,32,1,'2025-04-07','pending'),(72,32,14,'2025-03-23','approved'),(73,32,16,'2025-03-25','approved'),(74,32,7,'2025-03-17','pending'),(75,32,4,'2025-04-02','returned'),(76,32,18,'2025-03-23','approved'),(77,32,11,'2025-03-22','approved'),(78,32,17,'2025-03-14','approved'),(79,32,10,'2025-04-03','returned'),(80,32,8,'2025-03-15','received'),(81,40,2,'2025-03-29','pending'),(82,40,5,'2025-03-20','returned'),(83,40,3,'2025-04-01','returned'),(84,40,20,'2025-03-22','approved'),(85,40,13,'2025-04-07','pending'),(86,40,6,'2025-03-13','returned'),(87,40,12,'2025-03-23','approved'),(88,40,9,'2025-03-14','approved'),(89,40,15,'2025-03-30','received'),(90,40,19,'2025-04-08','approved'),(91,40,1,'2025-03-23','returned'),(92,40,14,'2025-03-13','received'),(93,40,16,'2025-03-12','approved'),(94,40,7,'2025-03-23','approved'),(95,40,4,'2025-03-19','pending'),(96,40,18,'2025-04-07','approved'),(97,40,11,'2025-03-25','approved'),(98,40,17,'2025-03-20','pending'),(99,40,10,'2025-03-29','received'),(100,40,8,'2025-04-01','approved');
/*!40000 ALTER TABLE `interlibrary_requests` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `library_fines`
--

DROP TABLE IF EXISTS `library_fines`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `library_fines` (
  `fine_id` int NOT NULL AUTO_INCREMENT,
  `reader_id` int NOT NULL,
  `loan_id` int DEFAULT NULL,
  `request_id` int DEFAULT NULL,
  `fine_amount` decimal(10,2) NOT NULL,
  `fine_date` date NOT NULL,
  `fine_status` enum('pending','paid','cancelled') NOT NULL DEFAULT 'pending',
  `fine_reason` enum('overdue','lost','damaged') NOT NULL,
  PRIMARY KEY (`fine_id`),
  KEY `reader_id` (`reader_id`),
  KEY `loan_id` (`loan_id`),
  KEY `request_id` (`request_id`),
  CONSTRAINT `library_fines_ibfk_1` FOREIGN KEY (`reader_id`) REFERENCES `library_readers` (`reader_id`),
  CONSTRAINT `library_fines_ibfk_2` FOREIGN KEY (`loan_id`) REFERENCES `book_loans` (`loan_id`),
  CONSTRAINT `library_fines_ibfk_3` FOREIGN KEY (`request_id`) REFERENCES `interlibrary_requests` (`request_id`)
) ENGINE=InnoDB AUTO_INCREMENT=128 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `library_fines`
--

LOCK TABLES `library_fines` WRITE;
/*!40000 ALTER TABLE `library_fines` DISABLE KEYS */;
INSERT INTO `library_fines` VALUES (1,16,93,28,739.79,'2025-03-20','pending','overdue'),(2,16,98,34,746.62,'2025-03-19','pending','overdue'),(3,32,NULL,64,319.54,'2025-03-24','cancelled','lost'),(4,16,98,33,789.27,'2025-03-13','pending','overdue'),(5,71,63,NULL,916.60,'2025-03-25','cancelled','damaged'),(6,87,37,NULL,531.37,'2025-03-23','paid','overdue'),(7,16,46,39,879.22,'2025-03-31','pending','overdue'),(8,8,NULL,17,253.87,'2025-04-04','pending','overdue'),(9,16,93,22,96.30,'2025-03-29','paid','damaged'),(10,80,94,NULL,34.50,'2025-04-08','pending','lost'),(11,16,93,25,538.70,'2025-03-23','pending','lost'),(12,60,92,NULL,546.76,'2025-03-22','paid','overdue'),(13,40,34,89,376.92,'2025-03-19','paid','overdue'),(14,16,88,31,520.09,'2025-03-27','paid','damaged'),(15,16,93,33,533.00,'2025-03-26','cancelled','lost'),(16,40,34,93,28.62,'2025-03-12','paid','lost'),(17,16,46,26,753.29,'2025-03-24','paid','overdue'),(18,8,NULL,8,778.77,'2025-03-20','pending','lost'),(19,16,88,30,915.46,'2025-03-30','pending','overdue'),(20,40,34,92,582.80,'2025-03-20','cancelled','lost'),(21,16,88,37,79.12,'2025-04-05','paid','lost'),(22,16,88,40,283.54,'2025-04-04','pending','damaged'),(23,16,98,28,84.10,'2025-04-04','cancelled','damaged'),(24,7,26,NULL,690.75,'2025-04-03','pending','lost'),(25,16,88,35,974.54,'2025-03-22','pending','overdue'),(26,16,93,21,816.95,'2025-03-16','cancelled','overdue'),(27,63,71,NULL,287.23,'2025-04-04','cancelled','lost'),(28,32,NULL,68,901.19,'2025-04-02','paid','lost'),(29,44,2,NULL,163.83,'2025-03-24','pending','lost'),(30,16,46,22,845.98,'2025-03-12','pending','overdue'),(31,7,40,NULL,182.38,'2025-03-22','paid','overdue'),(32,40,34,83,73.65,'2025-04-08','pending','damaged'),(33,72,69,NULL,371.72,'2025-03-25','paid','lost'),(34,32,NULL,65,19.57,'2025-03-19','paid','damaged'),(35,8,NULL,1,415.85,'2025-03-19','pending','overdue'),(36,40,34,81,330.94,'2025-04-02','pending','damaged'),(37,86,81,NULL,783.74,'2025-03-25','pending','lost'),(38,30,68,NULL,898.70,'2025-04-08','paid','lost'),(39,40,34,90,759.26,'2025-03-30','paid','overdue'),(40,32,NULL,78,458.03,'2025-03-16','paid','damaged'),(41,5,100,NULL,698.80,'2025-04-09','cancelled','lost'),(42,40,34,95,889.70,'2025-03-12','pending','lost'),(43,32,NULL,75,56.74,'2025-03-17','cancelled','overdue'),(44,32,NULL,67,830.32,'2025-03-22','paid','overdue'),(45,32,NULL,70,864.38,'2025-03-17','paid','overdue'),(46,16,46,32,28.19,'2025-03-23','cancelled','lost'),(47,5,18,NULL,912.24,'2025-03-11','pending','overdue'),(48,70,28,NULL,300.95,'2025-03-12','cancelled','overdue'),(49,16,98,27,587.31,'2025-03-31','cancelled','overdue'),(50,16,93,40,440.45,'2025-03-25','pending','damaged'),(51,16,46,28,692.69,'2025-03-17','cancelled','lost'),(52,70,64,NULL,546.20,'2025-04-09','paid','lost'),(53,16,93,24,559.91,'2025-04-07','cancelled','overdue'),(54,79,77,NULL,932.84,'2025-03-13','cancelled','lost'),(55,72,75,NULL,776.75,'2025-04-05','paid','lost'),(56,31,67,NULL,963.70,'2025-04-08','paid','damaged'),(57,24,74,45,809.87,'2025-04-01','pending','overdue'),(58,32,NULL,80,885.35,'2025-03-20','cancelled','lost'),(59,20,84,NULL,80.33,'2025-03-21','cancelled','damaged'),(60,101,29,NULL,393.73,'2025-04-04','paid','damaged'),(61,32,NULL,61,44.03,'2025-03-28','cancelled','overdue'),(62,8,NULL,6,824.93,'2025-03-31','pending','lost'),(63,24,74,44,335.75,'2025-03-15','pending','damaged'),(64,16,46,29,833.16,'2025-03-30','pending','overdue'),(65,68,60,NULL,137.77,'2025-03-15','cancelled','damaged'),(66,8,NULL,15,544.51,'2025-03-14','cancelled','overdue'),(67,32,NULL,76,259.14,'2025-03-28','paid','lost'),(68,61,31,NULL,484.16,'2025-03-24','pending','damaged'),(69,84,99,NULL,385.33,'2025-04-08','pending','lost'),(70,16,88,23,473.52,'2025-03-26','cancelled','overdue'),(71,64,89,NULL,853.95,'2025-03-29','pending','lost'),(72,6,57,NULL,146.51,'2025-03-16','cancelled','overdue'),(73,16,98,39,607.41,'2025-04-06','cancelled','lost'),(74,16,93,35,795.50,'2025-04-08','cancelled','lost'),(75,32,NULL,74,528.52,'2025-03-19','cancelled','lost'),(76,8,NULL,12,49.22,'2025-03-31','paid','damaged'),(77,40,34,85,521.51,'2025-03-21','cancelled','damaged'),(78,40,34,82,992.88,'2025-04-09','pending','lost'),(79,8,NULL,3,194.35,'2025-04-09','paid','lost'),(80,21,97,NULL,729.40,'2025-03-20','pending','overdue'),(81,24,74,56,277.65,'2025-03-28','pending','lost'),(82,64,13,NULL,471.98,'2025-03-29','paid','lost'),(83,16,46,35,574.94,'2025-03-14','cancelled','damaged'),(84,24,74,58,917.05,'2025-03-23','pending','damaged'),(85,32,NULL,66,217.35,'2025-04-08','paid','overdue'),(86,32,NULL,73,154.38,'2025-03-18','pending','overdue'),(87,76,49,NULL,349.06,'2025-03-19','paid','lost'),(88,104,15,NULL,791.61,'2025-03-13','pending','overdue'),(89,92,90,NULL,985.39,'2025-03-15','pending','damaged'),(90,24,74,46,968.85,'2025-03-19','cancelled','lost'),(91,16,88,34,227.65,'2025-03-11','pending','overdue'),(92,56,38,NULL,937.14,'2025-03-25','cancelled','overdue'),(93,24,74,41,602.18,'2025-03-15','paid','lost'),(94,61,11,NULL,189.25,'2025-03-18','pending','overdue'),(95,16,98,29,332.80,'2025-03-27','pending','damaged'),(96,30,23,NULL,137.73,'2025-03-26','cancelled','overdue'),(97,100,36,NULL,488.95,'2025-04-03','paid','lost'),(98,14,3,NULL,766.43,'2025-03-24','paid','damaged'),(99,63,21,NULL,23.85,'2025-03-16','pending','damaged'),(100,28,44,NULL,591.64,'2025-03-20','paid','damaged');
/*!40000 ALTER TABLE `library_fines` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `library_locations`
--

DROP TABLE IF EXISTS `library_locations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `library_locations` (
  `location_id` int NOT NULL AUTO_INCREMENT,
  `location_name` varchar(100) NOT NULL,
  `location_type` enum('loan','reading_room') NOT NULL,
  `address` varchar(200) NOT NULL,
  PRIMARY KEY (`location_id`)
) ENGINE=InnoDB AUTO_INCREMENT=32 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `library_locations`
--

LOCK TABLES `library_locations` WRITE;
/*!40000 ALTER TABLE `library_locations` DISABLE KEYS */;
INSERT INTO `library_locations` VALUES (1,'Абонемент №1','loan','Адрес 937'),(2,'Специализированный зал №1','loan','Адрес 879'),(3,'Читальный зал №6','loan','Адрес 939'),(4,'Читальный зал №7','reading_room','Адрес 818'),(5,'Читальный зал №3','loan','Адрес 726'),(6,'Межбиблиотечный абонемент №4','reading_room','Адрес 934'),(7,'Читальный зал №3','loan','Адрес 622'),(8,'Межбиблиотечный абонемент №10','loan','Адрес 848'),(9,'Читальный зал №9','loan','Адрес 618'),(10,'Межбиблиотечный абонемент №1','reading_room','Адрес 502'),(11,'Межбиблиотечный абонемент №1','loan','Адрес 228'),(12,'Фонд редких книг №10','loan','Адрес 742'),(13,'Читальный зал №2','loan','Адрес 86'),(14,'Абонемент №9','loan','Адрес 531'),(15,'Фонд редких книг №4','reading_room','Адрес 413'),(16,'Читальный зал №5','loan','Адрес 705'),(17,'Фонд редких книг №5','loan','Адрес 337'),(18,'Межбиблиотечный абонемент №8','reading_room','Адрес 825'),(19,'Читальный зал №7','reading_room','Адрес 785'),(20,'Читальный зал №2','reading_room','Адрес 680');
/*!40000 ALTER TABLE `library_locations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `library_readers`
--

DROP TABLE IF EXISTS `library_readers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `library_readers` (
  `reader_id` int NOT NULL AUTO_INCREMENT,
  `reader_type_id` int NOT NULL,
  `first_name` varchar(50) NOT NULL,
  `last_name` varchar(50) NOT NULL,
  `middle_name` varchar(50) DEFAULT NULL,
  `library_card_number` varchar(20) NOT NULL,
  `registration_date` date NOT NULL,
  `reader_status` enum('active','suspended','expelled') NOT NULL DEFAULT 'active',
  `suspension_end_date` date DEFAULT NULL,
  PRIMARY KEY (`reader_id`),
  UNIQUE KEY `library_card_number` (`library_card_number`),
  KEY `reader_type_id` (`reader_type_id`),
  CONSTRAINT `library_readers_ibfk_1` FOREIGN KEY (`reader_type_id`) REFERENCES `reader_types` (`type_id`)
) ENGINE=InnoDB AUTO_INCREMENT=128 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `library_readers`
--

LOCK TABLES `library_readers` WRITE;
/*!40000 ALTER TABLE `library_readers` DISABLE KEYS */;
INSERT INTO `library_readers` VALUES (1,8,'Стажер558','Фамилия899','Отчество820','CARD403862','2024-09-18','active',NULL),(2,7,'Абитуриент376','Фамилия212','Отчество933','CARD30068','2024-12-03','active',NULL),(3,6,'ФПК252','Фамилия525','Отчество870','CARD774839','2025-01-04','suspended',NULL),(4,5,'Сотрудник841','Фамилия721','Отчество81','CARD241570','2024-04-22','active',NULL),(5,4,'Аспирант694','Фамилия678','Отчество308','CARD508582','2024-08-27','active',NULL),(6,3,'Преподаватель14','Фамилия261','Отчество262','CARD529889','2024-05-30','active',NULL),(7,2,'Заочник820','Фамилия121','Отчество146','CARD367700','2024-11-15','active',NULL),(8,1,'Студент674','Фамилия559','Отчество772','CARD182670','2024-09-03','active',NULL),(9,8,'Стажер684','Фамилия224','Отчество68','CARD669805','2025-02-16','active','2025-06-09'),(10,7,'Абитуриент439','Фамилия172','Отчество543','CARD197294','2024-11-30','active',NULL),(11,6,'ФПК935','Фамилия965','Отчество18','CARD199276','2024-05-02','active',NULL),(12,5,'Сотрудник101','Фамилия467','Отчество34','CARD768060','2024-07-14','active',NULL),(13,4,'Аспирант349','Фамилия651','Отчество208','CARD86910','2024-06-18','active',NULL),(14,3,'Преподаватель164','Фамилия309','Отчество51','CARD330882','2024-10-09','active','2025-07-24'),(15,2,'Заочник886','Фамилия664','Отчество661','CARD316387','2024-09-04','active',NULL),(16,1,'Студент790','Фамилия817','Отчество718','CARD137352','2024-09-27','active',NULL),(17,8,'Стажер473','Фамилия435','Отчество756','CARD476873','2025-02-26','active',NULL),(18,7,'Абитуриент459','Фамилия160','Отчество425','CARD644739','2024-04-29','active',NULL),(19,6,'ФПК465','Фамилия803','Отчество618','CARD683228','2024-09-17','active','2025-05-05'),(20,5,'Сотрудник485','Фамилия992','Отчество506','CARD553078','2025-01-09','active',NULL),(21,4,'Аспирант923','Фамилия229','Отчество379','CARD208136','2024-05-15','active',NULL),(22,3,'Преподаватель949','Фамилия583','Отчество68','CARD594201','2024-07-04','active',NULL),(23,2,'Заочник401','Фамилия294','Отчество270','CARD469312','2024-09-27','active',NULL),(24,1,'Студент756','Фамилия654','Отчество6','CARD65786','2024-12-17','active',NULL),(25,8,'Стажер178','Фамилия344','Отчество187','CARD903886','2024-04-25','active',NULL),(26,7,'Абитуриент219','Фамилия637','Отчество529','CARD735097','2025-03-09','active',NULL),(27,6,'ФПК717','Фамилия945','Отчество574','CARD35768','2024-10-25','active',NULL),(28,5,'Сотрудник966','Фамилия341','Отчество806','CARD7140','2024-08-27','active',NULL),(29,4,'Аспирант180','Фамилия474','Отчество832','CARD740449','2025-01-25','active',NULL),(30,3,'Преподаватель473','Фамилия247','Отчество818','CARD350936','2024-12-22','active',NULL),(31,2,'Заочник187','Фамилия34','Отчество611','CARD951083','2024-05-08','active','2025-09-06'),(32,1,'Студент107','Фамилия32','Отчество843','CARD118481','2025-03-18','suspended',NULL),(33,8,'Стажер62','Фамилия558','Отчество605','CARD349803','2024-05-04','active',NULL),(34,7,'Абитуриент593','Фамилия99','Отчество714','CARD276897','2025-01-12','active',NULL),(35,6,'ФПК526','Фамилия252','Отчество682','CARD655104','2025-01-16','active',NULL),(36,5,'Сотрудник415','Фамилия513','Отчество320','CARD64691','2024-11-29','active',NULL),(37,4,'Аспирант992','Фамилия71','Отчество378','CARD676759','2025-01-08','active',NULL),(38,3,'Преподаватель39','Фамилия184','Отчество800','CARD450808','2024-06-02','suspended',NULL),(39,2,'Заочник215','Фамилия113','Отчество920','CARD263240','2024-09-19','suspended',NULL),(40,1,'Студент210','Фамилия365','Отчество194','CARD876365','2024-06-22','active',NULL),(41,8,'Стажер62','Фамилия18','Отчество903','CARD463597','2024-08-31','active',NULL),(42,7,'Абитуриент16','Фамилия916','Отчество535','CARD927579','2025-03-29','active',NULL),(43,6,'ФПК718','Фамилия293','Отчество311','CARD674934','2024-10-30','active',NULL),(44,5,'Сотрудник379','Фамилия144','Отчество581','CARD473413','2024-08-25','active',NULL),(45,4,'Аспирант991','Фамилия106','Отчество557','CARD467658','2024-08-09','suspended',NULL),(46,3,'Преподаватель450','Фамилия310','Отчество198','CARD61881','2024-07-23','active',NULL),(47,2,'Заочник752','Фамилия418','Отчество833','CARD913609','2025-03-16','active',NULL),(48,1,'Студент82','Фамилия91','Отчество211','CARD781589','2024-12-31','active',NULL),(49,8,'Стажер432','Фамилия259','Отчество0','CARD225161','2025-02-24','suspended',NULL),(50,7,'Абитуриент825','Фамилия139','Отчество223','CARD698988','2024-06-13','active',NULL),(51,6,'ФПК121','Фамилия693','Отчество104','CARD442166','2024-05-17','active',NULL),(52,5,'Сотрудник48','Фамилия926','Отчество488','CARD663138','2024-06-03','active',NULL),(53,4,'Аспирант923','Фамилия401','Отчество237','CARD979788','2025-01-31','active',NULL),(54,3,'Преподаватель186','Фамилия620','Отчество542','CARD849781','2024-08-25','active',NULL),(55,2,'Заочник41','Фамилия368','Отчество720','CARD498016','2024-12-11','active',NULL),(56,1,'Студент208','Фамилия863','Отчество692','CARD870518','2024-12-30','active','2025-08-17'),(57,8,'Стажер599','Фамилия830','Отчество355','CARD283648','2024-12-02','suspended',NULL),(58,7,'Абитуриент774','Фамилия364','Отчество500','CARD410852','2024-09-20','active',NULL),(59,6,'ФПК261','Фамилия405','Отчество242','CARD995038','2025-01-09','active',NULL),(60,5,'Сотрудник996','Фамилия314','Отчество585','CARD981343','2025-02-13','active',NULL),(61,4,'Аспирант593','Фамилия151','Отчество976','CARD428648','2025-01-22','active',NULL),(62,3,'Преподаватель947','Фамилия966','Отчество988','CARD45444','2025-01-04','active','2025-08-25'),(63,2,'Заочник678','Фамилия89','Отчество409','CARD781496','2024-08-05','active',NULL),(64,1,'Студент836','Фамилия597','Отчество476','CARD591207','2024-09-29','active',NULL),(65,8,'Стажер12','Фамилия908','Отчество504','CARD797973','2024-10-18','suspended',NULL),(66,7,'Абитуриент519','Фамилия113','Отчество9','CARD707523','2024-10-06','active',NULL),(67,6,'ФПК631','Фамилия418','Отчество200','CARD747574','2025-02-19','active',NULL),(68,5,'Сотрудник535','Фамилия372','Отчество256','CARD165971','2025-03-19','active',NULL),(69,4,'Аспирант719','Фамилия122','Отчество456','CARD913573','2025-01-27','active',NULL),(70,3,'Преподаватель593','Фамилия956','Отчество2','CARD141993','2024-07-27','active',NULL),(71,2,'Заочник363','Фамилия845','Отчество136','CARD144764','2024-12-16','active',NULL),(72,1,'Студент359','Фамилия529','Отчество571','CARD265576','2024-08-28','active',NULL),(73,8,'Стажер857','Фамилия673','Отчество797','CARD967839','2024-10-29','active',NULL),(74,7,'Абитуриент463','Фамилия454','Отчество882','CARD47377','2024-09-06','active',NULL),(75,6,'ФПК949','Фамилия919','Отчество749','CARD991089','2024-07-26','active',NULL),(76,5,'Сотрудник639','Фамилия212','Отчество142','CARD77230','2024-04-25','active',NULL),(77,4,'Аспирант926','Фамилия870','Отчество573','CARD255807','2024-09-18','active',NULL),(78,3,'Преподаватель162','Фамилия471','Отчество867','CARD924940','2025-04-02','active',NULL),(79,2,'Заочник33','Фамилия343','Отчество618','CARD62539','2024-10-25','active',NULL),(80,1,'Студент251','Фамилия934','Отчество919','CARD793576','2025-01-23','active',NULL),(81,8,'Стажер480','Фамилия320','Отчество159','CARD836107','2024-07-27','active',NULL),(82,7,'Абитуриент503','Фамилия814','Отчество561','CARD363242','2025-02-20','active',NULL),(83,6,'ФПК554','Фамилия412','Отчество400','CARD765792','2024-08-24','active',NULL),(84,5,'Сотрудник6','Фамилия120','Отчество584','CARD559431','2025-03-24','active',NULL),(85,4,'Аспирант321','Фамилия832','Отчество199','CARD498028','2024-05-19','suspended',NULL),(86,3,'Преподаватель928','Фамилия141','Отчество921','CARD181106','2025-02-16','active',NULL),(87,2,'Заочник584','Фамилия667','Отчество584','CARD920529','2024-06-04','active',NULL),(88,1,'Студент848','Фамилия668','Отчество796','CARD979225','2024-10-07','active',NULL),(89,8,'Стажер364','Фамилия546','Отчество637','CARD549636','2024-06-09','active',NULL),(90,7,'Абитуриент22','Фамилия753','Отчество702','CARD251442','2025-02-14','suspended',NULL),(91,6,'ФПК582','Фамилия378','Отчество142','CARD578214','2024-10-22','active',NULL),(92,5,'Сотрудник884','Фамилия840','Отчество550','CARD231007','2024-10-08','active',NULL),(93,4,'Аспирант546','Фамилия922','Отчество974','CARD105698','2024-09-01','active',NULL),(94,3,'Преподаватель440','Фамилия67','Отчество17','CARD886215','2024-11-23','active','2025-06-18'),(95,2,'Заочник899','Фамилия329','Отчество950','CARD762353','2024-04-24','active',NULL),(96,1,'Студент950','Фамилия651','Отчество408','CARD86869','2025-01-23','active',NULL),(97,8,'Стажер104','Фамилия648','Отчество928','CARD699287','2024-07-24','active',NULL),(98,7,'Абитуриент290','Фамилия64','Отчество452','CARD70266','2024-04-12','active',NULL),(99,6,'ФПК638','Фамилия857','Отчество370','CARD280086','2024-12-25','active',NULL),(100,5,'Сотрудник23','Фамилия611','Отчество986','CARD97777','2024-09-28','active',NULL),(101,4,'Аспирант819','Фамилия571','Отчество397','CARD274908','2025-02-02','active',NULL),(102,3,'Преподаватель80','Фамилия806','Отчество791','CARD539620','2024-12-13','suspended',NULL),(103,2,'Заочник10','Фамилия57','Отчество256','CARD111246','2024-06-27','active',NULL),(104,1,'Студент333','Фамилия792','Отчество961','CARD430780','2025-01-01','active',NULL);
/*!40000 ALTER TABLE `library_readers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `reader_registrations`
--

DROP TABLE IF EXISTS `reader_registrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `reader_registrations` (
  `registration_id` int NOT NULL AUTO_INCREMENT,
  `reader_id` int NOT NULL,
  `location_id` int NOT NULL,
  `registration_date` date NOT NULL,
  `registration_expiry_date` date NOT NULL,
  PRIMARY KEY (`registration_id`),
  KEY `reader_id` (`reader_id`),
  KEY `location_id` (`location_id`),
  CONSTRAINT `reader_registrations_ibfk_1` FOREIGN KEY (`reader_id`) REFERENCES `library_readers` (`reader_id`),
  CONSTRAINT `reader_registrations_ibfk_2` FOREIGN KEY (`location_id`) REFERENCES `library_locations` (`location_id`)
) ENGINE=InnoDB AUTO_INCREMENT=128 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `reader_registrations`
--

LOCK TABLES `reader_registrations` WRITE;
/*!40000 ALTER TABLE `reader_registrations` DISABLE KEYS */;
INSERT INTO `reader_registrations` VALUES (1,8,20,'2025-02-24','2026-01-09'),(2,8,19,'2024-11-14','2026-01-04'),(3,8,18,'2024-10-06','2025-07-31'),(4,8,17,'2025-03-29','2025-07-02'),(5,8,16,'2025-03-21','2025-11-07'),(6,8,15,'2024-07-11','2026-04-04'),(7,8,14,'2024-07-28','2025-10-20'),(8,8,13,'2024-09-16','2025-06-28'),(9,8,12,'2024-11-09','2025-09-06'),(10,8,11,'2024-06-16','2026-02-08'),(11,8,10,'2024-07-13','2025-06-19'),(12,8,9,'2024-07-08','2025-06-16'),(13,8,8,'2024-08-08','2026-01-23'),(14,8,7,'2024-04-28','2025-08-20'),(15,8,6,'2024-04-16','2026-01-30'),(16,8,5,'2025-02-26','2025-05-30'),(17,8,4,'2024-11-28','2025-08-28'),(18,8,3,'2024-06-02','2025-05-15'),(19,8,2,'2024-05-03','2025-08-27'),(20,8,1,'2025-02-25','2025-09-16'),(21,16,20,'2024-06-05','2026-03-04'),(22,16,19,'2024-04-16','2025-06-18'),(23,16,18,'2025-03-30','2025-11-01'),(24,16,17,'2024-07-15','2026-04-01'),(25,16,16,'2024-07-29','2025-10-25'),(26,16,15,'2024-08-20','2025-10-25'),(27,16,14,'2024-06-14','2025-09-25'),(28,16,13,'2024-05-30','2026-03-07'),(29,16,12,'2024-04-21','2025-05-20'),(30,16,11,'2024-08-09','2026-04-04'),(31,16,10,'2024-05-01','2026-01-05'),(32,16,9,'2024-05-17','2025-07-09'),(33,16,8,'2024-09-15','2025-05-05'),(34,16,7,'2024-08-08','2025-05-27'),(35,16,6,'2024-08-14','2026-02-19'),(36,16,5,'2024-11-25','2025-07-11'),(37,16,4,'2025-02-09','2025-04-29'),(38,16,3,'2024-06-28','2026-01-06'),(39,16,2,'2024-11-22','2025-12-08'),(40,16,1,'2025-01-29','2026-03-29'),(41,24,20,'2025-01-02','2025-09-10'),(42,24,19,'2024-12-14','2025-08-06'),(43,24,18,'2024-08-07','2025-08-27'),(44,24,17,'2024-05-13','2025-08-27'),(45,24,16,'2025-01-26','2026-02-14'),(46,24,15,'2024-08-11','2026-01-07'),(47,24,14,'2024-07-06','2025-10-29'),(48,24,13,'2024-10-09','2026-02-04'),(49,24,12,'2024-08-20','2025-12-22'),(50,24,11,'2024-08-26','2026-04-02'),(51,24,10,'2025-03-23','2025-07-25'),(52,24,9,'2024-12-09','2026-01-16'),(53,24,8,'2024-05-26','2025-04-23'),(54,24,7,'2024-09-09','2026-01-21'),(55,24,6,'2025-01-27','2025-11-24'),(56,24,5,'2024-09-20','2026-02-19'),(57,24,4,'2024-08-03','2026-01-30'),(58,24,3,'2025-04-06','2025-11-20'),(59,24,2,'2025-03-20','2025-09-11'),(60,24,1,'2024-04-24','2025-10-17'),(61,32,20,'2024-07-12','2025-05-30'),(62,32,19,'2024-10-19','2026-03-17'),(63,32,18,'2024-12-29','2025-11-04'),(64,32,17,'2025-03-27','2025-09-23'),(65,32,16,'2025-01-30','2025-11-04'),(66,32,15,'2024-12-23','2026-01-10'),(67,32,14,'2024-05-15','2025-07-05'),(68,32,13,'2024-10-11','2026-01-08'),(69,32,12,'2024-12-30','2025-05-22'),(70,32,11,'2024-07-02','2025-10-09'),(71,32,10,'2025-01-26','2025-10-07'),(72,32,9,'2024-05-23','2026-03-08'),(73,32,8,'2024-05-08','2026-02-22'),(74,32,7,'2024-08-29','2025-09-14'),(75,32,6,'2024-12-09','2025-08-20'),(76,32,5,'2024-06-10','2025-04-29'),(77,32,4,'2024-06-27','2026-01-08'),(78,32,3,'2024-11-09','2026-01-30'),(79,32,2,'2024-06-13','2025-12-12'),(80,32,1,'2024-05-08','2025-11-05'),(81,40,20,'2025-02-26','2026-02-14'),(82,40,19,'2024-05-09','2025-04-20'),(83,40,18,'2024-11-15','2026-03-05'),(84,40,17,'2024-12-12','2026-03-07'),(85,40,16,'2024-09-10','2025-06-08'),(86,40,15,'2025-03-08','2026-03-22'),(87,40,14,'2024-10-11','2025-11-18'),(88,40,13,'2024-09-10','2025-04-30'),(89,40,12,'2024-09-19','2025-11-12'),(90,40,11,'2024-12-14','2026-01-28'),(91,40,10,'2025-03-11','2026-03-31'),(92,40,9,'2024-08-19','2025-07-17'),(93,40,8,'2024-10-28','2025-09-08'),(94,40,7,'2024-07-11','2025-10-01'),(95,40,6,'2025-02-10','2025-08-19'),(96,40,5,'2024-12-08','2025-11-07'),(97,40,4,'2024-05-13','2026-01-23'),(98,40,3,'2025-01-09','2026-02-13'),(99,40,2,'2024-10-02','2025-04-22'),(100,40,1,'2024-08-23','2025-04-19');
/*!40000 ALTER TABLE `reader_registrations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `reader_types`
--

DROP TABLE IF EXISTS `reader_types`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `reader_types` (
  `type_id` int NOT NULL AUTO_INCREMENT,
  `type_name` varchar(50) NOT NULL,
  `max_books_allowed` int NOT NULL,
  `loan_period_days` int NOT NULL,
  `can_use_reading_room` tinyint(1) NOT NULL DEFAULT '1',
  `can_use_loan` tinyint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`type_id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `reader_types`
--

LOCK TABLES `reader_types` WRITE;
/*!40000 ALTER TABLE `reader_types` DISABLE KEYS */;
INSERT INTO `reader_types` VALUES (1,'Студент очной формы',5,30,1,1),(2,'Студент заочной формы',3,45,1,1),(3,'Преподаватель',10,60,1,1),(4,'Аспирант',8,45,1,1),(5,'Сотрудник университета',5,30,1,1),(6,'Слушатель ФПК',0,0,1,0),(7,'Абитуриент',0,0,1,0),(8,'Стажер',0,0,1,0);
/*!40000 ALTER TABLE `reader_types` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `staff_readers`
--

DROP TABLE IF EXISTS `staff_readers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `staff_readers` (
  `reader_id` int NOT NULL,
  `department_name` varchar(100) NOT NULL,
  `job_position` varchar(100) NOT NULL,
  PRIMARY KEY (`reader_id`),
  CONSTRAINT `staff_readers_ibfk_1` FOREIGN KEY (`reader_id`) REFERENCES `library_readers` (`reader_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `staff_readers`
--

LOCK TABLES `staff_readers` WRITE;
/*!40000 ALTER TABLE `staff_readers` DISABLE KEYS */;
INSERT INTO `staff_readers` VALUES (4,'Учебный отдел','Специалист'),(12,'Бухгалтерия','Старший специалист'),(20,'Бухгалтерия','Заместитель начальника'),(28,'Хозяйственный отдел','Начальник отдела'),(36,'Административный отдел','Старший специалист'),(44,'Учебный отдел','Начальник отдела'),(52,'Отдел кадров','Специалист'),(60,'Хозяйственный отдел','Начальник отдела'),(68,'Учебный отдел','Главный специалист'),(76,'Учебный отдел','Старший специалист'),(84,'Административный отдел','Специалист'),(92,'Отдел кадров','Специалист'),(100,'Учебный отдел','Специалист');
/*!40000 ALTER TABLE `staff_readers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `student_readers`
--

DROP TABLE IF EXISTS `student_readers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `student_readers` (
  `reader_id` int NOT NULL,
  `faculty_name` varchar(100) NOT NULL,
  `group_number` varchar(20) NOT NULL,
  `course_number` int NOT NULL,
  PRIMARY KEY (`reader_id`),
  CONSTRAINT `student_readers_ibfk_1` FOREIGN KEY (`reader_id`) REFERENCES `library_readers` (`reader_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `student_readers`
--

LOCK TABLES `student_readers` WRITE;
/*!40000 ALTER TABLE `student_readers` DISABLE KEYS */;
INSERT INTO `student_readers` VALUES (7,'Факультет информационных технологий','13-17',1),(8,'Факультет информационных технологий','46-17',2),(15,'Факультет гуманитарных наук','88-54',3),(16,'Факультет гуманитарных наук','20-48',4),(23,'Факультет естественных наук','74-95',3),(24,'Факультет экономики и управления','26-43',2),(31,'Факультет инженерных наук','10-09',3),(32,'Факультет гуманитарных наук','21-74',1),(39,'Факультет гуманитарных наук','27-02',4),(40,'Факультет естественных наук','22-50',3),(47,'Факультет гуманитарных наук','56-63',3),(48,'Факультет экономики и управления','30-09',4),(55,'Факультет экономики и управления','56-83',2),(56,'Факультет инженерных наук','39-59',1),(63,'Факультет информационных технологий','12-86',2),(64,'Факультет гуманитарных наук','29-79',3),(71,'Факультет инженерных наук','31-55',4),(72,'Факультет информационных технологий','92-43',2),(79,'Факультет информационных технологий','72-04',1),(80,'Факультет естественных наук','22-78',4),(87,'Факультет естественных наук','82-51',4),(88,'Факультет естественных наук','01-79',4),(95,'Факультет информационных технологий','61-60',1),(96,'Факультет информационных технологий','95-86',3),(103,'Факультет инженерных наук','83-37',3),(104,'Факультет экономики и управления','27-81',4);
/*!40000 ALTER TABLE `student_readers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `teacher_readers`
--

DROP TABLE IF EXISTS `teacher_readers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `teacher_readers` (
  `reader_id` int NOT NULL,
  `department_name` varchar(100) NOT NULL,
  `academic_degree` varchar(50) DEFAULT NULL,
  `academic_title` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`reader_id`),
  CONSTRAINT `teacher_readers_ibfk_1` FOREIGN KEY (`reader_id`) REFERENCES `library_readers` (`reader_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `teacher_readers`
--

LOCK TABLES `teacher_readers` WRITE;
/*!40000 ALTER TABLE `teacher_readers` DISABLE KEYS */;
INSERT INTO `teacher_readers` VALUES (6,'Кафедра физики','Доктор наук',NULL),(14,'Кафедра истории','Доктор наук',NULL),(22,'Кафедра информатики','Кандидат наук',NULL),(30,'Кафедра физики',NULL,NULL),(38,'Кафедра экономики','Кандидат наук','Доцент'),(46,'Кафедра физики','Доктор наук','Профессор'),(54,'Кафедра экономики',NULL,'Профессор'),(62,'Кафедра информатики',NULL,'Профессор'),(70,'Кафедра экономики',NULL,NULL),(78,'Кафедра физики','Доктор наук','Доцент'),(86,'Кафедра физики','Кандидат наук','Профессор'),(94,'Кафедра информатики','Доктор наук','Профессор'),(102,'Кафедра истории',NULL,NULL);
/*!40000 ALTER TABLE `teacher_readers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `temporary_readers`
--

DROP TABLE IF EXISTS `temporary_readers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `temporary_readers` (
  `reader_id` int NOT NULL,
  `reader_type` enum('FPC','applicant','intern') NOT NULL,
  PRIMARY KEY (`reader_id`),
  CONSTRAINT `temporary_readers_ibfk_1` FOREIGN KEY (`reader_id`) REFERENCES `library_readers` (`reader_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `temporary_readers`
--

LOCK TABLES `temporary_readers` WRITE;
/*!40000 ALTER TABLE `temporary_readers` DISABLE KEYS */;
INSERT INTO `temporary_readers` VALUES (1,'FPC'),(2,'intern'),(3,'intern'),(9,'applicant'),(10,'intern'),(11,'FPC'),(17,'intern'),(18,'FPC'),(19,'intern'),(25,'intern'),(26,'intern'),(27,'FPC'),(33,'FPC'),(34,'intern'),(35,'intern'),(41,'FPC'),(42,'applicant'),(43,'applicant'),(49,'intern'),(50,'applicant'),(51,'applicant'),(57,'applicant'),(58,'FPC'),(59,'FPC'),(65,'intern'),(66,'applicant'),(67,'applicant'),(73,'applicant'),(74,'FPC'),(75,'FPC'),(81,'intern'),(82,'applicant'),(83,'applicant'),(89,'intern'),(90,'applicant'),(91,'FPC'),(97,'applicant'),(98,'intern'),(99,'applicant');
/*!40000 ALTER TABLE `temporary_readers` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-04-14 13:01:30
