USE smartdelta__pcd;

CREATE TABLE IF NOT EXISTS tbl_ex_fileinfo
( 
	fileid INT AUTO_INCREMENT PRIMARY KEY, 
	filename VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS tbl_ex_sqm
( 
	fileid INT, 
	changerate INT DEFAULT NULL,	
    FOREIGN KEY (fileid) REFERENCES tbl_ex_fileinfo (fileid) 
    ON UPDATE RESTRICT 
    ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS tbl_ex_seqdiagram
( 
	fileid INT, 
	mmd blob DEFAULT NULL,
	svgimg blob DEFAULT NULL,
    FOREIGN KEY (fileid) REFERENCES tbl_ex_fileinfo (fileid) 
    ON UPDATE RESTRICT 
    ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS tbl_dia_heat
(
	fileid INT, 
    z_val blob,
    
    FOREIGN KEY (fileid) REFERENCES tbl_ex_fileinfo (fileid) 
    ON UPDATE RESTRICT 
    ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS tbl_dia_simheat
(
	fileid INT,
    similarity blob,
    
    FOREIGN KEY (fileid) REFERENCES tbl_ex_fileinfo (fileid) 
    ON UPDATE RESTRICT 
    ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS tbl_dia_states
(
    states blob
)
