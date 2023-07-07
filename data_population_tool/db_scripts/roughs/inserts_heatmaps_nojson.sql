use smartdelta_pcd;
select * from tbl_allstates_nojson;
select * from tbl_heatmaps_nojson;
#update tbl_heatmaps_nojson set filename = "calculator_log_3.log" where fileid =2
#insert into tbl_heatmaps_nojson (filename, data) values ("calculator_log_2.log", "[[0, 1, 0, 0, 0, 0, 1, 0], [1, 0, 1, 0, 0, 0, 0, 1], [0, 1, 0, 1, 0, 0, 0, 0], [0, 0, 0, 0, 1, 0, 0, 0], [0, 0, 1,1, 0, 1, 1, 0], [0, 0, 0, 0, 0, 0, 0, 1], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0]]");

#insert into tbl_heatmaps_nojson (filename, data) values ("calculator_log_2.log", "[[0, 1, 1, 1, 0, 0, 1, 1], [1, 0, 1, 0, 0, 0, 1, 1], [0, 1, 0, 1, 0, 0, 0, 0], [0, 0, 1, 1, 1, 1, 1, 0], [0, 1, 1, 1, 0, 1, 1, 0], [0, 1, 0, 1, 0, 0, 0, 1], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0]]");

#insert into tbl_heatmaps_nojson (filename, data) values ("calculator_log_1.log", "[[0, 1, 1, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 1], [0, 0, 0, 1, 0, 0, 0, 0], [0, 0, 0, 0, 1, 0, 0, 0], [0, 0, 0, 0, 0, 1, 0, 0], [0, 0, 0, 0, 0, 0, 0, 1], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0]]")
#insert into tbl_allstates_nojson (states) values ("[\"calculator.Initial\", \"calculator.on\", \"calculator.on.Initial\",\"calculator.on.operand1\", \"calculator.on.opEntered\",\"calculator.on.operand2\", \"calculator.on.result\", \"calculator.Final\"]")