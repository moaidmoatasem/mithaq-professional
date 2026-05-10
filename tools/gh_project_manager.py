#!/usr/bin/env python3
"""CHERENKOV GitHub Project Manager - Agent CLI for managing GitHub PM operations."""
import argparse, json, subprocess, sys
from datetime import datetime, timedelta
from pathlib import Path

REPO = "moaidmoatasem/cherenkov-professional"

def gh(args, capture=True):
    cmd = ["gh"] + args + ["--repo", REPO]
    try:
        r = subprocess.run(cmd, capture_output=capture, text=True, check=True)
        return r.stdout.strip() if capture and r.stdout else ""
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr}", file=sys.stderr); return None

def j(raw):
    if not raw: return []
    try: return json.loads(raw)
    except: return raw

def issue_create(args):
    a = ["issue", "create", "--title", args.title, "--body", args.body or ""]
    if args.labels:
        for l in args.labels.split(","): a += ["--label", l.strip()]
    if args.milestone: a += ["--milestone", args.milestone]
    if args.assignee: a += ["--assignee", args.assignee]
    gh(a, False)

def issue_update(args):
    a = ["issue", "edit", args.issue]
    if args.add_labels:
        for l in args.add_labels.split(","): a += ["--add-label", l.strip()]
    if args.remove_labels:
        for l in args.remove_labels.split(","): a += ["--remove-label", l.strip()]
    if args.milestone: a += ["--milestone", args.milestone]
    if args.add_assignee: a += ["--add-assignee", args.add_assignee]
    if args.title: a += ["--title", args.title]
    gh(a, False)

def issue_list(args):
    a = ["issue", "list", "--json", "number,title,state,labels,milestone,updatedAt"]
    if args.state: a += ["--state", args.state]
    if args.label: a += ["--label", args.label]
    if args.milestone: a += ["--milestone", args.milestone]
    if args.limit: a += ["--limit", str(args.limit)]
    r = j(gh(a))
    if not r: return
    for i in r:
        ls = ",".join(l["name"] for l in i.get("labels",[])) if i.get("labels") else ""
        ms = i.get("milestone",{}).get("title","") if i.get("milestone") else ""
        print(f"#{i['number']:>5} {i['state']:<8} {i['title'][:60]:<60} {ls[:20]:<20} {ms[:15]:<15}")

def milestone_list(args):
    r = j(gh(["milestone","list","--json","title,dueDate,openIssues,closedIssues"]))
    if r:
        for m in r: print(f"  {m['title']:25} {m['closedIssues']}/{m['openIssues']+m['closedIssues']} Due: {m.get('dueDate','N/A')[:10]}")

def release_create(args):
    a = ["release", "create", args.tag, "--title", args.title or args.tag, "--notes", args.notes or ""]
    if args.target: a += ["--target", args.target]
    if not args.draft: a += ["--latest"]
    gh(a, False)
    if args.discuss:
        gh(["discussion","create","--title",f"Release: {args.title or args.tag}",
            "--body",f"## {args.title or args.tag}\n\n{args.notes or 'Release notes'}","--category","Announcements"], False)

def status_report(args):
    print("="*60)
    print(f"CHERENKOV Status — {datetime.now().isoformat()[:10]}")
    print("="*60)
    r = j(gh(["milestone","list","--json","title,dueDate,openIssues,closedIssues"]))
    if r:
        print("\n── Milestones ──")
        for m in r: print(f"  {m['title']:25} {m['closedIssues']}/{m['openIssues']+m['closedIssues']} Due: {m.get('dueDate','N/A')[:10]}")
    print("\n── Open PRs ──")
    r = j(gh(["pr","list","--state","open","--json","number,title,author","--limit","10"]))
    if r:
        for p in r: print(f"  #{p['number']:>5} {p['title'][:60]:60} @{p['author']['login']}")

def generate_changelog(args):
    r = j(gh(["release","list","--limit","1","--json","tagName,publishedAt"]))
    since = r[0]["publishedAt"] if r else "1970-01-01"
    prs = j(gh(["pr","list","--state","merged","--json","number,title,labels,author","--limit","50"]))
    if not prs: return
    cl = {}
    for p in prs:
        ls = [l["name"] for l in p.get("labels",[])]
        if any(x in ls for x in ["feature","enhancement"]): cat="Added"
        elif any(x in ls for x in ["bug","bugfix"]): cat="Fixed"
        elif "security" in ls: cat="Security"
        elif "docs" in ls: cat="Docs"
        else: cat="Other"
        cl.setdefault(cat,[]).append(f"- {p['title']} (#{p['number']})")
    print("## Changelog\n")
    for cat, items in cl.items():
        print(f"### {cat}"); [print(i) for i in items]; print()

def main():
    global REPO
    p = argparse.ArgumentParser(description="CHERENKOV GitHub PM CLI")
    p.add_argument("--repo", default=REPO)
    s = p.add_subparsers(dest="cmd")
    for name, args_list in [
        ("issue-create", [("--title",True),("--body",False),("--labels",False),("--milestone",False),("--assignee",False)]),
        ("issue-update", [("--issue",True),("--add-labels",False),("--remove-labels",False),("--milestone",False),("--add-assignee",False),("--title",False)]),
        ("issue-list", [("--state",False),("--label",False),("--milestone",False),("--limit",False)]),
        ("milestone-list", []),
        ("release-create", [("--tag",True),("--title",False),("--notes",False),("--target",False),("--draft",False),("--discuss",False)]),
        ("status-report", []),
        ("generate-changelog", []),
    ]:
        sp = s.add_parser(name)
        for arg, req in args_list: sp.add_argument(arg, required=req)
    args = p.parse_args()
    if not args.cmd: p.print_help(); return
    if args.repo: REPO = args.repo
    {"issue-create":issue_create,"issue-update":issue_update,"issue-list":issue_list,
     "milestone-list":milestone_list,"release-create":release_create,
     "status-report":status_report,"generate-changelog":generate_changelog}.get(args.cmd)(args)

if __name__ == "__main__": main()
