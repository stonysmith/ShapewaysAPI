<?php
  ini_set("log_errors", 1);
  ini_set("error_log", "./php-error.log");
  error_log( "Hello, errors!" );
  session_start();
  require_once 'config.php';
    /* contains

define('OAUTH2_CLIENT_ID', 'Redacted');
define('OAUTH2_CLIENT_SECRET', 'Redacted');

define('OAUTH2_URL_AUTHORIZE','https://api.shapeways.com/oauth2/authorize');
define('OAUTH2_URL_TOKEN','https://api.shapeways.com/oauth2/token');
define('OAUTH2_URL_BASE', 'https://api.shapeways.com/');

    */
  print_r("<pre>");

function apiRequest($url, $post=FALSE, $headers=array()) {
  $ch = curl_init($url);
  curl_setopt($ch, CURLOPT_RETURNTRANSFER, TRUE);
  $x=http_build_query($post);
  $x=json_encode($post);
  if ($post) {
      curl_setopt($ch, CURLOPT_POSTFIELDS,$x);
    }
  print_r("url=".$url."<br>");
  print_r("data=".$x."<br>");
  $headers[] = 'Accept: application/json';
  if(session('access_token'))
    $headers[] = 'Authorization: Bearer ' . session('access_token');
  curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
  print_r("<br>curl<br>");
  $response = curl_exec($ch);
  print_r($response."<br>");
  return json_decode($response);
}

function session($key, $default=NULL) {
  return array_key_exists($key, $_SESSION) ? $_SESSION[$key] : $default;
}

    //make sure we are connected to shapeways
    print_r("logging in<br>");
    if (!isset($_SESSION['access_token'])) {
        $token=apiRequest(OAUTH2_URL_TOKEN, array(
            "grant_type"=>      "client_credentials",
            "client_id"=>       OAUTH2_CLIENT_ID,
            "client_secret"=>   OAUTH2_CLIENT_SECRET   
        ));
        $_SESSION['access_token'] = $token->access_token;
    }
    print_r("logged in<br>");
    print_r($_SESSION);

    //try to upload file
    $filename = "Box.stl"; //does exist
    $file = file_get_contents($filename);
    $data = array(
      "fileName" => $filename,
      "uploadScale" => ".001",
      "hasRightsToModel" => 1,
      "acceptTermsAndConditions" => 1,
      "file" => base64_encode($file)//rawurlencode(),
    );

    print_r($data);
    print_r("sending<br>");
    $response = apiRequest(OAUTH2_URL_BASE."models/v1",$data,$array);
    print_r("sent<br>");
    print_r($response);