use smartdelta__pcd;
#select * from tbl_ex_sqm;
select * from tbl_ex_fileinfo;
#select * from tbl_viz_seqdiagram;


#select * from tbl_viz_states;
#select * from tbl_viz_heatmaps;
select * from tbl_viz_simheatmaps;

select * from tbl_ex_folderinfo;
select * from tbl_ex_fileinfo;
select * from tbl_viz_heatmaps;
select * from tbl_viz_seqdiagram;


SELECT folderid as fid, foldername, folderlocation FROM tbl_ex_folderinfo;

SELECT filename, filelocation FROM tbl_ex_fileinfo fi, (SELECT folderid FROM tbl_ex_folderinfo fo WHERE foldername = "elevator") fo WHERE fi.folderid = fo.folderid;
SELECT mmd from tbl_viz_seqdiagram s, (SELECT fileid FROM tbl_ex_fileinfo f WHERE filename = "elevator2.log") f WHERE f.fileid = s.fileid;
SELECT data, states FROM tbl_viz_heatmaps h, (SELECT fileid FROM tbl_ex_fileinfo f WHERE filename = "elevator2.log") f WHERE f.fileid = h.fileid;
SELECT data, axisinfo from tbl_viz_simheatmaps s, (SELECT folderid FROM tbl_ex_folderinfo fo WHERE foldername = "elevator") fo WHERE s.folderid = fo.folderid;

SELECT fi.fileid, filename as FileName, createddate as CreatedDate, modifieddate as ModifiedDate, simfilecount as SimilarityCount, filesize 
FROM tbl_ex_fileinfo fi, (SELECT folderid FROM tbl_ex_folderinfo fo WHERE foldername = "elevator_demo") fo,  tbl_viz_qualitymetrics qm WHERE fi.folderid = fo.folderid and qm.fileid = fi.fileid;



