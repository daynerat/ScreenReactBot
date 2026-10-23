# Screen Reaction Bot — UI Styling Fix Notes

## Why the Gray Background Appeared Behind the Text

In Tkinter's `ttk` widget engine, themes like `clam` have a default state mapping (`style.map`) that hardcodes a light gray background (`#dcdad5` / `(220, 218, 213)`) for radio buttons, checkboxes, labels, and buttons under the `!disabled` (normal) state.

Even when `style.configure("TRadiobutton", background=...)` is set, Tkinter's internal state map takes strict precedence, causing Tkinter to draw solid gray bounding rectangles behind every label and radio button option on top of dark card surfaces.

## What Was Fixed in Version 10

1. **Full State-Map Override**:
   * `TRadiobutton` and `TCheckbutton` now override every possible widget state (`pressed`, `active`, `selected`, `disabled`, and `!disabled`) directly to the card background (`bg_card`).
   * The gray rectangle is eliminated entirely; text and radio indicators now blend 100% seamlessly into the dark card surface.

2. **Card Sub-Frames (`Card.TFrame`)**:
   * All internal layout rows inside card containers now use a dedicated `Card.TFrame` style matching the parent card background, preventing mismatched container backgrounds.

3. **Flat Themed Buttons & Input Fields**:
   * Secondary buttons (like `✂ Snip Destination Target` and `🎯 Pick (3s)`) and text entry boxes (`X: 960`, `Y: 540`) now use flat dark entry surfaces (`bg_entry`) with 1px borders instead of default gray/white Win32 bevels, highlighting with the theme's accent color on hover and click.
