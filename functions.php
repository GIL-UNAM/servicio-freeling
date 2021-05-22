<?php
$CLIENT_PATH = "/usr/bin/analyzer_client";
$PORTS = array(
  "tagged_es" => "9999",
  "tagged_en" => "9995",
  "tagged_fr" => "9994",
  "parsed_es" => "9998",
  "parsed_en" => "9993",
  "parsed_fr" => "9992",
  "dep_es" => "9997",
  "dep_en" => "9996",
  "dep_fr" => "9991"
);

function echo_data($data, $format="plain"){
  if($format == "plain"){
    echo $data;
  }
  else if($format == "json"){
    header("Content-type: application/json");
    echo $data;
  }
  else if($format == "html"){
    header("Content-type: text/html");
    echo "<!DOCTYPE html>";
    echo "<html><head>";
    echo "<title>Result</title>";
    echo '<link href="estilo_arbol.css" rel="stylesheet" type="text/css">';
    echo "<meta http-equiv=\"content-type\" content=\"text/html; charset=utf-8\"/>";
    echo "<body>";
    $data = str_replace("[", "<div class=\"nodo\">", $data);
    $data = str_replace("]", "</div>", $data);
    echo $data;
    echo "</body></html>";
  }
}

function http_error($status, $message){
  header("HTTP/1.0 ".$status);
  header("Content-type: application/json");
  echo json_encode(array("error"=>$message));
  die();
}

function execute($outf, $filename, $pipe = ""){
  global $CLIENT_PATH, $PORTS;
  
  $port = $PORTS[$outf];
  $command = "$CLIENT_PATH localhost:$port < $filename";
  if($pipe){
    $command.= " | $pipe";
  }
  $x = shell_exec($command);
  return $x; 
}

function tagged($filename, $format="plain", $lang="_es"){
  $x = execute("tagged".$lang, $filename);
  if($format == "plain") 
	  return $x;
  
  
  
  
  
  $data = array();
  $sentence = array();
  foreach(explode("\n",$x) as $line){
    $fields = explode(" ", $line);
    if(count($fields)==4){
      $sentence[] = array(
        "token" => $fields[0],
        "lemma" => $fields[1],
        "tag" => $fields[2],
        "prob" => $fields[3]
      );
    }else if(count($sentence)!=0){
      $data[] = $sentence;
      $sentence = array();
    }
  }
  if($format == "json") return json_encode($data);
  if($format == "html"){
    $html = "";
    foreach($data as $sentence){
      $html.= "<table><tr><th>Token</th><th>Lemma</th><th>Tag</th><th>Prob.</th></tr>";
      foreach($sentence as $w){
        $html.= "<tr>";
        $html.= "<td>{$w['token']}</td>";
        $html.= "<td>{$w['lemma']}</td>";
        $html.= "<td>{$w['tag']}</td>";
        $html.= "<td>{$w['prob']}</td>";
        $html.= "</tr>";
      }
      $html.= "</table><hr/>";
    }
    return $html;
  }
}

function parsed($filename, $format="plain", $lang="_es"){
  $pipe = "";
  if($format == "json"){
    $pipe = "python tree2json.py parsed";
  }
  $data = execute("parsed".$lang, $filename, $pipe);
  if($format == "html"){
    $data = str_replace("\n", "<br/>", $data);
    $data = str_replace(" ", "&nbsp;", $data);
  }
  return $data;
}

function dep($filename, $format="plain", $lang="_es"){
  $pipe = "";
  if($format == "json"){
    $pipe = "python tree2json.py dep";
  }
  $data = execute("dep".$lang, $filename, $pipe);
  if($format == "html"){
    $data = str_replace("\n", "<br/>", $data);
    $data = str_replace(" ", "&nbsp;", $data);
  }
  return $data;
}

function detectLang($file){
    $res = shell_exec("langid < $file");
    $expl = explode(",", $res);
    $lang = $expl[0];
    return $lang;
}

?>
