# Typing styles and credit

**Kala Goti** and **Kala Jhor** have separate published key maps and distinct native typing rules. A typing convention and a key arrangement are different contributions: this project searched the positions while building on established Bangla input methods. B01 identifies the historical shared-map experiment.

## Goti: the established modern fixed-layout convention

The first Goti arrangement used the UniJoy-style grammar, and the shared arrangement keeps it. **Credit goes to Ekushey's UniJoy contributors and to Avro/OmicronLab, including Mehdi Hasan Khan and the Avro team, for the established input-method lineage we build on.** Ekushey publishes UniJoy as its Unicode keyboard input system; Avro's fixed-layout manual documents Modern Typing Style. [Ekushey UniJoy](https://ekushey.org/keyboard-layout/ekusheyr-shadhinota-unijoy-layout/), [Avro fixed-layout manual](https://www.omicronlab.com/download/pdf/Bangla%20Typing%20with%20Fixed%20Keyboard%20Layouts.pdf#page=3), [Mehdi Hasan Khan's account](https://mehdikhan.dev/about/).

Goti's core recipe is consonant followed by vowel sign: ক + ো = কো, using J then R on published Goti. A full vowel uses hasant followed by the sign: ্ + ো = ও; অ has its own key. The new arrangement changes the physical positions, not the origin of these conventions. Goti is our name for this style in Kala; we do not claim to have invented modern vowel entry. [Map and examples](LAYOUTS.md).

## Visual entry and logical entry

Classic Bijoy/ANSI workflows used visual-order entry, including ে + ক + া for কো. Modern fixed-layout entry uses ক + ো, with one assigned key for the whole vowel sign. This is a change in entry convention, not merely a new location for the independent letter ও. [Avro's comparison of old and modern styles](https://www.omicronlab.com/download/pdf/Bangla%20Typing%20with%20Fixed%20Keyboard%20Layouts.pdf#page=9).

Unicode text is stored in logical character order; rendering handles the displayed shapes. This is not a claim that computers understand spoken pronunciation or that every Unicode keyboard must accept the same keystroke order. An input engine can convert visual-order typing into Unicode too—Avro documents both input styles. [Unicode's Indic-script FAQ](https://www.unicode.org/faq/indic.html), [Avro's style overview](https://www.omicronlab.com/download/pdf/Bangla%20Typing%20with%20Fixed%20Keyboard%20Layouts.pdf#page=3).

This history concerns fixed-layout typing, not a numerical comparison with Avro Phonetic. We credit the documented implementations without asserting who first invented every underlying idea. Avro is an input application with both fixed-layout and phonetic modes; the modern fixed-layout convention should not be conflated with Latin-letter transliteration.

## Jhor: context vowels with a specified repeat rule

Jhor gives a vowel sign after a consonant and a full vowel elsewhere. After a consonant, repeating the same vowel key rewrites the run in pairs from its end: one press gives a sign, two give a full vowel, three give sign + full vowel. There is no timer. Elsewhere each press adds another full vowel. This complete rule is documented and tested in this project. [Exact rules and examples](LAYOUTS.md).

**Context-sensitive vowel entry already has prior art in Avro.** Its optional Automatic Vowel Forming produces full vowels in several contexts without a hasant. Credit this existing idea too. [Avro feature description](https://www.omicronlab.com/avro-keyboard.html), [manual, vowel-forming section](https://www.omicronlab.com/download/pdf/Bangla%20Typing%20with%20Fixed%20Keyboard%20Layouts.pdf#page=7).

OmicronLab's version history records Automatic Vowel Forming in Avro 1.1.2, released on 15 September 2003. This is documented prior implementation, not a claim of worldwide invention priority. [Avro version history](https://www.omicronlab.com/avro-keyboard-version-history.html).

A focused primary-source review on 29 October 2026 did not locate an identical specification of Jhor's entire timing-free, pair-from-the-end repeat recipe in the cited documentation. That is a limited finding, not proof of novelty or invention priority. We describe it as the project's specified Jhor rule, not the first context-aware Bangla typing method. Earlier documentation of an equivalent complete rule would warrant updating this credit.

## What this research contributes

The contribution is the reproducible search and evaluation of one shared symbol arrangement under both explicitly specified styles, with the published costs and limitations. **The four-billion run searched placements; it did not invent the established modern entry convention.** The current publication changes neither Goti's nor Jhor's frozen grammar. [How the arrangement was found](HOW_WE_FOUND_THEM.md), [why share one arrangement](SHARED_LAYOUT.md).
