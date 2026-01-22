<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Quickstart Manual Test Procedure

**Feature**: GitHub Pages Documentation Website
**Success Criterion**: SC-001 - New users can install Lynx and create their first diagram following the quickstart guide in under 10 minutes

## Purpose

This document provides a manual testing procedure to validate the quickstart guide meets SC-001 (user completes onboarding in <10 minutes). The procedure simulates a first-time user experience from a fresh environment.

## Prerequisites

- **Test Environment**: Fresh Python 3.11+ environment (use `python -m venv test_env` or Docker container)
- **Network**: Internet connection (for pip install)
- **Browser**: Modern browser (Chrome, Firefox, Safari) for viewing documentation
- **Tester**: Person unfamiliar with Lynx (ideally external user, not dev team)

## Test Procedure

### Setup (Pre-Test)

1. **Prepare fresh environment**:
   ```bash
   # Create isolated test environment
   python3.11 -m venv test_lynx_env
   source test_lynx_env/bin/activate  # On Windows: test_lynx_env\Scripts\activate

   # Verify clean state
   pip list  # Should show only pip, setuptools
   ```

2. **Start timer**: Begin timing when tester opens documentation site

3. **Documentation URL**: Provide tester with GitHub Pages URL only (no additional guidance)

### Test Scenario (Timed)

**Step 1: Navigate to Documentation (Expected: <1 min)**

- Tester opens documentation landing page
- Tester identifies "Quickstart" link
- Tester clicks through to quickstart guide

**Expected Result**:
- User reaches quickstart guide without confusion
- Navigation is intuitive (grid cards or clear sidebar)

---

**Step 2: Install Lynx (Expected: 2-3 min)**

- Tester reads installation instructions
- Tester copies installation command
- Tester runs: `pip install lynx-nb` (or appropriate command from docs)
- Tester verifies installation: `python -c "import lynx; print(lynx.__version__)"`

**Expected Result**:
- Installation completes without errors
- Lynx version prints correctly
- Instructions are clear enough that tester doesn't need to ask for help

---

**Step 3: Create First Diagram - Programmatic (Expected: 3-4 min)**

Tester follows quickstart code examples to create a simple feedback control diagram:

```python
import lynx

# Create diagram
diagram = lynx.Diagram()

# Add blocks
diagram.add_block('io_marker', 'r', marker_type='input', label='r', position={'x': 0, 'y': 0})
diagram.add_block('gain', 'controller', K=5.0, position={'x': 100, 'y': 0})
diagram.add_block('transfer_function', 'plant',
                  numerator=[2.0], denominator=[1.0, 3.0],
                  position={'x': 200, 'y': 0})
diagram.add_block('io_marker', 'y', marker_type='output', label='y', position={'x': 300, 'y': 0})

# Add connections
diagram.add_connection('c1', 'r', 'out', 'controller', 'in')
diagram.add_connection('c2', 'controller', 'out', 'plant', 'in')
diagram.add_connection('c3', 'plant', 'out', 'y', 'in')

# Save diagram
diagram.save('my_first_diagram.json')
print("Diagram saved successfully!")
```

**Expected Result**:
- Code executes without errors
- `my_first_diagram.json` created in working directory
- Tester understands what code does (comments are clear)

---

**Step 4: Launch Interactive Widget (Expected: 2-3 min)**

**Note**: This step requires Jupyter environment. If tester doesn't have Jupyter:

```bash
pip install jupyter
```

Then in a Jupyter notebook:

```python
import lynx

diagram = lynx.Diagram.load('my_first_diagram.json')
lynx.edit(diagram)  # Launches interactive widget
```

**Expected Result**:
- Widget launches and displays diagram visually
- Tester can see blocks and connections
- Interactive features work (pan, zoom)

**Alternative (If Jupyter not covered in quickstart)**:
- If quickstart focuses only on programmatic API without widget, Step 4 can be optional
- Validate that programmatic workflow alone takes <10 minutes

---

**Step 5: Verify Success (Expected: <1 min)**

- Tester confirms diagram is saved
- Tester understands basic Lynx concepts (diagrams, blocks, connections)
- Tester sees "Next Steps" section linking to examples or API reference

**Expected Result**:
- Tester feels they've accomplished something meaningful
- Clear guidance on what to explore next

---

### Stop Timer

**Total Time**: Record elapsed time from opening documentation to completing Step 5.

---

## Success Criteria Validation

**Pass**: Total time ≤ 10 minutes AND tester completed all steps without external help

**Partial Pass**: Time >10 min OR tester needed clarification on 1-2 minor points
- **Action**: Identify confusing instructions, update quickstart guide

**Fail**: Time significantly >10 min (e.g., >15 min) OR tester got stuck and couldn't proceed
- **Action**: Major revision needed - unclear instructions, missing steps, or poor UX

---

## Post-Test Debrief

Ask tester these questions:

1. **Clarity**: Were the instructions clear? Which steps were confusing?
2. **Completeness**: Was any information missing?
3. **Confidence**: Do you feel you understand how to use Lynx after this?
4. **Next Steps**: Was it clear what to do next (explore examples, read API docs)?
5. **Overall Experience**: On a scale of 1-10, how smooth was the onboarding?

Document feedback for iterative improvement.

---

## Variations for Different User Personas

### Variation 1: Jupyter-First User
- User prefers interactive workflow over programmatic
- Quickstart should offer both paths (programmatic + interactive)
- Expected time: Same (≤10 min)

### Variation 2: Advanced Python User
- May skip verification steps
- Expected time: Faster (7-8 min)
- Still validate quickstart is clear for beginners

### Variation 3: Control Theory Student
- May need more context on control system terminology
- Expected time: Slightly longer (9-10 min) if extra explanations needed
- Validate terminology is accessible

---

## Automated Validation (CI)

While the timed user test is manual, parts can be automated:

```bash
# CI script to validate quickstart code examples execute
cd docs/source/getting-started
python -m doctest quickstart.md  # If code blocks are doctests

# Or extract and run code blocks
extract_code_blocks quickstart.md > test_quickstart.py
python test_quickstart.py  # Should complete without errors
```

**Note**: Automated validation ensures code correctness but doesn't replace manual user testing for UX validation.

---

## Frequency

**Run manual test**:
- Before initial documentation launch (3+ testers)
- After major quickstart revisions (1-2 testers)
- Quarterly with new external testers (to catch documentation drift)

**Update procedure**:
- If quickstart content changes significantly, update this procedure to match
- Keep expected times updated based on actual user data

---

## Appendix: Sample Test Log Template

```markdown
## Test Session

**Date**: YYYY-MM-DD
**Tester**: [Name or Anonymous ID]
**Environment**: [OS, Python version]
**Timer Start**: [HH:MM:SS]

### Step-by-Step Log

**Step 1 - Navigate to Documentation**
- Start: [HH:MM:SS]
- End: [HH:MM:SS]
- Duration: [MM:SS]
- Issues: [None / Describe issue]

**Step 2 - Install Lynx**
- Start: [HH:MM:SS]
- End: [HH:MM:SS]
- Duration: [MM:SS]
- Issues: [None / Describe issue]

**Step 3 - Create First Diagram**
- Start: [HH:MM:SS]
- End: [HH:MM:SS]
- Duration: [MM:SS]
- Issues: [None / Describe issue]

**Step 4 - Launch Widget (if applicable)**
- Start: [HH:MM:SS]
- End: [HH:MM:SS]
- Duration: [MM:SS]
- Issues: [None / Describe issue]

**Step 5 - Verify Success**
- Start: [HH:MM:SS]
- End: [HH:MM:SS]
- Duration: [MM:SS]
- Issues: [None / Describe issue]

### Summary

**Total Time**: [MM:SS]
**Pass/Fail**: [Pass / Partial Pass / Fail]
**Key Issues**: [List major blockers or confusions]
**Tester Feedback**: [Open-ended comments]

### Recommendations

- [Actionable changes to quickstart guide]
- [Suggested improvements]
```

---

## Notes

- This procedure validates SC-001 specifically. Other success criteria (SC-002 through SC-008) have separate validation procedures (see plan.md Testing Strategy section).
- Focus on first-time user experience - don't optimize for power users who already know Lynx.
- Realistic timing includes reading instructions, not just code execution time.
- If tester completes in <5 min, they may have skipped reading - verify they understood the material.

---

**End of Quickstart Test Procedure**
