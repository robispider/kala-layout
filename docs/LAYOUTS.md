# One shared map, Goti and Jhor typing styles

**B01 is the provisional shared arrangement.** Goti (A) and Jhor (D) are typing styles on this same map. Changing style changes vowel behavior, never symbol positions. Read [why we are transitioning](SHARED_LAYOUT.md) and the [publication report](../results/shared-publication-v1/REPORT.md).

## The shared arrangement

Each pair shows Shift above base. Vowel signs identify the keys; the style determines their output. Hasant is S; অ is Shift+D.

| | Q | W | E | R | T | Y | U | I | O | P |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Shift | ঢ় | ৌ | ৃ | ৎ | ঢ | ঘ | ণ | ং | ফ | ঠ |
| base | ী | হ | ু | য | ট | শ | স | প | ম | দ |

| | A | S | D | F | G | H | J | K | L |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Shift | ঁ | ূ | অ | ষ | ঝ | ড | থ | ভ | চ |
| base | ি | ্ | া | র | গ | জ | ক | ে | ব |

| | Z | X | C | V | B | N | M |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Shift | ঃ | ৈ | ড় | ঙ | ঞ | খ | ধ |
| base | । | ো | ন | ল | ছ | য় | ত |

Bangla digits remain on the number row, US punctuation stays fixed. Normal and Shift are the two modeled layers. ZWNJ, ZWJ, ঽ, ॥, — and ৳ have no modeled key. ড়, ঢ় and য় use canonical NFC units even when the font draws a single letter.

## Goti style (A)

Type a sign after a consonant: ক + ি = কি. For a full vowel, type hasant and then its sign: ্ + ি = ই. অ has its own key. Hasant also joins consonants: ক + ্ + ষ = ক্ষ.

| Text | Keys | Label presses |
| --- | --- | --- |
| আমি | S D O A | ্ া ম ি |
| কী | J Q | ক ী |
| বই | L S A | ব ্ ি |
| এবং | S K L Shift+I | ্ ে ব ং |
| তিনিই | M A C A S A | ত ি ন ি ্ ি |
| আকাশ | S D J D Y | ্ া ক া শ |

## Jhor style (D)

After a consonant, the vowel key gives its sign; elsewhere it gives the full vowel. At word start ি = ই. After a consonant, two presses of the same vowel key give the full vowel: ব + ি + ি = বই. A run pairs from its end: three presses give sign + full vowel, as in তিনিই. Elsewhere every press gives another full vowel. There is no timing rule. অ and hasant retain the same positions as in Goti.

| Text | Keys | Label presses |
| --- | --- | --- |
| আমি | D O A | া ম ি |
| কী | J Q | ক ী |
| বই | L A A | ব ি ি |
| এবং | K L Shift+I | ে ব ং |
| তিনিই | M A C A A A | ত ি ন ি ি ি |
| আকাশ | D J D Y | া ক া শ |

## Availability and transition

These are research exports, not an installed application update: [Goti-style export](../results/shared-publication-v1/kala-shared-goti.json) and [Jhor-style export](../results/shared-publication-v1/kala-shared-jhor.json). They have identical key maps and different style metadata. Goti uses hasant/sign combinations; Jhor requires a compatible context-vowel engine. Confirm support before importing. An existing Kala installation or its Learn exercises may still use the original arrangements.

[Kala for Windows](https://robispider.github.io/kala-releases/en/), [installation](https://robispider.github.io/kala-releases/en/guide/installation/) and [learning guide](https://robispider.github.io/kala-releases/en/guide/learning/) describe the companion app. Check its [release status](https://robispider.github.io/kala-releases/en/release-status/) for actual availability. This research release changes no application or practice lessons.

Existing users can keep the [original separate arrangements](../results/kala-keyboards/README.md). B01 relocates 43 Goti and 39 Jhor symbols; see [every change](../results/shared-publication-v1/RELOCATIONS.md). Scores model effort and movement; learning time, speed and comfort are not measured. B01 is a provisional compromise, with no transferred optimality certificate.
