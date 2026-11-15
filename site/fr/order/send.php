<?php
// Order form of Gravit Path: the fields are written into the message and handled like a contact message.
$f = fn($k, $n) => mb_substr(trim((string)($_POST[$k] ?? '')), 0, $n);
$_POST['message'] = "ORDER
Plan: " . $f('plan', 20) . "
Payment: " . $f('pay', 20) . "
Language: " . $f('lang', 5)
    . "
Billing address: " . $f('addr', 1000) . "
Notes: " . $f('note', 2000);
$_POST['topic'] = 'sales';
require dirname(__DIR__, 3) . '/contact-forms/lib.php';
cf_handle('gravitpath.world');
