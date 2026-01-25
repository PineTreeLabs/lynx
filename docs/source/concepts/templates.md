# Diagram Templates

While every control system is unique, there are several common architectures that many systems will either share or be minor variations of.

To simplify construction of these diagrams, Lynx provides pre-built "template" systems that you can instantiate and edit.
In many cases, you may only need to edit the block parameters, block/signal labels, LaTeX content to make the diagram consistent with your own system.

For an example using templates to quickly construct a system, see {doc}`../examples/cruise-control`.

## Example

For a simple feedback controller with a transfer function plant model we can load the `"feedback_tf"` template:

```python
diagram = lynx.Diagram.from_template("feedback_tf")
```

```{image} _static/feedback-tf-light.png
:class: only-light
```

```{image} _static/feedback-tf-dark.png
:class: only-dark
```

The template is initialized with arbitrary transfer functions, so we will need to update these with values appropriate to our system.

For example, in the [cruise control example](BROKEN_LINK) the linearized plant model for the car is

$$
G(s) = \frac{b}{s - a}, \qquad b=1.32, ~~ a=-0.0101
$$

The cruise control is simple proportional-integral (PI) feedback:

$$
C(s) = k_p + \frac{k_i}{s}, \qquad k_p = 0.5, ~~ k_i = 0.1
$$

Let's update the transfer functions and turn off custom LaTeX rendering to see the numerical values:

```python
# Linearized vehicle model
b = 1.32
a = -0.0101
diagram["plant"].set_parameter("num", [b])
diagram["plant"].set_parameter("den", [1, -a])
diagram["plant"].custom_latex = None

# PI controller
kp = 0.5
ki = 0.1
diagram["controller"].set_parameter("num", [kp, ki])
diagram["controller"].set_parameter("den", [1, 0])
diagram["controller"].custom_latex = None
```

```{image} _static/edited-template-light.png
:class: only-light
```

```{image} _static/edited-template-dark.png
:class: only-dark
```

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