#!/usr/bin/expect
set user yourusername
set pass yourpassword
spawn hexo d
expect "Username"
send "$user\r"
expect "Password"
send "$pass\r"

interact
