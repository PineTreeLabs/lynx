# Diagram Templates

While every control system is unique, there are several common architectures that many systems will either share or be minor variations of.

To simplify construction of these diagrams, Lynx provides pre-built "template" systems that you can instantiate and edit.
In many cases, you may only need to edit the block parameters, block/signal labels, LaTeX content to make the diagram consistent with your own system.

For an example using templates to quickly construct a system, see {doc}`../examples/cruise-control`.

## Available templates

**Open-loop (transfer function plant)** (`"open_loop_tf"`)

```{image} _static/open-loop-tf-light.png
:class: only-light
```

```{image} _static/open-loop-tf-dark.png
:class: only-dark
```

**Open-loop (state-space plant)** (`"open_loop_ss"`)

```{image} _static/open-loop-ss-light.png
:class: only-light
```

```{image} _static/open-loop-ss-dark.png
:class: only-dark
```

**Feedback (transfer function plant)** (`"feedback_tf"`)

```{image} _static/feedback-tf-light.png
:class: only-light
```

```{image} _static/feedback-tf-dark.png
:class: only-dark
```

**Feedback (state space plant)** (`"feedback_ss"`)

```{image} _static/feedback-ss-light.png
:class: only-light
```

```{image} _static/feedback-ss-dark.png
:class: only-dark
```

**Feedforward (transfer function plant)** (`"feedforward_tf"`)

```{image} _static/feedforward-tf-light.png
:class: only-light
```

```{image} _static/feedforward-tf-dark.png
:class: only-dark
```

**Feedforward (state space plant)** (`"feedforward_ss"`)

```{image} _static/feedforward-ss-light.png
:class: only-light
```

```{image} _static/feedforward-ss-dark.png
:class: only-dark
```

**Feedback + filtering** (`"filtered"`)

```{image} _static/filtered-light.png
:class: only-light
```

```{image} _static/filtered-dark.png
:class: only-dark
```

**Cascaded control** (`"cascaded"`)

```{image} _static/cascaded-light.png
:class: only-light
```

```{image} _static/cascaded-dark.png
:class: only-dark
```