# indicator-tablet-mode
### Ubuntu Unity indicator to change between different device modes

This is a simple and device-agnostic indicator. It should work on normal Ubuntu-like systems (at least 14.04+) with `onboard` installed. Customize onboard settings to your likings (show when editing text, dock to screen border, resize workspace). For more device-specific adjustments, you can find alternative scripts ([Lenovo Yoga 3](https://github.com/philipphangg/screenrotation), [Thinkpad](https://github.com/johanneswilm/thinkpad-yoga-14-s3-scripts)...).

 - ![Laptop](https://cdn.rawgit.com/Aerilius/indicator-tablet-mode/master/indicator-tablet-mode/light/indicator-tablet-mode-laptop.svg?raw=true) **Laptop mode**: physical keyboard, touchpad
 
 - ![Tablet](https://cdn.rawgit.com/Aerilius/indicator-tablet-mode/master/indicator-tablet-mode/light/indicator-tablet-mode-tablet.svg?raw=true) **Tablet mode**: onscreen keyboard; physical keyboard and touchpad disabled
 
 - **Rotations** (both touch input and display output)
 
### Installation
Unzip to `~/.local/bin/`  
Open "Startup aplications" and add `python ~/.local/bin/indicator-tablet-mode/indicator-tablet-mode.py`
