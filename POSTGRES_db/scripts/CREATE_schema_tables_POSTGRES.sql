CREATE DATABASE smartdelta_pcd;
/*
Create tbl_ex_folderinfo
Updated Date: 06.07.2023
Purpose: This table contains all folder-related info.
The folderid identifier should be used for linking multiple tables when folder is required.
*/


CREATE TABLE tbl_ex_folderinfo (
    folderid SERIAL PRIMARY KEY,
    foldername VARCHAR(200),
    folderlocation VARCHAR(4000)
);

/*
Create tbl_ex_fileinfo
Updated Date: 06.07.2023
Purpose: Contains all related information regarding a file and its metadata.
Fileid should be used to join tables when this info is required.
*/
CREATE TABLE tbl_ex_fileinfo (
    fileid SERIAL PRIMARY KEY,
    filename VARCHAR(400) NOT NULL,
    filelocation VARCHAR(4000) NOT NULL,
    folderid INTEGER REFERENCES tbl_ex_folderinfo (folderid),
    simfilecount INTEGER,
    createddate DATE,
    modifieddate DATE
);

/*
Create tbl_viz_states
Updated Date: 21.06.2023
Purpose: Contains state info for a state machine.
NOTE:(LEGACY TABLE)
THIS IS NOT CURRENTLY IN USE; STATE INFO IS STORED IN tbl_ex_fileinfo ITSELF.
*/
CREATE TABLE tbl_viz_states (
    states TEXT,
    fileid INTEGER REFERENCES tbl_ex_fileinfo (fileid)
);

/*
Create tbl_viz_simheatmaps
Updated Date: 06.07.2023
Purpose: Contains all related information required to visualize similarity heatmap, including dataframes and axis information.
*/
CREATE TABLE tbl_viz_simheatmaps (
    folderid INTEGER REFERENCES tbl_ex_folderinfo (folderid),
    data TEXT,
    axisinfo TEXT
);

/*
Create tbl_viz_seqdiagram
Updated Date: 06.07.2023
Purpose: Contains all related information required to visualize sequence diagrams, including the mermaid statements and SVG files.
*/
CREATE TABLE tbl_viz_seqdiagram (
    fileid INTEGER REFERENCES tbl_ex_fileinfo (fileid) ON DELETE CASCADE ON UPDATE RESTRICT,
    mmd TEXT,
    svgimg BYTEA
);

/*
Create tbl_viz_qualitymetrics
Updated Date: 06.07.2023
Purpose: Contains all related information related to software quality metrics.
*/
CREATE TABLE tbl_viz_qualitymetrics (
    fileid INTEGER REFERENCES tbl_ex_fileinfo (fileid) ON DELETE CASCADE ON UPDATE RESTRICT,
    changerate INTEGER,
    filesize DECIMAL(10, 2)
);

/*
Create tbl_viz_heatmaps
Updated Date: 06.07.2023
Purpose: Contains all related information required to plot a heatmap from a log file.
*/
CREATE TABLE tbl_viz_heatmaps (
    fileid INTEGER REFERENCES tbl_ex_fileinfo (fileid) ON DELETE CASCADE ON UPDATE RESTRICT,
    data TEXT,
    states TEXT
);

/*
Create tbl_ex_similarity_info
Updated Date: 06.11.2024
Purpose: Contains all related information required to show delta view on the dashboard.
*/
CREATE TABLE tbl_ex_similarity_info (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(45),
    svg_data_usm TEXT,
    svg_data_dbsm TEXT,
    createddate TIMESTAMP
);

/*
Create tbl_viz_state_diagram
Updated Date: 06.11.2024
Purpose: Contains all related information required to visualize state diagrams, including the PUML and SVG data.
*/
CREATE TABLE tbl_viz_state_diagram (
    fileid INTEGER REFERENCES tbl_ex_fileinfo (fileid) ON DELETE CASCADE ON UPDATE RESTRICT,
    puml TEXT,
    svg_data BYTEA
);
