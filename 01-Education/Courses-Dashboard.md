# 📚 Education Dashboard

> Completed courses tracked via Dataview.  
> Last updated: {{date:YYYY-MM-DD}}

## Completed Courses (Newest First)

```dataview
TABLE 
    file.ctime AS "Completed",
    file.link AS "Course",
    length(file.outlinks) AS "Links",
    file.tags AS "Tags"
FROM "01-Education/Completed-Courses"
SORT file.ctime DESC
```

## Summary Stats

```dataview
TABLE WITHOUT ID 
    length(rows) AS "Total Completed",
    max(file.ctime) AS "Most Recent"
FROM "01-Education/Completed-Courses"
```

## By Year

```dataview
TABLE 
    length(rows) AS "Courses",
    max(file.ctime) AS "Latest"
FROM "01-Education/Completed-Courses"
GROUP BY dateformat(file.ctime, "yyyy") AS "Year"
SORT "Year" DESC
```

## Enhanced View (with extra fields)

Add these fields to your individual course notes (YAML frontmatter) for richer tables:

```dataview
TABLE 
    file.ctime AS "Completed",
    file.link AS "Course",
    rating AS "Rating",
    hours AS "Hours",
    instructor AS "Instructor",
    certificate AS "Certificate",
    file.tags AS "Tags"
FROM "01-Education/Completed-Courses"
WHERE rating
SORT file.ctime DESC
```

**Quick Links**
- [[01-Education/Index|Back to Education Index]]
- [[Templates/Course-Template|New Course Template]]
