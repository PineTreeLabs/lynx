__all__ = ["DIAGRAM_TEMPLATES"]


DIAGRAM_TEMPLATES = {
    "open_loop_tf": open_loop_tf_template,
    "open_loop_ss": open_loop_ss_template,
    "feedback_tf": feedback_tf_template,
    "feedback_ss": feedback_ss_template,
    "feedforward_tf": feedforward_tf_template,
    "feedforward_ss": feedforward_ss_template,
    "filtered": filtered_tf_template,
    "cascaded": cascaded_tf_template,
}
