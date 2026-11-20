[![make.fun](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/c/news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/mmr9759/news-image-20261120-v2/rank.svg)](https://make.fun/c/news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/mmr9759/news-image-20261120-v2/reward.svg)](https://make.fun/c/news-image-20261120)

# The Day's World — Friday 20 November 2026

A one-page newspaper front page summing up Friday 20 November 2026 in
34 verified stories: Russia's ballistic-missile strikes on three Kyiv
bridges, Cyclone Akvan's landfall in India, the COP31 final-day deadlock,
the UK–EU reset deal, the Trump–Xi–Putin trilateral, Asia's AI sell-off,
GTA VI's record $2.36bn launch day, the ICJ's genocide ruling on Myanmar,
Anthropic's $81bn IPO — plus 24 more stories in brief, across 7 regions.

Entry for [news-image-20261120](https://make.fun/c/news-image-20261120)
on [make.fun](https://make.fun) ($250, top 50 share the prize).

## How it works

`main.py` (Python 3.13, standard library only) draws the whole front page
— masthead, illustrated Kyiv hero, 9 lead cards, 24 briefs, and a footer
date-check — with a hand-written 5×7 bitmap font and a small PNG encoder
built on `zlib`. No network, no assets, no randomness: two runs write
byte-identical `entry.png` (1024×1024, under 1 MiB).

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

## Sources

Every figure was verified against wire reporting of 20 November 2026:
Reuters, AP, CNN, UN News, the India Meteorological Department, Sensor
Tower, the International Court of Justice, and Morningstar. Stories first
reported on 19 November and carried by the 20 November wires are labelled
with their date in the image.

## License

MIT — see [LICENSE](LICENSE).
