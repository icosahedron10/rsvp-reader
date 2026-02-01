# GOALS

## North star
- Enable a user to reliably read 2 to 3 times faster with equal or better comprehension using Rapid serial visual presentation.

## Current goals (tight scope)
1. Goal: Allow for the parsing of .pub files.
   - Acceptance criteria: Testing the accurate parsing of a test file that is created to test the edge cases with respect to characters and sequencing.
   - Notes: For lengthy files with multiple chapters, use regex to separate the text into its requisite parts (chapters, parts, articles, etc.) and ensure that we create a RSVP output for each.
   - Status: COMPLETE - Added .epub/.pub parsing using standard library (zipfile, xml). Added parse_chapters() method with regex detection for Chapter/Part/Article/Section headings. 11 new tests cover edge cases.
2. Goal: Refine UI and create a short demo .txt file that will exhibit the features of the app without requiring additional input.
   - Acceptance criteria: A basic, 500-1000 word file of any composition that can be used to exhibit a clutter-free UI and all of the funcionallity of our early app.
   - Notes:
   - Status: demo.txt created (652 words) - covers speed reading concepts, app features, and practical tips. UI refinements pending.
3. Goal: Chapter queueing for the .pub files after being broken down into chapter-like sections. Imagine that we can take several outputs and have them in a queue where when one ends, the next begins, you can rearrange the order of the files, add and remove with ease.
   - Acceptance criteria: Fully funcioning queue built into the UI with a Browse button. The user can select several outputs and add them to the queue. User can easily remove and rearrange files in the queue. Autoplay button near the queue to handle whether the next file should play following the end of the current file.
   - Notes:

## Constraints
- Never push to origin from this machine
- Commit often and with descriptive messages
- Keep diffs small and reviewable
- Prefer minimal dependencies
