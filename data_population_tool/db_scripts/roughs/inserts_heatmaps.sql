use smartdelta_pcd;
select * from tbl_heatmaps;
select * from tbl_allstates;
#SELECT t2.states, fileid, filename, JSON_EXTRACT(`data`, '$.z') AS z_value FROM smartdelta_pcd.tbl_heatmaps t, smartdelta_pcd.tbl_allstates t2 where fileid =1
#SELECT fileid, filename, 
#    JSON_EXTRACT(`data`, '$.z') AS z_value  
#FROM tbl_heatmaps where fileid = 1;
#INSERT INTO tbl_allstates (states) VALUES ("{\"states\": [\"calculator.Initial\", \"calculator.on\", \"calculator.on.Initial\",\"calculator.on.operand1\", \"calculator.on.opEntered\",\"calculator.on.operand2\", \"calculator.on.result\", \"calculator.Final\"]}")

#INSERT INTO tbl_heatmaps (filename, data) VALUES ("calculator_log_2.txt", "{ \"z\" : [[0, 1, 1, 1, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 1, 1], [0, 0, 0, 1, 0, 1, 0, 0], [0, 0, 0, 0, 1, 0, 0, 0], [0, 0, 0, 0, 0, 1, 0, 0], [0, 0, 0, 0, 0, 0, 0, 1], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0]]}")