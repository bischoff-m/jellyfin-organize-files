---
uid: server-media-shows
title: Shows
---

# Shows

The most common naming scheme for shows is categorizing the files by series and then season. Another common method is simply using series folders, especially for shows that are organized by air date and those without seasons. Adding the year at the end in parentheses will yield the best results when scraping metadata.

:::tip

In order to help with identifying a series, Jellyfin can make use of media provider identifiers. This can be specified in your show's folder name, for example: `Series Name (2018) [tmdbid-65567]` or `Series Name (2018) [tvdbid-65567]` (`imdbid` is not supported for shows)

:::

```txt
Shows
├── Series Name A (2010)
│   ├── Season 00
│   │   ├── Some Special.mkv
│   │   ├── Series Name A S00E01.mkv
│   │   └── Series Name A S00E02.mkv
│   ├── Season 01
│   │   ├── Series Name A S01E01-E02.mkv
│   │   ├── Series Name A S01E03.mkv
│   │   └── Series Name A S01E04.mkv
│   └── Season 02
│       ├── Series Name A S02E01.mkv
│       ├── Series Name A S02E02.mkv
│       ├── Series Name A S02E03 Part 1.mkv
│       └── Series Name A S02E03 Part 2.mkv
└── Series Name B (2018)
    ├── Season 01
    |   ├── Series Name B S01E01.mkv
    |   └── Series Name B S01E02.mkv
    └── Season 02
        ├── Series Name B S02E01-E02.mkv
        └── Series Name B S02E03.mkv
```

:::note

Avoid special characters such as \* in M\*A\*S\*H, use MASH instead.

:::

:::note

Do not mix episodes inside season folders and episodes on the Series root folder.

Do not abbreviate the Season folder with `S01` or `SE01` or alike.

:::

:::note

Season folders shouldn't contain the series name, otherwise Jellyfin can in certain cases (Stargate SG-1 due to the dash and one, for instance) misdetect your episodes and put them all under the same season.

:::
