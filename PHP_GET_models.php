<?php
// This reads the list of models from the owner's Shapeways shop and presents the list as an html table.
// author: stonysmith 2017-04-21

//error_reporting(E_ALL); 
//ini_set('display_errors', '1');
//ini_set("log_errors", 1);
//echo ini_get("error_log");
//ini_set("error_log", "./php-error.log");

function getAccessToken(){
$client_id = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa";
$client_secret = "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb";
$user=$client_id.":".$client_secret;
$url = 'https://api.shapeways.com/oauth2/token';
$params = array(
    "grant_type" => "client_credentials"
);

$url = 'https://api.shapeways.com/oauth2/token';
$process = curl_init($url);
//curl_setopt($process, CURLOPT_HTTPHEADER, array('Content-Type: application/xml', $additionalHeaders));
//curl_setopt($process, CURLOPT_HEADER, 1);
curl_setopt($process, CURLOPT_USERPWD, $client_id . ":" . $client_secret);
curl_setopt($process, CURLOPT_TIMEOUT, 30);
curl_setopt($process, CURLOPT_POST, 1);
curl_setopt($process, CURLOPT_POSTFIELDS, $params);
curl_setopt($process, CURLOPT_RETURNTRANSFER, TRUE);
$result = curl_exec($process);
curl_close($process);
//echo 'result='.$result.'<br>';
$responseObj = json_decode($result);
//echo 'json='.string($responseObj).'<br>';
//echo 'vars=';
//var_dump($responseObj);
//echo '<br>';
$access_token=$responseObj->access_token;
//echo "Access token: " . $access_token.'<br>';
return $access_token;
}

function getModels($access_token,$page){
$url = 'https://api.shapeways.com/models/v1?page='.$page;
$process = curl_init($url);
curl_setopt($process, CURLOPT_HTTPHEADER, array('Authorization: Bearer '.$access_token,'Content-type: application/x-www-form-urlencoded'));
curl_setopt($process, CURLOPT_HEADER, 1);
curl_setopt($process, CURLOPT_TIMEOUT, 30);
curl_setopt($process, CURLOPT_RETURNTRANSFER, TRUE);
$content=curl_exec($process);
$header_size = curl_getinfo($process, CURLINFO_HEADER_SIZE);
$response['content'] = $content;
$response['err'] = curl_errno($process);
$response['errmsg']  = curl_error($process);
$response['header']  = curl_getinfo($process);
$response['header_size']=$header_size;
$response['body'] = substr($content, $header_size);
curl_close($process);
//echo '<br><br>body=';
//echo $body;
return $response;
}

function formatModels($models){
foreach ($models as $key => $model) {
  //echo "<br>$key = ".var_dump($model);
  echo '<tr><td><a href="https://www.shapeways.com/model/upload-and-buy/'.$model['modelId'].'">'.$model['modelId'].'</a><td>'.$model['title'].'</tr>';
  }}

echo '<html><body><table border=1 style="border-collapse:collapse"><tr><td>ModelId<td>Title</tr>';

$access_token=getAccessToken();
$models='any';
$page=1;
while ($models<>'') {
$resp=getModels($access_token,$page);
$body=$resp['body'];
$responseObj = json_decode($body,true);
$models=$responseObj['models'];
if ($models <> '') {
formatModels($models);
//echo '<br><br>jmodels=';
}
$page=$page+1;
}
echo '</table></body></html>';
?>
