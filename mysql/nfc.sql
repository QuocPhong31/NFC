-- MySQL dump 10.13  Distrib 8.0.41, for Win64 (x86_64)
--
-- Host: localhost    Database: nfc
-- ------------------------------------------------------
-- Server version	9.2.0

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
-- Table structure for table `card_certificates`
--

DROP TABLE IF EXISTS `card_certificates`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `card_certificates` (
  `id` int NOT NULL AUTO_INCREMENT,
  `card_id` int NOT NULL,
  `tenChungChi` varchar(255) NOT NULL,
  `donViCap` varchar(255) DEFAULT NULL,
  `moTa` text,
  `url` varchar(1000) DEFAULT NULL,
  `ngayCap` date DEFAULT NULL,
  `sort_order` int DEFAULT '0',
  `is_active` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`id`),
  KEY `card_id` (`card_id`),
  CONSTRAINT `card_certificates_ibfk_1` FOREIGN KEY (`card_id`) REFERENCES `the_nfc` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `card_certificates`
--

LOCK TABLES `card_certificates` WRITE;
/*!40000 ALTER TABLE `card_certificates` DISABLE KEYS */;
/*!40000 ALTER TABLE `card_certificates` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `card_items`
--

DROP TABLE IF EXISTS `card_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `card_items` (
  `id` int NOT NULL AUTO_INCREMENT,
  `card_id` int NOT NULL,
  `category` enum('GENERAL','SOCIAL','MESSAGING','LINK') NOT NULL,
  `platform` varchar(50) DEFAULT NULL,
  `item_type` varchar(50) NOT NULL,
  `display_title` varchar(255) DEFAULT NULL,
  `value` text,
  `sort_order` int DEFAULT '0',
  `is_active` tinyint(1) DEFAULT '1',
  `ngayTao` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `ngayCapNhat` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `fk_card_items` (`card_id`),
  CONSTRAINT `fk_card_items` FOREIGN KEY (`card_id`) REFERENCES `the_nfc` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `card_items`
--

LOCK TABLES `card_items` WRITE;
/*!40000 ALTER TABLE `card_items` DISABLE KEYS */;
/*!40000 ALTER TABLE `card_items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `nguoidungs`
--

DROP TABLE IF EXISTS `nguoidungs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `nguoidungs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `hoTen` varchar(255) DEFAULT NULL,
  `gioiTinh` tinyint DEFAULT NULL,
  `ngaySinh` date DEFAULT NULL,
  `diaChi` varchar(255) DEFAULT NULL,
  `SDT` varchar(20) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `taiKhoan` varchar(100) DEFAULT NULL,
  `matKhau` varchar(255) DEFAULT NULL,
  `role` enum('ADMIN','USER') DEFAULT 'USER',
  `ngayTao` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`),
  UNIQUE KEY `taiKhoan` (`taiKhoan`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `nguoidungs`
--

LOCK TABLES `nguoidungs` WRITE;
/*!40000 ALTER TABLE `nguoidungs` DISABLE KEYS */;
INSERT INTO `nguoidungs` VALUES (1,'Quoc Phong',1,'1990-01-01','HCM','0123456789','admin@example.com','admin','8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92','ADMIN','2026-10-03 03:58:49');
/*!40000 ALTER TABLE `nguoidungs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `the_nfc`
--

DROP TABLE IF EXISTS `the_nfc`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `the_nfc` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `tenThe` varchar(255) NOT NULL,
  `slug` varchar(255) NOT NULL,
  `hoTen` varchar(255) DEFAULT NULL,
  `chucVu` varchar(255) DEFAULT NULL,
  `congTy` varchar(255) DEFAULT NULL,
  `phongBan` varchar(255) DEFAULT NULL,
  `gioiThieu` text,
  `email` varchar(255) DEFAULT NULL,
  `soDienThoai` varchar(50) DEFAULT NULL,
  `urlCongTy` varchar(500) DEFAULT NULL,
  `diaChi` text,
  `maSoThue` varchar(100) DEFAULT NULL,
  `anhBia` varchar(1000) DEFAULT NULL,
  `anhDaiDien` varchar(1000) DEFAULT NULL,
  `logo` varchar(1000) DEFAULT NULL,
  `theme` varchar(50) DEFAULT 'orange',
  `qrUrl` varchar(1000) DEFAULT NULL,
  `trangThai` enum('ACTIVE','HIDDEN') DEFAULT 'ACTIVE',
  `ngayTao` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `ngayCapNhat` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `slug` (`slug`),
  KEY `fk_the_user` (`user_id`),
  CONSTRAINT `fk_the_user` FOREIGN KEY (`user_id`) REFERENCES `nguoidungs` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `the_nfc`
--

LOCK TABLES `the_nfc` WRITE;
/*!40000 ALTER TABLE `the_nfc` DISABLE KEYS */;
/*!40000 ALTER TABLE `the_nfc` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-10-03 11:18:18
