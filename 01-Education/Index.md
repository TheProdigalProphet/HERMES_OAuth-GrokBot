# 01-Education Index

## Folder Structure
- 01-Education/
  - Completed-Courses/ ← Your Dataview source
  - In-Progress/
  - Planned/
  - Templates/
  - Courses-Dashboard.md
  - Index.md (this file)

## Quick Links
- [[Courses-Dashboard]]
- [[Completed-Courses Index]] (auto-generated via Dataview below)

## All Completed Courses
```dataview
LIST 
FROM "01-Education/Completed-Courses"
SORT file.ctime DESC
```

## In-Progress Courses
```dataview
TABLE file.link AS "Course", file.mtime AS "Last Updated"
FROM "01-Education/In-Progress"
SORT file.mtime DESC
```

**Education Dashboard:** [[Courses-Dashboard]]
