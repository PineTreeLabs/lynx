# Lynx

**Lynx** is a minimal, lightweight Jupyter widget for editing block diagrams. Design, visualize, and analyze linear SISO control systems using an interactive Jupyter workflow and seamless python-control integration.

- **Classic Block Diagrams**: Drag-and-drop interface for creating control system schematics
- **Interactive Jupyter Widget**: Real-time visualization and editing directly in Jupyter notebooks
- **Python-Control Export**: Export diagrams to python-control objects for analysis and simulation
- **LaTeX Rendering**: Clean mathematical notation for transfer functions, state-space matrices, and custom block content


<div class="hero-video-container">
  <video autoplay loop muted playsinline class="hero-video">
    <source src="_static/landing-demo.webm" type="video/webm">
    Your browser does not support the video tag.
  </video>
  <p class="hero-caption">Jupyter-based control systems design</p>
</div>


Lynx is designed to support seamless Jupyter-based linear, single-input-single-output control systems workflows.
It is **not** a full-fledged modeling and simulation tool and does not support nonlinearities, discrete-time systems, or even hierarchical subsystems (at least for now).
It **does** support integration with ecosystem tools for design, analysis, and simulation, in particular the [Python Control Systems Library](https://python-control.readthedocs.io/en/0.10.2/) and [Archimedes](https://pinetreelabs.github.io/archimedes/).


::::{grid} 1 2 2 3
:gutter: 3

:::{grid-item-card} 🚀 Quickstart
:link: quickstart
:link-type: doc

Get started in under 5 minutes. Install Lynx, create your first diagram, and run a feedback control simulation.
:::

:::{grid-item-card} 📚 Examples
:link: examples/index
:link-type: doc

Learn through working Jupyter notebooks covering feedback control, PID tuning, and state-space design.
:::

:::{grid-item-card} 📖 API Reference
:link: api/index
:link-type: doc

Complete API documentation with method signatures, parameters, and code examples.
:::

::::


## Installation

The recommended way to install Lynx is via PyPI:

```bash
pip install lynx-nb
python -c "import lynx; print(lynx.__version__)"
```

If you plan to use the interactive widget in Jupyter notebooks (which is the whole point), ensure you have Jupyter (or JupyterLab) installed:

```bash
pip install jupyter
```


```{toctree}
:maxdepth: 2
:caption: Contents
:hidden:

quickstart
concepts
examples/index
api/index
```
