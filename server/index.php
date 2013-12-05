<?php
// Simple PHP script to host .lrf uplaods and resultant analysis files
require("config.php");

session_start();
if(!file_exists("config.php")) {
    echo "<h1>Configuration file not found.</h1><p>Please copy <code>config.sample.php</code> into <code>config.php</code> after mofiying the
    appropriate variables.";
    die();
}

//User authentication section begin
if($_GET['action'] == "login") {
    $_SESSION['username'] = $_POST['username'];
    $_SESSION['password'] = $_POST['password'];
}
elseif($_GET['action'] == "logout") {
    unset($_SESSION['username']);
    unset($_SESSION['password']);
}
?>
<?php
if(!$_SESSION['username'] || !$_SESSION['password'] || !in_array($_SESSION['username'], array_keys($_CONFIG['users'])) 
        || $_CONFIG['users'][$_SESSION['username']] != $_SESSION['password']) { 
            include("header.php"); ?>
<h1>Login Required</h1>
<p>This project is currently in closed alpha. If you have been given a username and password, please enter them to continue.</p>
<br />
<form action="?action=login" method="post" />
<?php if($_POST['username']) echo "<p style='color: #F00'>Invalid username or password.</p>" ?>
<table>
    <tr>
        <td>Username</td>
        <td><input type="text" name="username" size="40" /></td>
    </tr>
    <tr>
        <td>Password</td>
        <td><input type="password" name="password" size="40" /></td>
    </tr>
</table>
<input type="submit" value="Login" />
</form>

</div>

</body>

</html>
<?php
die (); }
//End of user authentication section. Everything beyond here is logged-in users only.
$dbh = mysql_connect($_CONFIG['mysql_host'], $_CONFIG['mysql_username'], $_CONFIG['mysql_password']);
mysql_select_db($_CONFIG['mysql_database'], $dbh);


if($_GET['action'] == "upload") {
    if(!is_dir("lrf")) {
        mkdir("lrf");
    }
    if(end(explode(".", $_FILES["lrffile"]["name"])) != "lrf" || $_FILES["lrffile"]["size"] > 30000000) {
        $fileerror = "Invalid File";
    }
    else {
        $orig_filename = mysql_real_escape_string(implode(".", array_slice(explode(".", $_FILES["lrffile"]["name"]), 0, -1)));
        $result = mysql_query("INSERT INTO replays (created_at, orig_filename) VALUES ('".date('Y-m-d H:i:s')."', '$orig_filename')", $dbh)
            or die("Internal Database Error.");
        $id = mysql_insert_id();
        
        if (move_uploaded_file($_FILES["lrffile"]["tmp_name"], "lrf/$id.lrf")) {
            chmod("lrf/$id.lrf", 0777);
            $filesuccess = ".lrf file uploaded sucessfully.";
        }
        else
            $fileerror = "Internal server error.";
    }
}


if(!$_GET['replay_id'])
include("header.php");
?>
<h1>League of Legends Replay Analysis Service</h1>
<br />
<form action="?action=upload" method="post" enctype="multipart/form-data">
    <fieldset>
        <legend>Upload a .lrf file (Max 30MB)</legend>
        <p>Please upload a .lrf file created on the 3.14.0.738 patch. You must upload the spectator version of the .lrf file.</p>
        <?php if($fileerror) echo "<p style='color: #F00'>$fileerror</p>"; ?>
        <?php if($filesuccess) echo "<p style='color: #0A0'>$filesuccess</p>"; ?>
        <input type="file" name="lrffile" /><br />
        <input type="submit" value="Upload" />
    </fieldset>
</form>

</div>

</body>

</html>