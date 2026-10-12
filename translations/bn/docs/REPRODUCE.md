# নিজে চালিয়ে দেখুন

গবেষণাটি তিনটি গভীরতায় আবার চালানো যায়। প্রতিটি গভীরতা নিজেকে যাচাই করে `PASS` বলে, অথবা কোথায় ভিন্নতা তা দেখায়। সবকিছু Python 3.10 বা নতুন সংস্করণ ও স্ট্যান্ডার্ড লাইব্রেরিতে চলে; OR-Tools লাগে শুধু ঐচ্ছিক প্রমাণের জন্য।

PowerShell-এ নিচের কমান্ডের আগে `$env:PYTHONPATH = "src"` দিন, অথবা একবার `pip install -e .` চালিয়ে `python -m bangla_dh`-এর জায়গায় `bangla-dh` লিখুন। কমান্ডগুলো রিপোজিটরির ফোল্ডার থেকে চালান। একাধিক প্রসেসের কমান্ড কমান্ড লাইন থেকে শুরু করতে হয়, ইন্টারঅ্যাক্টিভ Python সেশনে টাইপ করে নয়।

## কোন গভীরতা আপনার দরকার

| গভীরতা | কী করবেন | ডাউনলোড | সময় | কী জানবেন |
| --- | --- | --- | --- | --- |
| 1. সার্চ | লেআউট সার্চ চালিয়ে কালার সঙ্গে তুলনা করুন | নেই | কয়েক মিনিট (`--seeds 32`) থেকে প্রায় 25 মিনিট, 32 কোরে (`--reproduce`) | স্বাধীন সার্চ কি কালা ঝড় ও কালা গতিই পায়, নাকি ভিন্ন বা আরও ভালো কিছু? |
| 2. সারণি আবার তৈরি | প্রকাশ্য টেক্সট নামিয়ে প্রতিটি কি-স্ট্রোক সারণি আবার বানান | প্রায় 1 GB | ডাউনলোডের পর প্রায় 30 মিনিট | টেক্সট কি সার্চে ব্যবহৃত সংখ্যাগুলোই হুবহু দেয়? |
| 3. সবকিছু | সব ধাপ ক্রমে আবার চালান | প্রায় 1 GB | ডাউনলোডের পর প্রায় 1.5 ঘণ্টা, 32 কোরে | টেক্সট থেকে লেআউট ফাইল পর্যন্ত পুরো ধারা কি আবার তৈরি হয়? |

## গভীরতা ১: সার্চ চালান

সার্চের দরকারি কি-স্ট্রোক সারণি `results/`-এ কমিট করা আছে, তাই কোনো ডাউনলোড লাগে না।

```bash
PYTHONPATH=src python -m bangla_dh generate-layout --style D --seeds 32
PYTHONPATH=src python -m bangla_dh generate-layout --style A --seeds 32
```

32 সিডের একটি সার্চ 8 কোরে কয়েক মিনিট নেয়। এটি এলোমেলো লেআউট থেকে শুরু করে, নিজের সেরা লেআউট ও প্রকাশিত লেআউট পাশাপাশি দেখায় (ট্রেনিং J1 ও তিনটি আলাদা রাখা J1), এবং বলে একই লেআউট পাওয়া গেল, ভিন্ন ও খারাপ কিছু, নাকি ভালো কিছু। ফাইলগুলো লেখা হয় `work/generate-<style>/`-এ, প্রকাশিত ফলের ওপর কখনো নয়। `D-layout.json` বা `A-layout.json` ফাইল [চ্যালেঞ্জ স্কোরার](CHALLENGE.md) দিয়ে স্কোর করা যায়।

অপশন:

* `--seeds N`: স্বতন্ত্র রানের সংখ্যা। প্রকাশিত লেআউটে পৌঁছানো গেছে 512টি শুরুর মধ্যে ঝড়ের 24টি ও গতির 36টি থেকে, তাই 32 সিডে এগুলো কখনো কখনোই পাওয়া যায়।
* `--first-seed N`: অন্য শুরু খুঁজতে সিডগুলো সরান।
* `--workers N`: কতগুলো প্রসেস ব্যবহার হবে।
* `--weights bnwiki/train=0.5 newspaper/train=0.5`: ট্রেনিং মিশ্রণ বদলান, যেমন শুধু উইকিপিডিয়ার জন্য `bnwiki/train=1`।

**প্রকাশিত** রান হুবহু আবার চালাতে (512 সিড, প্রকাশিত সিড-পরিসর, এবং আগের উইকিপিডিয়া ও সংবাদের লেআউট থেকে পালিশ):

```bash
PYTHONPATH=src python -m bangla_dh generate-layout --style D --reproduce --workers 28
```

32 কোরে এতে প্রায় 25 মিনিট লাগে; মিলে গেলে `the same layout as Kala Jhor` ছাপে, আর এক্সিট কোড 0 হয় শুধু তখনই।

## গভীরতা ২: টেক্সট থেকে সারণি আবার বানান

```bash
PYTHONPATH=src python -m bangla_dh fetch-data
PYTHONPATH=src python -m bangla_dh prepare-data
PYTHONPATH=src python -m bangla_dh build-inventory
PYTHONPATH=src python -m bangla_dh build-corpus
PYTHONPATH=src python -m bangla_dh compute-frequency
PYTHONPATH=src python -m bangla_dh build-problem
PYTHONPATH=src python -m bangla_dh style-frequency
PYTHONPATH=src python -m bangla_dh crosscheck-build
PYTHONPATH=src python -m bangla_dh check-results --group tables
```

শেষ কমান্ড আবার তৈরি প্রতিটি ফ্রিকোয়েন্সি ও কি-স্ট্রোক সারণি প্রকাশিতটির সঙ্গে মেলায়। ডেটার কমান্ডগুলো [DATASETS.md](DATASETS.md)-এ বর্ণিত।

## গভীরতা ৩: প্রতিটি ধাপ

গভীরতা ২-এর পর:

```bash
PYTHONPATH=src python -m bangla_dh evaluate-phase2
PYTHONPATH=src python -m bangla_dh optimize
PYTHONPATH=src python -m bangla_dh evaluate-phase3
PYTHONPATH=src python -m bangla_dh crosscheck-optimize
PYTHONPATH=src python -m bangla_dh evaluate-crosscheck
PYTHONPATH=src python -m bangla_dh mix-optimize --styles A D --seeds 512 --workers 28
PYTHONPATH=src python -m bangla_dh kala-export
PYTHONPATH=src python -m bangla_dh challenge-kit
PYTHONPATH=src python -m bangla_dh check-results
```

| ধাপ | কমান্ড | কী করে | শেষ হয় |
| --- | --- | --- | --- |
| Phase 2 রিপোর্ট | `evaluate-phase2` | স্কোরারকে মূল বিশ্লেষকের পোর্ট ও স্বাধীন যাচাইকারীর সঙ্গে মেলায়, 454,000 শব্দ ঘুরিয়ে মেলায়, UniJoy স্কোর করে | তিনটি `PASS` লাইনে |
| Phase 3 সার্চ | `optimize` | উইকিপিডিয়ায় চার স্টাইলের প্রতিটির জন্য 64 সিড | `check-results --group "phase3 search"` |
| Phase 3 রিপোর্ট | `evaluate-phase3` | পৃথক মূল্যায়নের স্কোর, তুলনার লেআউট, স্বাধীন যাচাই | সব যাচাই `PASS` |
| সংবাদের সার্চ | `crosscheck-optimize` | সংবাদপত্রের টেক্সটে একই সার্চ | `check-results --group "news search"` |
| সংবাদের রিপোর্ট | `evaluate-crosscheck` | তিনটি পৃথক টেক্সটে প্রতিটি তুলনার লেআউট স্কোর করে | সব যাচাই `PASS` |
| মিশ্র সার্চ | `mix-optimize` | উইকিপিডিয়া ও সংবাদপত্রের মিশ্রণে A ও D-র জন্য 512 সিড, তারপর পালিশ | একটি `PASS` লাইন |
| Kala ফাইল | `kala-export` | লেআউট ফাইল ও লিডারবোর্ড লেখে, Kala-র ইঞ্জিনের পোর্ট দিয়ে 500,000 শব্দ টাইপ করে | `Checks: PASS` |
| চ্যালেঞ্জ কিট | `challenge-kit` | একফাইলের স্কোরার বানায় এবং প্রমাণ করে এটি ইন্টিজার মডেলের সঙ্গে হুবহু সমান | বারোটি `PASS` লাইন |
| শেষ যাচাই | `check-results` | সব সারণি, সার্চ ও লেআউট ফাইল প্রকাশিতগুলোর সঙ্গে মেলায় | আটটি `PASS` গ্রুপ |

প্রতিটি ধাপ `results/`-এর নিজের ফোল্ডার নতুন করে লেখে (রিপোর্ট, ফল, এবং ইনপুট-আউটপুটের SHA-256সহ `run-manifest.json`)। কী বদলাল তা দেখতে `git diff` ব্যবহার করুন।

### ঐচ্ছিক: প্রমাণ ও মডেল যাচাই

```bash
pip install "ortools==9.14.6206"
PYTHONPATH=src python -m bangla_dh certify-lp
PYTHONPATH=src python -m bangla_dh certify
PYTHONPATH=src python -m bangla_dh sensitivity
PYTHONPATH=src python -m bangla_dh evaluate-phase4
PYTHONPATH=src python -m bangla_dh fetch-upstream
PYTHONPATH=src python -m bangla_dh reproduce-colemak
```

প্রথম চারটি [Phase 4](../results/phase4/REPORT.md)-এর প্রমাণিত নিম্নসীমা, নির্দিষ্ট পরিধির প্রমাণ ও প্যারামিটার-সংবেদনশীলতা যাচাই তৈরি করে এবং কয়েক ঘণ্টা নেয়। শেষ দুটি মূল Colemak Mod-DH বিশ্লেষক একটি নির্দিষ্ট কমিটে নামায় এবং এর প্রকাশিত ফল আবার তৈরি করে (প্রায় এক মিনিট); প্রতিটি যাচাই `PASS` দিয়ে শেষ হতে হবে।

## হুবহু মেলা এবং না মিললে কী করবেন

সার্চ নির্ধারিত: একই Python-এ একই সিড একই লেআউট দেয়। ফল আপনার প্ল্যাটফর্মের C লাইব্রেরির exp ফাংশনের ওপরও নির্ভর করে, তাই খুব ভিন্ন প্ল্যাটফর্মে অ্যানিলিং রান শেষ অঙ্কে সরে গিয়ে অন্য জায়গায় পৌঁছাতে পারে। চূড়ান্ত লেআউটগুলোতে অনেক স্বতন্ত্র সিড পৌঁছেছে, তাই ভিন্ন প্ল্যাটফর্মেও সেগুলো পাওয়া যায়। `check-results` যদি `DIFFERS` দেখায়:

1. ডাউনলোড নষ্ট হওয়ার সম্ভাবনা বাদ দিতে `verify-data` আবার চালান।
2. ইউনিট টেস্ট চালান: `PYTHONPATH=src python -m unittest discover -s tests` `OK` দিয়ে শেষ হওয়া উচিত।
3. আপনার অপারেটিং সিস্টেম, `python --version` এবং ভিন্ন ফাইলগুলোর নামসহ একটি ইস্যু খুলুন।

## ছোট কম্পিউটারে চালানো

যা সময় নেয় সবই সমান্তরাল। প্রসেস সীমিত করতে `--workers` ব্যবহার করুন, আর সার্চ ছোট করতে `mix-optimize --seeds 64` বা `generate-layout --seeds 16`। মনে রাখবেন, কম সিডে সেরা লেআউট কম বার পাওয়া যায়। জোড়া দেওয়া টেক্সটের জন্য 1 GB ডাউনলোডের ওপর প্রায় 4 GB ডিস্ক জায়গা লাগে।
