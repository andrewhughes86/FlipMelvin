# FlipMelvin — Autodesk Fusion Automation Script
**Version:** 1.0  
**Author:** Andy Hughes  

---

## Overview

`FlipMelvin.py` is an Autodesk Fusion script that automates the process of **duplicating and reorienting manufacturing setups** for CAM operations.  
It ensures that the workspace is correctly set, finds or creates World Coordinate System (WCS) points, and flips the machining orientation to create a mirrored setup (“Melvin Flipped”).

---

## What It Does

1. **Switches to the Design Workspace** to ensure geometry access.  
2. **Locates WCS points:**
   - `Melvin WCS`
   - `Melvin Flipped WCS`
   - Automatically creates missing points if necessary.
3. **Determines origin points** based on “Stud” and “Track” bodies.
4. **Copies or updates the “Melvin” setup**:
   - If current WCS ≠ “Melvin Flipped WCS” → flips it.
   - Otherwise → restores it to default.
5. **Updates the Perimeter toolpath** to reference the correct WCS.
6. **Regenerates the toolpath automatically.**
7. **Displays a detailed summary** of all changes made.

---

## Script Structure

| Function | Description |
|-----------|--------------|
| `run(context)` | Entry point — runs the script, manages summary messages. |
| `addMessage(msg)` | Adds messages to display in a final summary dialog. |
| `in_cm(x)` | Converts inches to centimeters. |
| `getPoints()` | Finds or creates WCS construction points for Melvin setups. |
| `idOrigin()` | Identifies min/max bounds for Studs and Tracks. |
| `createOrigin()` | Creates a new construction point for `Melvin Flipped WCS`. |
| `copySetup()` | Copies and flips the Manufacturing setup, regenerates toolpaths. |
| `scriptSummary()` | Displays all collected messages at the end of execution. |

---

## Usage

1. **Open Autodesk Fusion.**
2. Load your **CAM Design** that contains a setup named `"Melvin"`.
3. Ensure the following construction points exist (or will be created):
   - `Melvin WCS`
   - `Melvin Flipped WCS`
4. Go to **Scripts and Add-Ins** → **My Scripts**.
5. Select and **Run** `FlipMelvin.py`.
6. Check the **Summary dialog** for confirmation and WCS flip results.

---

## Workflow Example

| Step | Description |
|------|--------------|
| 1️⃣ | Script checks for `"Melvin"` setup |
| 2️⃣ | Verifies WCS origin (creates if missing) |
| 3️⃣ | Flips WCS to `"Melvin Flipped WCS"` |
| 4️⃣ | Updates Perimeter operation entry point |
| 5️⃣ | Regenerates toolpath |
| ✅ | Displays summary of completed actions |