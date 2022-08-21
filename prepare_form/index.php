<?php

use Google\CloudFunctions\FunctionsFramework;
use Google\Cloud

FunctionsFramework::http('prepare_form', 'prepare_form');

function prepare_form(ServerRequestInterface $request): string
{
	return file_get_contents("https://storage.googleapis.com/cdn.youngklopp.com/form.html");
}

?>
