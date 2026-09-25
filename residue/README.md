# Residue

A 30-second animation. Open `residue.html` in a browser (click to replay), or watch `residue.mp4`.

The page draws its own source code. Every cell starts as random glyphs. Then the "temperature" falls:
whitespace settles first, so you see the outline of the code before you can read it. After that the
characters settle one by one, in bit-reversed order so they fill in evenly everywhere. Faint threads
show attention: they connect random cells while it is hot, then each settling glyph links to the last
place that same character appeared. At the end one `?` never settles.
