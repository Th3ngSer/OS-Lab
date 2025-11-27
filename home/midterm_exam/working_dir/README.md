Getting Started (Student Instructions)
Each student must copy the working folder to their home directory before beginning:

cp -r /home/midterm_exam ~/midterm_exam
cd ~/midterm_exam
mkdir commands results
📂 Create folders: commands/ and results/
✍️ For each task:
•	commands/cmd0X.txt → the command
•	results/res0X.txt → the output

midterm_exam/
└── working_dir/
    ├── notes/
    │   ├── meeting.txt
    │   └── plan1.txt
    ├── README.md
    ├── reports/
    │   ├── bugfixes.txt
    │   └── summary.txt
    └── users.csv

Ex 1: Basic Commands, Wildcards, Redirection (Tasks 01–05)
________________________________________
✅ Task 01: List Files Using Wildcards
List all .txt files inside the notes/ folder using *.
📄 Files:
•	cmd01.txt: your ls command
•	res01.txt: the output
________________________________________
✅ Task 02: Copy Multiple Files Using Brace Expansion
Copy plan1.txt and meeting.txt from notes/ using {} to folder copy/ inside ~/midterm_exam.
📄 Files:
•	cmd02.txt: your cp command
•	res02.txt: output of tree  ~/midterm_exam/
________________________________________
✅ Task 03: Move and Rename a File
Move summary.txt from reports/ to ~/midterm_exam and rename it project_summary.txt.
📄 Files:
•	cmd03.txt: your mv command
•	res03.txt: result of tree  ~/midterm_exam/
________________________________________
✅ Task 04: Trigger a Real Error
Try to move bugfixes.txt to / to produce a permission error.
📄 Files:
•	cmd04.txt: your mv command
•	res04.txt: error message output
________________________________________
✅ Task 05: Use Complex Wildcards
List all files in results/ that:
•	has a file name ended with at least 2 number
•	has any file extensions
Example pattern: cmd05.log, res01.txt
📄 Files:
•	cmd05.txt: your ls command
•	res05.txt: the matching file names

Ex 2: Text Processing (grep, cut, wc, sort, uniq, pipes) (Tasks 06–10)
________________________________________
✅ Task 06: Count Lines in README
Use cat and wc -l to count lines in README.md.
📄 Files:
•	cmd06.txt: your command
•	res06.txt: number of lines
________________________________________
✅ Task 07: Extract Emails from CSV
Extract the field (emails) from users.csv using cut, and save to results/emails.txt.
📄 Files:
•	cmd07.txt: your cut command
•	email.txt: output from command used in cmd07
•	res07.txt: contains the first 5 lines of emails.txt
________________________________________
✅ Task 08: Count Occurrences of a Word
Use grep -i and wc to count how many times bug appears in bugfixes.txt.
📄 Files:
•	cmd08.txt: your command
•	res08.txt: the number
________________________________________
✅ Task 09: Show Unique Email Domains
Extract domain names (after @) from users.csv, then sort and show only unique ones.
📄 Files:
•	cmd09.txt: your cut | cut | sort | uniq command
•	res09.txt: list of domains
________________________________________
✅ Task 10: Find Words That Start or End With a Letter
From bugfixes.txt, use grep with a regular expression to match words that:
•	Start with b OR end with d (case-insensitive)
📄 Files:
•	cmd10.txt: your grep -E command
•	res10.txt: the matching lines

Expected tree Structure

midterm_exam/
├── working_dir/
│   ├── notes/
│   │   ├── plan1.txt
│   │   └── meeting.txt
│   ├── reports/
│   │   ├── summary.txt
│   │   └── bugfixes.txt
│   ├── users.csv
│   └── README.md
├── copy/
│   ├── plan1.txt             # ← newly copied
│   └── meeting.txt           # ← newly copied
├── emails.txt                # extracted from users.csv (Task07)\
|-- project_summary.txt
├── commands/
│   ├── cmd01.txt
│   ├── cmd02.txt
│   ├── ...
│   └── cmd10.txt
├── results/
│   ├── res01.txt
│   ├── res02.txt
│   ├── ...
│   └── res10.txt
