#!/bin/bash
cd /home/moaid/cherenkov-professional
gh issue list --state open --limit 50 --json number,title,labels --jq '.[] | {n: .number, t: .title, l: [.labels[].name] | join(",")}' 
