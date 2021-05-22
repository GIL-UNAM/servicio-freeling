<?php $endpoint = "http://www.corpus.unam.mx/servicio-freeling/analyze.php"; ?>
<!DOCTYPE html>
<html>

<head>
  <title>Servicio Freeling</title>
  <meta http-equiv="content-type" content="text/html; charset=utf-8" />
  <link rel="stylesheet" href="//maxcdn.bootstrapcdn.com/bootstrap/3.2.0/css/bootstrap.min.css">
  <link rel="stylesheet" href="//maxcdn.bootstrapcdn.com/bootstrap/3.2.0/css/bootstrap-theme.min.css">
  <script src="//maxcdn.bootstrapcdn.com/bootstrap/3.2.0/js/bootstrap.min.js"></script>
  <link rel="stylesheet" href="prism.css">
  <script src="prism.js"></script>
  <link href='https://fonts.googleapis.com/css?family=PT+Sans' rel='stylesheet' type='text/css'>
  <link rel="shortcut icon" href="favicon.ico" type="image/x-icon">
  <link rel="icon" href="/favicon.ico" type="image/x-icon">
  <style>
  body{
      font-family: 'PT Sans', sans-serif;
  }
  footer{
      color: white;
      background-color: #5D5D5D;
      padding: 15px 15px 15px 15px;
      margin-top: 30px;
  }
  .required::before{
    color:red;
    content:"*"
  }
  footer a{
      color: white
  }
  footer a:hover{
      color: white
  }
  </style>
</head>

<body>

<div class="jumbotron">
<div class="container">
 
  <div class="row">

  <div class="col-md-6">
    <h1>Freeling via web</h1>
    <p><small><a href="http://nlp.lsi.upc.edu/freeling/node/1">Freeling (v. 4.0)</a> es una suite de herramientas para análisis del lenguaje
    desarrollada en la Universitat Politècnica de Catalunya. En este sitio el 
    <a href="http://www.iling.unam.mx">Grupo de Ingeniería Lingüística</a>
    de la UNAM pone a disposición un API para usar dicha herramienta via web.<p>
	Ponte en <a href="mailto:gch@pumas.iingen.unam.mx">contacto</a> para problemas, dudas y comentarios</small></p>
	</p>
	
  </div> 

  <div class="col-md-6">
    <h2>Usar online</h2>
    <fieldset>
    <div class="form-group">
    <form action="analyze.php" method="post"enctype="multipart/form-data">
      <label for="file">Archivo:</label>
      <span style="color:#377BB5"><strong><small>Debe ser en formato .txt (texto plano) y codificado en utf-8</small></strong></span>
      <input type="file" name="file" id="file" class="form-control" required="required"><br/>
      <label for="outf">Salida analizador:</label>
      <select name="outf" class="form-control">
        <option value="tagged">Etiquetado</option>
        <option value="parsed">Parsed</option>
        <option value="dep">Dependencias</option>
      </select>
      <br/>
      <label for="lang">Idioma:</label>
      <select name="lang" class="form-control">
        <option value="es">Español</option>
        <option value="en">Inglés</option>
        <option value="fr">Francés</option>
        <option value="auto">Automático</option>
      </select>
      <br/>
      <label for="format">Formato respuesta:</label>
      <select name="format" class="form-control">
        <option value="html">HTML</option>
        <option value="json">json</option>
        <option value="plain">Texto plano</option>
      </select>
      <br/>
      <input type="submit" name="submit" value="Enviar" class="btn btn-lg btn-primary">
    </form>
    </div>
    </fieldset>
  </div>

  </div>

</div>
</div>

<div class="container">

  <h1>API</h1>
  <div>
    <p><strong>Endpoint:</strong> <code><?php echo $endpoint?></code></p>
    <span class="required"></span> Campos requeridos
    <table class="table">
      <thead>
        <tr>
          <th>Parámetro</th>
          <th>Valores</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>file<span class="required"></span></td>
          <td>Archivo a procesar</td>
        </tr>
        <tr>
          <td>outf<span class="required"></span></td>
          <td>Tipo de análisis a realizar
            <ul>
              <li><strong>tagged</strong> Tokenizado, lematizado y etiquetado POS.</li>
              <li><strong>parsed</strong> Parseado sintácticamente</li>
              <li><strong>dep</strong> Árbol de dependencias</li>
            </ul>
          </td>
        </tr>
        <tr>
          <td>lang</td>
          <td>Idioma
            <ul>
              <li><strong>es</strong> Español</li>
              <li><strong>en</strong> Inglés</li>
              <li><strong>fr</strong> Francés</li>
              <li><strong>auto</strong> Detección automática <br/>(debe de todos modos ser alguno de los idiomas soportados)</li>
            </ul>
            Este parámetro de ser omitido, tomará por default el valor <strong>es</strong>
          </td>
        </tr>
        <tr>
          <td>format<span class="required"></span></td>
          <td>Formato de la respuesta
            <ul>
              <li><strong>plain</strong> Texto plano, tal como Freeling arroja el resultado</li>
              <li><strong>json</strong> JSON, estructurado de acuerdo al análisis realizado</li>
              <li><strong>html</strong> HTML, para ser mostrado en una página web</li>
            </ul>
          </td>
        </tr>
      </tbody>
    </table>
    <p class="alert alert-warning">
        <span class="glyphicon glyphicon-warning-sign"></span>
        <strong>Los archivos deben estar en texto plano (.txt) y codificados en UTF-8</strong>
    </p>
    <p class="alert alert-warning">
        <span class="glyphicon glyphicon-warning-sign"></span>
        <strong>Por el momento en fránces sólo está disponible análisis de etiquetado (tagged)</strong>
    </p>
  </div>


  <h1>Ejemplos</h1>
  <div>
    <h2>curl</h2>
    <pre>
    <code class="language-bash">
      curl -F file=@ruta_archivo.txt "<?php echo $endpoint?>?outf=tagged&format=plain"</code>
    </pre>
    <h2>Python</h2>
    <pre>
    <code class="language-python">
      #-*- coding: utf-8 -*-
      import requests

      #Archivo a ser enviado
      files = {'file': open('ruta_de_archivo.txt', 'rb')}
      #Parámetros
      params = {'outf': 'tagged', 'format': 'json'}
      #Enviar petición
      url = "<?php echo $endpoint?>"
      r = requests.post(url, files=files, params=params)
      #Convertir de formato json<br/>
      obj = r.json()

      #Ejemplo, obtener todos los lemas<br/>
      for sentence in obj:<br/>
          for word in sentence:<br/>
              print word["lemma"]</code>
    </pre>
  </div>

</div>

<footer>
    <a href="http://www.iling.unam.mx">Grupo de Ingeniería Lingüística</a>, <?php echo date("Y") ?>
</footer>

</body>
</html>
