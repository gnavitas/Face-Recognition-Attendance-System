<?php
// Force UTC+8 timezone
ini_set('date.timezone', 'Asia/Kuala_Lumpur');
date_default_timezone_set('Asia/Kuala_Lumpur');

// Get current time and add 4 hours to correct the offset
$current_time = time() + (4 * 3600); // Add 4 hours in seconds

echo "Current PHP Timezone: " . date_default_timezone_get() . "<br>";
echo "Current Time (Adjusted): " . date('Y-m-d H:i:s', $current_time) . "<br>";
echo "Current Timezone: " . date('e') . "<br>";
echo "Timezone Offset: " . date('P') . "<br>";

// Additional verification with manual adjustment
$now = new DateTime();
$now->modify('+4 hours'); // Add 4 hours to correct the time
echo "Adjusted DateTime: " . $now->format('Y-m-d H:i:s') . "<br>";
echo "DateTime Object Timezone: " . $now->getTimezone()->getName() . "<br>";
echo "DateTime Object Offset: " . $now->getOffset()/3600 . " hours<br>";

// Show raw time for debugging
echo "<br>Debug Information:<br>";
echo "Raw Unix Timestamp: " . time() . "<br>";
echo "Raw Time: " . date('Y-m-d H:i:s') . "<br>";
?> 