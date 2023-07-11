/*
Created Date: 06.07.2023
Updated Date: 07.07.2023
Author: Fraunhofer 
Purpose: Creates a backend for populating architecture visualization dashboard data. alter
NOTES:
-- The defaule Project Control Database (PCD) is SmartDelta__PCD. Please change according to requirement
*/

/*CREATE tbl_ex_folderinfo
	Updated Date: 06.07.2023
	Purpose: Creates a schema that contains all tables that will be used by the dashboard
*/
CREATE SCHEMA `smartdelta__pcd`;

use smartdelta__pcd;

/*
Create tbl_ex_folderinfo
	Updated Date: 06.07.2023
	Purpose: This table contains all folder related info. 
			 The folderid identifier should be used for linking multiple tables when folder is required.
*/
CREATE TABLE `tbl_ex_folderinfo` (
  `Folderid` int(11) NOT NULL AUTO_INCREMENT,
  `FolderName` varchar(200) DEFAULT NULL,
  `FolderLocation` varchar(4000) DEFAULT NULL,
  PRIMARY KEY (`Folderid`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

/*
Create tbl_ex_fileinfo
	Updated Date: 06.07.2023
	Purpose: Contains all related information regarding a file and its metadata.
			 Fileid should be used to join tables when this info is required
*/
CREATE TABLE `tbl_ex_fileinfo` (
  `fileid` int(11) NOT NULL AUTO_INCREMENT,
  `filename` varchar(400) NOT NULL,
  `filelocation` varchar(4000) NOT NULL,
  `folderid` int(11) DEFAULT NULL,
  `simfilecount` int(11) DEFAULT NULL,
  `createddate` date DEFAULT NULL,
  `modifieddate` date DEFAULT NULL,
  PRIMARY KEY (`fileid`),
  KEY `folderid_idx` (`folderid`),
  CONSTRAINT `folderid` FOREIGN KEY (`folderid`) REFERENCES `tbl_ex_folderinfo` (`Folderid`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

/*
Create tbl_viz_states
	Updated Date: 21.06.2023
	Purpose: Contains state info for a statemachine.
	NOTE:(LEGACY TABLE) 
		 THIS IS NOT CURRENTLY IN USE; STATE INFO IS STORED IN THE tbl_ex_Fileinfo ITSELF. NO DATA IS POPULATED BY APP
*/
CREATE TABLE `tbl_viz_states` (
  `states` longtext,
  `fileid` int(11) DEFAULT NULL,
  KEY `fileid_idx` (`fileid`),
  CONSTRAINT `fileid` FOREIGN KEY (`fileid`) REFERENCES `tbl_ex_fileinfo` (`fileid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

/*
Create tbl_viz_simheatmaps
	Updated Date: 06.07.2023
	Purpose: Contains all related information required to visualize similarity heatmap, this inclides dataframes and axis information.
*/
CREATE TABLE `tbl_viz_simheatmaps` (
  `folderid` int(11) DEFAULT NULL,
  `data` longtext,
  `axisinfo` longtext,
  KEY `folderid_idx` (`folderid`),
  CONSTRAINT `_folderid` FOREIGN KEY (`folderid`) REFERENCES `tbl_ex_folderinfo` (`Folderid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

/*
Create tbl_viz_seqdiagram
	Updated Date: 06.07.2023
	Purpose: Contains all related information required to visualize a sequence diagrams, this includes the mermaid statements and the svg files.
*/
CREATE TABLE `tbl_viz_seqdiagram` (
  `fileid` int(11) DEFAULT NULL,
  `mmd` longtext,
  `svgimg` blob,
  KEY `fileid` (`fileid`),
  CONSTRAINT `tbl_viz_seqdiagram_ibfk_1` FOREIGN KEY (`fileid`) REFERENCES `tbl_ex_fileinfo` (`fileid`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


/*
Create tbl_viz_qualitymetrics
	Updated Date: 06.07.2023
	Purpose: Contains all related information related to software quality metrics.
*/
CREATE TABLE `tbl_viz_qualitymetrics` (
  `fileid` int(11) DEFAULT NULL,
  `changerate` int(11) DEFAULT NULL,
  `filesize` decimal(10,2) DEFAULT NULL,
  KEY `fileid` (`fileid`),
  CONSTRAINT `tbl_viz_qualitymetrics_ibfk_1` FOREIGN KEY (`fileid`) REFERENCES `tbl_ex_fileinfo` (`fileid`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

/*
Create tbl_viz_heatmaps
	Updated Date: 06.07.2023
	Purpose: Contains all related information required to plot a heatmap from a log file.
*/
CREATE TABLE `tbl_viz_heatmaps` (
  `fileid` int(11) DEFAULT NULL,
  `data` longtext,
  `states` longtext,
  KEY `fileid` (`fileid`),
  CONSTRAINT `tbl_viz_heatmaps_ibfk_1` FOREIGN KEY (`fileid`) REFERENCES `tbl_ex_fileinfo` (`fileid`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

