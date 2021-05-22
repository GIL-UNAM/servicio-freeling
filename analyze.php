<?php

include("functions.php");


if ($_SERVER['REQUEST_METHOD'] === 'POST') {
	
	
  if(isset($_REQUEST["outf"])){

    //Asegurarse que se envió un archivo
    if(!isset($_FILES["file"])){
      http_error("400 Bad Request", "No text file sent");
    }

    //Recolectar parámetros
    $outf = $_REQUEST["outf"];
    $format = $_REQUEST["format"];
    $filename = $_FILES["file"]["tmp_name"];

    //Determinar idioma
    if(isset($_REQUEST["lang"])){
        //Si se solicita detección automática del idioma
        if($_REQUEST["lang"] == "auto"){
            $lang = detectLang($filename);
        }else{
            $lang = $_REQUEST["lang"];
        }
        //Si el idioma no es soportado actualmente
        if($lang != "es" && $lang != "en" && $lang != "fr"){
            http_error("400 Bad Request", "Unsupported language ".$_REQUEST["lang"]);
        }
        $lang = "_".$lang;
    }else{
        //Por default usar español
        $lang = "_es";
    }
    $data = "resultados:  ";
    //Alguno de los tres tipos de análisis
    if($outf == "tagged"){
      $data = tagged($filename, $format, $lang);
    }
    else if($outf == "parsed"){
      $data = parsed($filename, $format, $lang);
    }
    else if($outf == "dep"){
      $data = dep($filename, $format, $lang);
    }

    //-----------------------------------------
    //Deprecated, usar parámetro lang
    //------------------------------------------
    else if($outf == "dep_en"){
      $data = dep_en($filename, $format, "_en");
    }
    else if($outf == "tagged_en"){
      $data = tagged($filename, $format, "_en");
    }
    else if($outf == "tagged_fr"){
      $data = tagged($filename, $format, "_fr");
    }
    // -------------------------------------------

    //Si no es ninguno de los análisis reconocidos
    else{
      http_error("400 Bad Request", "$outf not a recognized option");
    }

    //Mostrar resultados según formato solicitado
    echo_data($data, $format);
  }
  else{
    http_error("400 Bad Request", "No format specified");
  }
}else{
  http_error("405 Method not allowed", $_SERVER['REQUEST_METHOD']." method not allowed");
}


?>
