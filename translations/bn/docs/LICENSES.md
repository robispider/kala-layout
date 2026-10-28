# লাইসেন্স

নতুন অভিন্ন B01 ম্যাপ ও গবেষণার এক্সপোর্টে রিপোজিটরির [MIT লাইসেন্স](../LICENSE) প্রযোজ্য। আগের CC0 উৎসর্গ মূল আলাদা ম্যাপ ও তাদের নিয়মের জন্য বহাল। [অভিন্ন প্রকাশনা ও প্রাপ্যতা](../results/shared-publication-v1/REPORT.md)।

| অংশ | লাইসেন্স |
| --- | --- |
| `src/`, `tests/`, `site/scripts/` ও ওয়ার্কফ্লোর কোড | [MIT](../LICENSE) |
| কালা ঝড় ও কালা গতির মূল লেআউট-ম্যাপ ও স্বরবর্ণ লেখার মূল নিয়ম (`results/kala-keyboards/`) | [CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/) |
| ডকুমেন্টেশন (`docs/`, `results/*/REPORT.md`) | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) |
| `reference/colemak-dh-resources/`-এ প্রকাশিত Colemak Mod-DH রিসোর্স | CC0, `colemakmods/mod-dh` প্রকল্প থেকে |
| মূল কোড থেকে নেওয়া Dvorak-7 ও Engram অংশ, মূল কোডের কপি ও মাপকাঠির সারণি (`data/evaluators/mechanics-v1/`) | Arno Klein, [MIT](../data/evaluators/mechanics-v1/LICENSE) |
| ওয়েবসাইটের ফন্ট (Inter, Noto Sans Bengali) | SIL Open Font License; নোটিশ `site/public/licenses/`-এ |
| তুলনার লেআউটের কি-ম্যাপ (`data/baselines/layouts/`, `data/kala/`-এ UniJoy ও Bijoy) | নির্মাতাদের শর্ত; শুধু তুলনার ডেটা |
| ban-dataset-collection-এর টেক্সট | এই রিপোজিটরিতে নেই; দেখুন [DATASETS.md](DATASETS.md) |

## লেআউট-ম্যাপ

কালার মূল কালা ঝড় ও কালা গতি লেআউট-ম্যাপ পাবলিক ডোমেইনে উৎসর্গ করা। অনুমতি বা রয়্যালটি ছাড়াই এগুলো ব্যবহার করুন, বদলান, শেয়ার করুন, বা বাণিজ্যিকভাবেও অন্য কিবোর্ড বাস্তবায়নে অন্তর্ভুক্ত করুন। উৎসর্গের আওতায় আছে মূল কি ও স্তরের ম্যাপ এবং স্বরবর্ণ লেখার মূল নিয়ম। কালা অ্যাপের কোড, অভিধান, ডেটাসেট, তৃতীয় পক্ষের ইঞ্জিন, তুলনার লেআউট ও ব্র্যান্ড চিহ্ন এর আওতায় নয়। মালিক ২০২৬ সালের ১২ অক্টোবর উৎসর্গ অনুমোদন করেছেন; একই বক্তব্য [কালার নির্দেশিকার সঙ্গে](https://github.com/robispider/kala-releases/blob/main/docs/reference/original-layout-license.md) প্রকাশিত।

## মূল বিশ্লেষক

Phase 1 যে Colemak Mod-DH বিশ্লেষকের সোর্স আবার তৈরি করেছে তার কোনো লাইসেন্স নেই, তাই সেটি এই রিপোজিটরির অংশ নয়। `python -m bangla_dh fetch-upstream` শুধু ঐচ্ছিক মডেল-পুনরুৎপাদন ধাপের জন্য সেটি একটি নির্দিষ্ট কমিটে `reference/upstream/`-এ নামায়, যা Git উপেক্ষা করে।
