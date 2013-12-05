<?php
// Simple PHP script to host .lrf uplaods and resultant analysis files
session_start();
if(!file_exists("config.php")) {
    echo "<h1>Configuration file not found.</h1><p>Please copy <code>config.sample.php</code> into <code>config.php</code> after mofiying the
    appropriate variables.";
}
?>
<!DOCTYPE HTML>
<html>
<head>
    <title>LOL Replay Analysis</title>
    
    <style type="text/css">
        @import url(http://fonts.googleapis.com/css?family=Open+Sans:400italic,700italic,400,700);
        body { font-family: "Open Sans", "Tahoma", sans-serif; background: #F0F0F0; font-size: 14px; }
        a { text-decoration: none; color: #0042AE;}
        a:hover { text-decoration: underline;}
        a:visited { color: #2E00AD;}
        a:active { color: #BC0000;}
        p.analysis_note { text-align: right; margin-top: 0;}
        .analysis_note { color: #999999; font-style: italic; font-size: 10pt;}
        
        h1 { padding-bottom: 0; margin-bottom: 0;}
        h2 { border-bottom: 1px solid #999; height: 29px; padding: 0; margin: 25px 0 20px 0;}
        h3 { padding: 0; margin: 25px 0 3px 0;}
        
        table { width: 100%;}
        table, td, th { border-collapse: collapse; padding: 2px 4px;}
        th { border-bottom: 1px solid #CCC; text-align: left;}
    </style>
</head>
<body>
    
    
    
</body>

</html>