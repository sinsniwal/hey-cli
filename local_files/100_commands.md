# 100 Most Used Terminal Commands & Tools

Compiled from GeeksForGeeks, DigitalOcean, Red Hat, Hostinger, and community sources.

---

## File & Directory Navigation
1. `cd` — Change directory
2. `ls` — List directory contents
3. `pwd` — Print working directory
4. `tree` — Display directory tree structure

## File & Directory Management
5. `touch` — Create empty file / update timestamps
6. `mkdir` — Create directories
7. `rmdir` — Remove empty directories
8. `cp` — Copy files and directories
9. `mv` — Move or rename files/directories
10. `rm` — Remove files or directories
11. `ln` — Create symbolic or hard links
12. `file` — Determine file type
13. `stat` — Display file or filesystem status

## File Viewing & Editing
14. `cat` — Concatenate and display file contents
15. `less` — Page through file contents interactively
16. `more` — View file contents (simpler pager)
17. `head` — Display beginning of a file
18. `tail` — Display end of a file (use `-f` to follow logs)
19. `nano` — Simple terminal text editor
20. `vim` — Advanced terminal text editor
21. `nvim` — Neovim (modern vim fork)

## Text Processing & Search
22. `grep` — Search text using patterns/regex
23. `sed` — Stream editor for text transformation
24. `awk` — Pattern scanning and processing language
25. `sort` — Sort lines of text
26. `uniq` — Filter or report duplicate lines
27. `wc` — Count lines, words, characters
28. `cut` — Remove sections from each line
29. `paste` — Merge lines of files
30. `tr` — Translate, squeeze, or delete characters
31. `diff` — Compare files line by line
32. `tee` — Read stdin and write to stdout and files
33. `fmt` — Simple text formatter
34. `rev` — Reverse lines of a file
35. `xargs` — Build and execute commands from stdin

## File Search
36. `find` — Search for files by criteria
37. `locate` — Fast file search via pre-built index
38. `which` — Locate a command binary
39. `whereis` — Locate binary, source, and man page for a command

## Permissions & Ownership
40. `chmod` — Change file permissions
41. `chown` — Change file owner
42. `chgrp` — Change group ownership
43. `umask` — Set default file creation permissions

## User Management
44. `whoami` — Print current username
45. `id` — Print user and group identity info
46. `sudo` — Execute command as superuser
47. `su` — Switch user
48. `passwd` — Change user password
49. `useradd` — Create a new user
50. `userdel` — Delete a user account
51. `usermod` — Modify a user account
52. `groupadd` — Create a new group
53. `w` — Show who is logged on
54. `last` — Show last logged-in users

## Process Management
55. `ps` — Report snapshot of current processes
56. `top` — Real-time process monitor
57. `htop` — Interactive process viewer
58. `kill` — Terminate process by PID
59. `killall` — Terminate processes by name
60. `pkill` — Kill processes by name/pattern
61. `nice` — Run command with modified scheduling priority
62. `renice` — Alter priority of running process
63. `bg` — Place job in background
64. `fg` — Place job in foreground
65. `jobs` — List active jobs
66. `pstree` — Display tree of processes
67. `watch` — Execute a program periodically

## System Information & Monitoring
68. `uname` — Print system information
69. `uptime` — Show system uptime
70. `free` — Display free and used memory
71. `df` — Filesystem disk space usage
72. `du` — Estimate file/directory space usage
73. `vmstat` — Report virtual memory statistics
74. `iostat` — Report CPU and I/O statistics
75. `lscpu` — Display CPU architecture info
76. `lsblk` — List block devices (disks/partitions)
77. `lsof` — List open files and ports
78. `date` — Print or set system date/time
79. `cal` — Display a calendar
80. `history` — View command history
81. `env` — Display environment variables
82. `export` — Set environment variables

## Networking
83. `ping` — Check network connectivity
84. `curl` — Transfer data from/to a server
85. `wget` — Download files from the web
86. `ssh` — Secure shell remote login
87. `scp` — Secure copy over SSH
88. `rsync` — Fast incremental file transfer
89. `ip` — Network interface config (Linux)
90. `ifconfig` — Network interface config (BSD/macOS)
91. `netstat` — Network statistics
92. `ss` — Socket statistics (modern netstat)
93. `traceroute` — Trace packet route to host
94. `dig` — DNS query tool
95. `nslookup` — DNS lookup
96. `nmap` — Network scanner
97. `nc` — Netcat, TCP/UDP utility

## Compression & Archives
98. `tar` — Create/extract archives
99. `gzip` / `gunzip` — Compress/decompress files
100. `zip` / `unzip` — Package and compress/extract files

## Disk & Storage
101. `fdisk` — Partition table manipulator
102. `mount` — Mount a filesystem
103. `umount` — Unmount a filesystem

## Service Management
104. `systemctl` — Linux systemd service manager
105. `launchctl` — macOS service manager
106. `crontab` — Schedule recurring jobs

## Terminal Session
107. `clear` — Clear the terminal screen
108. `man` — Display manual pages
109. `alias` — Create command aliases
110. `exit` — Terminate shell session
111. `tmux` — Terminal multiplexer
112. `screen` — Terminal session manager

## Modern CLI Alternatives
113. `rg` (ripgrep) — Faster alternative to grep
114. `fd` — Faster alternative to find
115. `bat` — cat with syntax highlighting
116. `eza` / `exa` — Modern ls replacement
117. `fzf` — Fuzzy finder
118. `zoxide` — Smarter cd that learns paths
119. `jq` — JSON processor
120. `yq` — YAML processor
121. `tldr` — Simplified man pages with examples
122. `httpie` — Modern curl alternative for APIs

## Developer Tools
123. `git` — Distributed version control
124. `gh` — GitHub CLI
125. `docker` — Container runtime
126. `docker-compose` — Multi-container orchestration
127. `kubectl` — Kubernetes CLI
128. `npm` — Node.js package manager
129. `yarn` — Alternative Node.js package manager
130. `pip` — Python package installer
131. `brew` — macOS Homebrew package manager
132. `cargo` — Rust package manager
133. `go` — Go toolchain
134. `make` — Build automation tool
135. `gcc` — GNU C compiler
136. `python` / `python3` — Python interpreter
137. `node` — Node.js runtime
138. `ruby` — Ruby interpreter

## Cloud & Infrastructure
139. `aws` — AWS CLI
140. `gcloud` — Google Cloud CLI
141. `az` — Azure CLI
142. `terraform` — Infrastructure as Code
143. `ansible` — Configuration management
144. `helm` — Kubernetes package manager
