# Examples Gallery

Learn Lynx through executable Jupyter notebook examples. Each example demonstrates key concepts and can be downloaded and run locally.

## Prerequisites

To run these examples, you'll need:

```bash
pip install lynx-nb numpy scipy matplotlib python-control jupyter
```

Basic understanding of:
- Control theory fundamentals (transfer functions, feedback, stability)
- Python and Jupyter notebooks
- Laplace transforms (helpful but not required)

## Example Notebooks

::::{grid} 1 2 2 3
:gutter: 3

:::{grid-item-card} Basic Feedback Control
:link: basic-feedback
:link-type: doc

Simple proportional feedback system with first-order plant. Learn diagram creation, export, and analysis.

**Topics**: Feedback loops, transfer functions, step response, Bode plots

**Level**: Beginner
:::

:::{grid-item-card} PI Controller Design
:link: pid-controller
:link-type: doc

PI controller tuning for a second-order system. Explore the effects of proportional and integral gains.

**Topics**: PI control, integral action, overshoot, steady-state error

**Level**: Intermediate
:::

:::{grid-item-card} State-Space Control
:link: state-feedback
:link-type: doc

State feedback design using pole placement for a double integrator.

**Topics**: State-space models, pole placement, MIMO systems

**Level**: Advanced
:::

::::

## Running Examples Locally

### Option 1: Download Individual Notebooks

Click the download button (↓) at the top of each example page to get the `.ipynb` file.

### Option 2: Clone Repository

```bash
git clone https://github.com/pinetreelabs/lynx.git
cd lynx/docs/source/examples
jupyter notebook
```

### Option 3: Run in Colab

Each notebook can be opened directly in Google Colab (no installation required).

## Learning Path

Recommended order for new users:

1. **Start here**: {doc}`basic-feedback` - Understand the basics
2. {doc}`pid-controller` - Learn PI controller design
3. {doc}`state-feedback` - Explore advanced state-space methods

## What's Next?

After working through the examples:

- {doc}`../api/index` - Explore the full API reference
- {doc}`../getting-started/quickstart` - Quick reference for creating diagrams
- Try modifying the examples to solve your own control problems!

## Example Code Structure

All examples follow this pattern:

1. **Import libraries**: lynx, python-control, numpy, matplotlib
2. **Create diagram**: Add blocks and connections
3. **Export system**: Convert to python-control objects
4. **Analyze**: Step response, Bode plots, stability analysis
5. **Visualize**: Plot results with matplotlib

```{toctree}
:maxdepth: 1
:hidden:

basic-feedback
pid-controller
state-feedback
```
