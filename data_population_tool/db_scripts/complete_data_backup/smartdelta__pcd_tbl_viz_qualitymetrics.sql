-- MySQL dump 10.13  Distrib 8.0.18, for Win64 (x86_64)
--
-- Host: localhost    Database: smartdelta__pcd
-- ------------------------------------------------------
-- Server version	8.0.18

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
-- Table structure for table `tbl_viz_qualitymetrics`
--

DROP TABLE IF EXISTS `tbl_viz_qualitymetrics`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tbl_viz_qualitymetrics` (
  `fileid` int(11) DEFAULT NULL,
  `changerate` int(11) DEFAULT NULL,
  `filesize` decimal(10,2) DEFAULT NULL,
  KEY `fileid` (`fileid`),
  CONSTRAINT `tbl_viz_qualitymetrics_ibfk_1` FOREIGN KEY (`fileid`) REFERENCES `tbl_ex_fileinfo` (`fileid`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbl_viz_qualitymetrics`
--

LOCK TABLES `tbl_viz_qualitymetrics` WRITE;
/*!40000 ALTER TABLE `tbl_viz_qualitymetrics` DISABLE KEYS */;
INSERT INTO `tbl_viz_qualitymetrics` VALUES (1,NULL,1.17),(2,NULL,1.09),(3,NULL,0.44),(4,NULL,1.17),(5,NULL,0.62),(6,NULL,0.62),(7,NULL,0.69),(8,NULL,0.69),(9,NULL,0.27),(10,NULL,0.07),(11,NULL,0.27),(12,NULL,0.14),(13,NULL,0.22),(14,NULL,0.18),(15,NULL,0.13),(16,NULL,0.22),(17,NULL,0.27),(18,NULL,0.27),(19,NULL,0.35),(20,NULL,0.17),(21,NULL,0.98),(22,NULL,0.69),(23,NULL,1.02),(24,NULL,0.24),(25,NULL,0.83),(26,NULL,0.96),(27,NULL,0.89),(28,NULL,0.79),(29,NULL,1.17),(30,NULL,0.81),(31,NULL,1.08),(32,NULL,1.04),(33,NULL,0.96),(34,NULL,1.07),(35,NULL,1.03),(36,NULL,0.97),(37,NULL,0.49),(38,NULL,1.11),(39,NULL,0.97),(40,NULL,1.09),(41,NULL,0.40),(42,NULL,1.15),(43,NULL,1.14),(44,NULL,0.03),(45,NULL,0.03),(46,NULL,0.07),(47,NULL,0.21),(48,NULL,0.92),(49,NULL,0.10),(50,NULL,0.24),(51,NULL,0.44),(52,NULL,0.12),(53,NULL,0.28),(54,NULL,0.15),(55,NULL,0.21),(56,NULL,1.15),(57,NULL,1.09),(58,NULL,0.42),(59,NULL,0.31),(60,NULL,0.10),(61,NULL,0.21),(62,NULL,1.17),(63,NULL,0.12),(64,NULL,0.24),(65,NULL,0.19),(66,NULL,0.24),(67,NULL,0.35),(68,NULL,0.25),(69,NULL,0.62),(70,NULL,0.62),(71,NULL,0.69),(72,NULL,0.69);
/*!40000 ALTER TABLE `tbl_viz_qualitymetrics` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2023-07-07  2:45:42
