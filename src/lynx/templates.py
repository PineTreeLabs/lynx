__all__ = ["DIAGRAM_TEMPLATES"]

open_loop_tf_template = """
{
  "version": "1.0.0",
  "blocks": [
    {
      "id": "io_marker_1769112157639",
      "type": "io_marker",
      "position": {
        "x": 34.0,
        "y": 185.0
      },
      "label": "input",
      "flipped": false,
      "custom_latex": null,
      "label_visible": true,
      "width": null,
      "height": null,
      "parameters": [
        {
          "name": "marker_type",
          "value": "input",
          "expression": null
        },
        {
          "name": "label",
          "value": "u",
          "expression": null
        },
        {
          "name": "index",
          "value": 0,
          "expression": null
        }
      ],
      "ports": [
        {
          "id": "out",
          "type": "output",
          "label": "u"
        }
      ]
    },
    {
      "id": "transfer_function_1769112159991",
      "type": "transfer_function",
      "position": {
        "x": 222.0,
        "y": 176.0
      },
      "label": "plant",
      "flipped": false,
      "custom_latex": "G(s)",
      "label_visible": true,
      "width": null,
      "height": null,
      "parameters": [
        {
          "name": "numerator",
          "value": [
            1
          ],
          "expression": null
        },
        {
          "name": "denominator",
          "value": [
            1,
            1
          ],
          "expression": null
        }
      ],
      "ports": [
        {
          "id": "in",
          "type": "input",
          "label": null
        },
        {
          "id": "out",
          "type": "output",
          "label": null
        }
      ]
    },
    {
      "id": "io_marker_1769112179924",
      "type": "io_marker",
      "position": {
        "x": 460.37048685107857,
        "y": 185.0
      },
      "label": "output",
      "flipped": false,
      "custom_latex": null,
      "label_visible": true,
      "width": null,
      "height": null,
      "parameters": [
        {
          "name": "marker_type",
          "value": "output",
          "expression": null
        },
        {
          "name": "label",
          "value": "y",
          "expression": null
        },
        {
          "name": "index",
          "value": 0,
          "expression": null
        }
      ],
      "ports": [
        {
          "id": "in",
          "type": "input",
          "label": "y"
        }
      ]
    }
  ],
  "connections": [
    {
      "id": "conn_1769112168974",
      "source_block_id": "io_marker_1769112157639",
      "source_port_id": "out",
      "target_block_id": "transfer_function_1769112159991",
      "target_port_id": "in",
      "waypoints": [],
      "label": "u",
      "label_visible": true
    },
    {
      "id": "conn_1769112182774",
      "source_block_id": "transfer_function_1769112159991",
      "source_port_id": "out",
      "target_block_id": "io_marker_1769112179924",
      "target_port_id": "in",
      "waypoints": [
        {
          "x": 391.18519237747466,
          "y": 201.00023464133773
        },
        {
          "x": 391.18519237747466,
          "y": 201.00023464133773
        }
      ],
      "label": "y",
      "label_visible": true
    }
  ],
  "theme": null
}
"""

open_loop_ss_template = """
{
  "version": "1.0.0",
  "blocks": [
    {
      "id": "io_marker_1769112157639",
      "type": "io_marker",
      "position": {
        "x": 34.0,
        "y": 185.0
      },
      "label": "input",
      "flipped": false,
      "custom_latex": null,
      "label_visible": true,
      "width": null,
      "height": null,
      "parameters": [
        {
          "name": "marker_type",
          "value": "input",
          "expression": null
        },
        {
          "name": "label",
          "value": "u",
          "expression": null
        },
        {
          "name": "index",
          "value": 0,
          "expression": null
        }
      ],
      "ports": [
        {
          "id": "out",
          "type": "output",
          "label": "u"
        }
      ]
    },
    {
      "id": "io_marker_1769112179924",
      "type": "io_marker",
      "position": {
        "x": 460.37048685107857,
        "y": 185.0
      },
      "label": "output",
      "flipped": false,
      "custom_latex": null,
      "label_visible": true,
      "width": null,
      "height": null,
      "parameters": [
        {
          "name": "marker_type",
          "value": "output",
          "expression": null
        },
        {
          "name": "label",
          "value": "y",
          "expression": null
        },
        {
          "name": "index",
          "value": 0,
          "expression": null
        }
      ],
      "ports": [
        {
          "id": "in",
          "type": "input",
          "label": "y"
        }
      ]
    },
    {
      "id": "state_space_1769112354776",
      "type": "state_space",
      "position": {
        "x": 212.43384163373594,
        "y": 171.0
      },
      "label": "plant",
      "flipped": false,
      "custom_latex": null,
      "label_visible": true,
      "width": null,
      "height": null,
      "parameters": [
        {
          "name": "A",
          "value": [
            [
              0,
              1
            ],
            [
              -1,
              -1
            ]
          ],
          "expression": null
        },
        {
          "name": "B",
          "value": [
            [
              0
            ],
            [
              1
            ]
          ],
          "expression": null
        },
        {
          "name": "C",
          "value": [
            [
              1,
              0
            ]
          ],
          "expression": null
        },
        {
          "name": "D",
          "value": [
            [
              0
            ]
          ],
          "expression": null
        }
      ],
      "ports": [
        {
          "id": "in",
          "type": "input",
          "label": null
        },
        {
          "id": "out",
          "type": "output",
          "label": null
        }
      ]
    }
  ],
  "connections": [
    {
      "id": "conn_1769112360643",
      "source_block_id": "io_marker_1769112157639",
      "source_port_id": "out",
      "target_block_id": "state_space_1769112354776",
      "target_port_id": "in",
      "waypoints": [],
      "label": "u",
      "label_visible": true
    },
    {
      "id": "conn_1769112363143",
      "source_block_id": "state_space_1769112354776",
      "source_port_id": "out",
      "target_block_id": "io_marker_1769112179924",
      "target_port_id": "in",
      "waypoints": [
        {
          "x": 396.40210209693726,
          "y": 201.00002846805472
        },
        {
          "x": 396.40210209693726,
          "y": 201.00002846805472
        }
      ],
      "label": "y",
      "label_visible": true
    }
  ],
  "theme": null
}
"""

feedback_tf_template = """
{
  "version": "1.0.0",
  "blocks": [
    {
      "id": "io_marker_1769102540105",
      "type": "io_marker",
      "position": {
        "x": -9.445531640680983,
        "y": 166.0
      },
      "label": "ref",
      "flipped": false,
      "custom_latex": null,
      "label_visible": true,
      "width": null,
      "height": null,
      "parameters": [
        {
          "name": "marker_type",
          "value": "input",
          "expression": null
        },
        {
          "name": "index",
          "value": 0,
          "expression": null
        },
        {
          "name": "label",
          "value": "u",
          "expression": null
        }
      ],
      "ports": [
        {
          "id": "out",
          "type": "output",
          "label": "u"
        }
      ]
    },
    {
      "id": "sum_1769102547306",
      "type": "sum",
      "position": {
        "x": 311.0,
        "y": 154.0
      },
      "label": "sum_1769102547306",
      "flipped": false,
      "custom_latex": null,
      "label_visible": false,
      "width": null,
      "height": null,
      "parameters": [
        {
          "name": "signs",
          "value": [
            "+",
            "+",
            "-"
          ],
          "expression": null
        }
      ],
      "ports": [
        {
          "id": "out",
          "type": "output",
          "label": null
        },
        {
          "id": "in1",
          "type": "input",
          "label": null
        },
        {
          "id": "in2",
          "type": "input",
          "label": null
        },
        {
          "id": "in3",
          "type": "input",
          "label": null
        }
      ]
    },
    {
      "id": "transfer_function_1769102555888",
      "type": "transfer_function",
      "position": {
        "x": 451.67635068437426,
        "y": 157.0
      },
      "label": "controller",
      "flipped": false,
      "custom_latex": "C(s)",
      "label_visible": true,
      "width": null,
      "height": null,
      "parameters": [
        {
          "name": "numerator",
          "value": [
            1
          ],
          "expression": null
        },
        {
          "name": "denominator",
          "value": [
            1,
            1
          ],
          "expression": null
        }
      ],
      "ports": [
        {
          "id": "in",
          "type": "input",
          "label": null
        },
        {
          "id": "out",
          "type": "output",
          "label": null
        }
      ]
    },
    {
      "id": "transfer_function_1769102559255",
      "type": "transfer_function",
      "position": {
        "x": 624.6416269173607,
        "y": 157.0
      },
      "label": "plant",
      "flipped": false,
      "custom_latex": "G(s)",
      "label_visible": true,
      "width": null,
      "height": null,
      "parameters": [
        {
          "name": "numerator",
          "value": [
            1
          ],
          "expression": null
        },
        {
          "name": "denominator",
          "value": [
            1,
            1
          ],
          "expression": null
        }
      ],
      "ports": [
        {
          "id": "in",
          "type": "input",
          "label": null
        },
        {
          "id": "out",
          "type": "output",
          "label": null
        }
      ]
    },
    {
      "id": "io_marker_1769102614871",
      "type": "io_marker",
      "position": {
        "x": 905.2910533469737,
        "y": 166.26005326187624
      },
      "label": "output",
      "flipped": false,
      "custom_latex": null,
      "label_visible": true,
      "width": null,
      "height": null,
      "parameters": [
        {
          "name": "marker_type",
          "value": "output",
          "expression": null
        },
        {
          "name": "index",
          "value": 0,
          "expression": null
        },
        {
          "name": "label",
          "value": "y",
          "expression": null
        }
      ],
      "ports": [
        {
          "id": "in",
          "type": "input",
          "label": "y"
        }
      ]
    },
    {
      "id": "sum_1769105068595",
      "type": "sum",
      "position": {
        "x": 785.9531991933441,
        "y": 154.26005326187624
      },
      "label": "sum_1769105068595",
      "flipped": false,
      "custom_latex": null,
      "label_visible": false,
      "width": null,
      "height": null,
      "parameters": [
        {
          "name": "signs",
          "value": [
            "+",
            "+",
            "|"
          ],
          "expression": null
        }
      ],
      "ports": [
        {
          "id": "in1",
          "type": "input",
          "label": null
        },
        {
          "id": "in2",
          "type": "input",
          "label": null
        },
        {
          "id": "out",
          "type": "output",
          "label": null
        }
      ]
    },
    {
      "id": "io_marker_1769105091712",
      "type": "io_marker",
      "position": {
        "x": 640.938954071276,
        "y": 53.653742324102495
      },
      "label": "noise",
      "flipped": false,
      "custom_latex": null,
      "label_visible": true,
      "width": null,
      "height": null,
      "parameters": [
        {
          "name": "marker_type",
          "value": "input",
          "expression": null
        },
        {
          "name": "label",
          "value": "u",
          "expression": null
        },
        {
          "name": "index",
          "value": 2,
          "expression": null
        }
      ],
      "ports": [
        {
          "id": "out",
          "type": "output",
          "label": "u"
        }
      ]
    },
    {
      "id": "io_marker_1769112438327",
      "type": "io_marker",
      "position": {
        "x": 182.62098901703015,
        "y": 50.50281938153603
      },
      "label": "disturbance",
      "flipped": false,
      "custom_latex": null,
      "label_visible": true,
      "width": null,
      "height": null,
      "parameters": [
        {
          "name": "marker_type",
          "value": "input",
          "expression": null
        },
        {
          "name": "label",
          "value": "u",
          "expression": null
        },
        {
          "name": "index",
          "value": 1,
          "expression": null
        }
      ],
      "ports": [
        {
          "id": "out",
          "type": "output",
          "label": "u"
        }
      ]
    },
    {
      "id": "transfer_function_1769112492212",
      "type": "transfer_function",
      "position": {
        "x": 147.98514262269015,
        "y": 157.0
      },
      "label": "reference_shaping",
      "flipped": false,
      "custom_latex": "F(s)",
      "label_visible": true,
      "width": null,
      "height": null,
      "parameters": [
        {
          "name": "numerator",
          "value": [
            1
          ],
          "expression": null
        },
        {
          "name": "denominator",
          "value": 1,
          "expression": "1"
        }
      ],
      "ports": [
        {
          "id": "in",
          "type": "input",
          "label": null
        },
        {
          "id": "out",
          "type": "output",
          "label": null
        }
      ]
    }
  ],
  "connections": [
    {
      "id": "conn_1769102596971",
      "source_block_id": "sum_1769102547306",
      "source_port_id": "out",
      "target_block_id": "transfer_function_1769102555888",
      "target_port_id": "in",
      "waypoints": [],
      "label": "e",
      "label_visible": true
    },
    {
      "id": "conn_1769102602987",
      "source_block_id": "transfer_function_1769102555888",
      "source_port_id": "out",
      "target_block_id": "transfer_function_1769102559255",
      "target_port_id": "in",
      "waypoints": [],
      "label": "u",
      "label_visible": true
    },
    {
      "id": "conn_1769105074479",
      "source_block_id": "transfer_function_1769102559255",
      "source_port_id": "out",
      "target_block_id": "sum_1769105068595",
      "target_port_id": "in2",
      "waypoints": [],
      "label": null,
      "label_visible": false
    },
    {
      "id": "conn_1769105083062",
      "source_block_id": "sum_1769105068595",
      "source_port_id": "out",
      "target_block_id": "io_marker_1769102614871",
      "target_port_id": "in",
      "waypoints": [],
      "label": "y",
      "label_visible": true
    },
    {
      "id": "conn_1769105094595",
      "source_block_id": "io_marker_1769105091712",
      "source_port_id": "out",
      "target_block_id": "sum_1769105068595",
      "target_port_id": "in1",
      "waypoints": [
        {
          "x": 813.9531294742162,
          "y": 69.6542071715903
        }
      ],
      "label": "n",
      "label_visible": true
    },
    {
      "id": "conn_1769112467161",
      "source_block_id": "sum_1769105068595",
      "source_port_id": "out",
      "target_block_id": "sum_1769102547306",
      "target_port_id": "in3",
      "waypoints": [
        {
          "x": 863.9532031002068,
          "y": 182.26052807318874
        },
        {
          "x": 863.9532031002068,
          "y": 282.5349047202021
        },
        {
          "x": 338.99999287922856,
          "y": 282.5349047202021
        }
      ],
      "label": null,
      "label_visible": false
    },
    {
      "id": "conn_1769112479077",
      "source_block_id": "io_marker_1769112438327",
      "source_port_id": "out",
      "target_block_id": "sum_1769102547306",
      "target_port_id": "in1",
      "waypoints": [],
      "label": "d",
      "label_visible": true
    },
    {
      "id": "conn_1769112495012",
      "source_block_id": "transfer_function_1769112492212",
      "source_port_id": "out",
      "target_block_id": "sum_1769102547306",
      "target_port_id": "in2",
      "waypoints": [],
      "label": null,
      "label_visible": false
    },
    {
      "id": "conn_1769112499045",
      "source_block_id": "io_marker_1769102540105",
      "source_port_id": "out",
      "target_block_id": "transfer_function_1769112492212",
      "target_port_id": "in",
      "waypoints": [],
      "label": "r",
      "label_visible": true
    }
  ],
  "theme": null
}
"""

feedback_ss_template = """
{
  "version": "1.0.0",
  "blocks": [
    {
      "id": "io_marker_1769102540105",
      "type": "io_marker",
      "position": {
        "x": -20.718489400001502,
        "y": 166.0
      },
      "label": "ref",
      "flipped": false,
      "custom_latex": null,
      "label_visible": true,
      "width": null,
      "height": null,
      "parameters": [
        {
          "name": "marker_type",
          "value": "input",
          "expression": null
        },
        {
          "name": "label",
          "value": "u",
          "expression": null
        },
        {
          "name": "index",
          "value": 0,
          "expression": null
        }
      ],
      "ports": [
        {
          "id": "out",
          "type": "output",
          "label": "u"
        }
      ]
    },
    {
      "id": "sum_1769102547306",
      "type": "sum",
      "position": {
        "x": 311.0,
        "y": 154.0
      },
      "label": "sum_1769102547306",
      "flipped": false,
      "custom_latex": null,
      "label_visible": false,
      "width": null,
      "height": null,
      "parameters": [
        {
          "name": "signs",
          "value": [
            "+",
            "+",
            "-"
          ],
          "expression": null
        }
      ],
      "ports": [
        {
          "id": "out",
          "type": "output",
          "label": null
        },
        {
          "id": "in1",
          "type": "input",
          "label": null
        },
        {
          "id": "in2",
          "type": "input",
          "label": null
        },
        {
          "id": "in3",
          "type": "input",
          "label": null
        }
      ]
    },
    {
      "id": "transfer_function_1769102555888",
      "type": "transfer_function",
      "position": {
        "x": 451.67635068437426,
        "y": 157.0
      },
      "label": "controller",
      "flipped": false,
      "custom_latex": "C(s)",
      "label_visible": true,
      "width": null,
      "height": null,
      "parameters": [
        {
          "name": "numerator",
          "value": [
            1
          ],
          "expression": null
        },
        {
          "name": "denominator",
          "value": [
            1,
            1
          ],
          "expression": null
        }
      ],
      "ports": [
        {
          "id": "in",
          "type": "input",
          "label": null
        },
        {
          "id": "out",
          "type": "output",
          "label": null
        }
      ]
    },
    {
      "id": "io_marker_1769102614871",
      "type": "io_marker",
      "position": {
        "x": 939.2910533469737,
        "y": 166.0
      },
      "label": "output",
      "flipped": false,
      "custom_latex": null,
      "label_visible": true,
      "width": null,
      "height": null,
      "parameters": [
        {
          "name": "marker_type",
          "value": "output",
          "expression": null
        },
        {
          "name": "label",
          "value": "y",
          "expression": null
        }
      ],
      "ports": [
        {
          "id": "in",
          "type": "input",
          "label": "y"
        }
      ]
    },
    {
      "id": "state_space_1769102736336",
      "type": "state_space",
      "position": {
        "x": 627.2234383321918,
        "y": 152.0
      },
      "label": "plant",
      "flipped": false,
      "custom_latex": null,
      "label_visible": true,
      "width": null,
      "height": null,
      "parameters": [
        {
          "name": "A",
          "value": [
            [
              0,
              1
            ],
            [
              -1,
              -1
            ]
          ],
          "expression": null
        },
        {
          "name": "B",
          "value": [
            [
              0
            ],
            [
              1
            ]
          ],
          "expression": null
        },
        {
          "name": "C",
          "value": [
            [
              1,
              0
            ]
          ],
          "expression": null
        },
        {
          "name": "D",
          "value": [
            [
              0
            ]
          ],
          "expression": null
        }
      ],
      "ports": [
        {
          "id": "in",
          "type": "input",
          "label": null
        },
        {
          "id": "out",
          "type": "output",
          "label": null
        }
      ]
    },
    {
      "id": "sum_1769105176411",
      "type": "sum",
      "position": {
        "x": 809.0,
        "y": 154.0
      },
      "label": "sum_1769105176411",
      "flipped": false,
      "custom_latex": null,
      "label_visible": false,
      "width": null,
      "height": null,
      "parameters": [
        {
          "name": "signs",
          "value": [
            "+",
            "+",
            "|"
          ],
          "expression": null
        }
      ],
      "ports": [
        {
          "id": "in1",
          "type": "input",
          "label": null
        },
        {
          "id": "in2",
          "type": "input",
          "label": null
        },
        {
          "id": "out",
          "type": "output",
          "label": null
        }
      ]
    },
    {
      "id": "io_marker_1769105192695",
      "type": "io_marker",
      "position": {
        "x": 645.0,
        "y": 42.0
      },
      "label": "noise",
      "flipped": false,
      "custom_latex": null,
      "label_visible": true,
      "width": null,
      "height": null,
      "parameters": [
        {
          "name": "marker_type",
          "value": "input",
          "expression": null
        },
        {
          "name": "label",
          "value": "u",
          "expression": null
        },
        {
          "name": "index",
          "value": 2,
          "expression": null
        }
      ],
      "ports": [
        {
          "id": "out",
          "type": "output",
          "label": "u"
        }
      ]
    },
    {
      "id": "transfer_function_1769112585529",
      "type": "transfer_function",
      "position": {
        "x": 129.66275576166487,
        "y": 157.0
      },
      "label": "reference_shaping",
      "flipped": false,
      "custom_latex": "F(s)",
      "label_visible": true,
      "width": null,
      "height": null,
      "parameters": [
        {
          "name": "numerator",
          "value": 1,
          "expression": null
        },
        {
          "name": "denominator",
          "value": 1,
          "expression": null
        }
      ],
      "ports": [
        {
          "id": "in",
          "type": "input",
          "label": null
        },
        {
          "id": "out",
          "type": "output",
          "label": null
        }
      ]
    },
    {
      "id": "io_marker_1769112712948",
      "type": "io_marker",
      "position": {
        "x": 154.41137037928974,
        "y": 38.48817753742151
      },
      "label": "disturbance",
      "flipped": false,
      "custom_latex": null,
      "label_visible": true,
      "width": null,
      "height": null,
      "parameters": [
        {
          "name": "marker_type",
          "value": "input",
          "expression": null
        },
        {
          "name": "label",
          "value": "u",
          "expression": null
        },
        {
          "name": "index",
          "value": 1,
          "expression": null
        }
      ],
      "ports": [
        {
          "id": "out",
          "type": "output",
          "label": "u"
        }
      ]
    }
  ],
  "connections": [
    {
      "id": "conn_1769102596971",
      "source_block_id": "sum_1769102547306",
      "source_port_id": "out",
      "target_block_id": "transfer_function_1769102555888",
      "target_port_id": "in",
      "waypoints": [],
      "label": "e",
      "label_visible": true
    },
    {
      "id": "conn_1769102739804",
      "source_block_id": "transfer_function_1769102555888",
      "source_port_id": "out",
      "target_block_id": "state_space_1769102736336",
      "target_port_id": "in",
      "waypoints": [
        {
          "x": 589.449869982383,
          "y": 181.99981216992967
        },
        {
          "x": 589.449869982383,
          "y": 181.99981216992967
        }
      ],
      "label": "u",
      "label_visible": true
    },
    {
      "id": "conn_1769105181945",
      "source_block_id": "state_space_1769102736336",
      "source_port_id": "out",
      "target_block_id": "sum_1769105176411",
      "target_port_id": "in2",
      "waypoints": [],
      "label": null,
      "label_visible": false
    },
    {
      "id": "conn_1769105186028",
      "source_block_id": "sum_1769105176411",
      "source_port_id": "out",
      "target_block_id": "io_marker_1769102614871",
      "target_port_id": "in",
      "waypoints": [],
      "label": "y",
      "label_visible": true
    },
    {
      "id": "conn_1769105199711",
      "source_block_id": "io_marker_1769105192695",
      "source_port_id": "out",
      "target_block_id": "sum_1769105176411",
      "target_port_id": "in1",
      "waypoints": [],
      "label": "n",
      "label_visible": true
    },
    {
      "id": "conn_1769112597997",
      "source_block_id": "io_marker_1769102540105",
      "source_port_id": "out",
      "target_block_id": "transfer_function_1769112585529",
      "target_port_id": "in",
      "waypoints": [],
      "label": "r",
      "label_visible": true
    },
    {
      "id": "conn_1769112704664",
      "source_block_id": "transfer_function_1769112585529",
      "source_port_id": "out",
      "target_block_id": "sum_1769102547306",
      "target_port_id": "in2",
      "waypoints": [],
      "label": null,
      "label_visible": false
    },
    {
      "id": "conn_1769112709248",
      "source_block_id": "sum_1769105176411",
      "source_port_id": "out",
      "target_block_id": "sum_1769102547306",
      "target_port_id": "in3",
      "waypoints": [
        {
          "x": 886.9999470490217,
          "y": 182.00015162327549
        },
        {
          "x": 886.9999470490217,
          "y": 274.8493182608869
        },
        {
          "x": 339.00000073712914,
          "y": 274.8493182608869
        }
      ],
      "label": null,
      "label_visible": false
    },
    {
      "id": "conn_1769112720747",
      "source_block_id": "io_marker_1769112712948",
      "source_port_id": "out",
      "target_block_id": "sum_1769102547306",
      "target_port_id": "in1",
      "waypoints": [],
      "label": "d",
      "label_visible": true
    }
  ],
  "theme": null
}
"""

feedforward_ss_template = """
{
  "version": "1.0.0",
  "blocks": [
    {
      "id": "io_marker_1769102540105",
      "type": "io_marker",
      "position": {
        "x": -131.63271358428148,
        "y": 58.42401563813837
      },
      "label": "ref",
      "flipped": false,
      "custom_latex": null,
      "label_visible": true,
      "width": null,
      "height": null,
      "parameters": [
        {
          "name": "marker_type",
          "value": "input",
          "expression": null
        },
        {
          "name": "index",
          "value": 0,
          "expression": null
        },
        {
          "name": "label",
          "value": "u",
          "expression": null
        }
      ],
      "ports": [
        {
          "id": "out",
          "type": "output",
          "label": "u"
        }
      ]
    },
    {
      "id": "sum_1769102547306",
      "type": "sum",
      "position": {
        "x": -10.46979370385418,
        "y": 154.0
      },
      "label": "sum_1769102547306",
      "flipped": false,
      "custom_latex": null,
      "label_visible": false,
      "width": null,
      "height": null,
      "parameters": [
        {
          "name": "signs",
          "value": [
            "|",
            "+",
            "-"
          ],
          "expression": null
        }
      ],
      "ports": [
        {
          "id": "in1",
          "type": "input",
          "label": null
        },
        {
          "id": "in2",
          "type": "input",
          "label": null
        },
        {
          "id": "out",
          "type": "output",
          "label": null
        }
      ]
    },
    {
      "id": "transfer_function_1769102555888",
      "type": "transfer_function",
      "position": {
        "x": 109.34708434553534,
        "y": 157.0
      },
      "label": "feedback",
      "flipped": false,
      "custom_latex": "C(s)",
      "label_visible": true,
      "width": null,
      "height": null,
      "parameters": [
        {
          "name": "numerator",
          "value": [
            1
          ],
          "expression": null
        },
        {
          "name": "denominator",
          "value": [
            1,
            1
          ],
          "expression": null
        }
      ],
      "ports": [
        {
          "id": "in",
          "type": "input",
          "label": null
        },
        {
          "id": "out",
          "type": "output",
          "label": null
        }
      ]
    },
    {
      "id": "io_marker_1769102614871",
      "type": "io_marker",
      "position": {
        "x": 916.4374082642759,
        "y": 166.0
      },
      "label": "output",
      "flipped": false,
      "custom_latex": null,
      "label_visible": true,
      "width": null,
      "height": null,
      "parameters": [
        {
          "name": "marker_type",
          "value": "output",
          "expression": null
        },
        {
          "name": "index",
          "value": 0,
          "expression": null
        },
        {
          "name": "label",
          "value": "y",
          "expression": null
        }
      ],
      "ports": [
        {
          "id": "in",
          "type": "input",
          "label": "y"
        }
      ]
    },
    {
      "id": "state_space_1769102736336",
      "type": "state_space",
      "position": {
        "x": 569.8000543788206,
        "y": 152.0
      },
      "label": "plant",
      "flipped": false,
      "custom_latex": null,
      "label_visible": true,
      "width": null,
      "height": null,
      "parameters": [
        {
          "name": "A",
          "value": [
            [
              0,
              1
            ],
            [
              -1,
              -1
            ]
          ],
          "expression": null
        },
        {
          "name": "B",
          "value": [
            [
              0
            ],
            [
              1
            ]
          ],
          "expression": null
        },
        {
          "name": "C",
          "value": [
            [
              1,
              0
            ]
          ],
          "expression": null
        },
        {
          "name": "D",
          "value": [
            [
              0
            ]
          ],
          "expression": null
        }
      ],
      "ports": [
        {
          "id": "in",
          "type": "input",
          "label": null
        },
        {
          "id": "out",
          "type": "output",
          "label": null
        }
      ]
    },
    {
      "id": "transfer_function_1769102803187",
      "type": "transfer_function",
      "position": {
        "x": 106.00835790115087,
        "y": 49.42401563813837
      },
      "label": "feedforward",
      "flipped": false,
      "custom_latex": "F(s)",
      "label_visible": true,
      "width": null,
      "height": null,
      "parameters": [
        {
          "name": "numerator",
          "value": [
            1
          ],
          "expression": null
        },
        {
          "name": "denominator",
          "value": [
            1,
            1
          ],
          "expression": null
        }
      ],
      "ports": [
        {
          "id": "in",
          "type": "input",
          "label": null
        },
        {
          "id": "out",
          "type": "output",
          "label": null
        }
      ]
    },
    {
      "id": "sum_1769102922603",
      "type": "sum",
      "position": {
        "x": 440.20578052341557,
        "y": 154.0
      },
      "label": "sum_1769102922603",
      "flipped": false,
      "custom_latex": null,
      "label_visible": false,
      "width": null,
      "height": null,
      "parameters": [
        {
          "name": "signs",
          "value": [
            "+",
            "+",
            "|"
          ],
          "expression": null
        }
      ],
      "ports": [
        {
          "id": "out",
          "type": "output",
          "label": null
        },
        {
          "id": "in1",
          "type": "input",
          "label": null
        },
        {
          "id": "in2",
          "type": "input",
          "label": null
        }
      ]
    },
    {
      "id": "sum_1769105252127",
      "type": "sum",
      "position": {
        "x": 761.848309722594,
        "y": 154.0
      },
      "label": "sum_1769105252127",
      "flipped": false,
      "custom_latex": null,
      "label_visible": false,
      "width": null,
      "height": null,
      "parameters": [
        {
          "name": "signs",
          "value": [
            "+",
            "+",
            "|"
          ],
          "expression": null
        }
      ],
      "ports": [
        {
          "id": "in1",
          "type": "input",
          "label": null
        },
        {
          "id": "in2",
          "type": "input",
          "label": null
        },
        {
          "id": "out",
          "type": "output",
          "label": null
        }
      ]
    },
    {
      "id": "io_marker_1769105261377",
      "type": "io_marker",
      "position": {
        "x": 672.1293363206678,
        "y": 59.05818256954808
      },
      "label": "noise",
      "flipped": false,
      "custom_latex": null,
      "label_visible": true,
      "width": null,
      "height": null,
      "parameters": [
        {
          "name": "marker_type",
          "value": "input",
          "expression": null
        },
        {
          "name": "label",
          "value": "u",
          "expression": null
        },
        {
          "name": "index",
          "value": 2,
          "expression": null
        }
      ],
      "ports": [
        {
          "id": "out",
          "type": "output",
          "label": "u"
        }
      ]
    },
    {
      "id": "io_marker_1769112847751",
      "type": "io_marker",
      "position": {
        "x": 355.2796378054232,
        "y": 60.339578438708486
      },
      "label": "disturbance",
      "flipped": false,
      "custom_latex": null,
      "label_visible": true,
      "width": null,
      "height": null,
      "parameters": [
        {
          "name": "marker_type",
          "value": "input",
          "expression": null
        },
        {
          "name": "label",
          "value": "u",
          "expression": null
        },
        {
          "name": "index",
          "value": 1,
          "expression": null
        }
      ],
      "ports": [
        {
          "id": "out",
          "type": "output",
          "label": "u"
        }
      ]
    },
    {
      "id": "sum_1769112947819",
      "type": "sum",
      "position": {
        "x": 280.173751711254,
        "y": 154.0
      },
      "label": "sum_1769112947819",
      "flipped": false,
      "custom_latex": null,
      "label_visible": false,
      "width": null,
      "height": null,
      "parameters": [
        {
          "name": "signs",
          "value": [
            "+",
            "+",
            "|"
          ],
          "expression": null
        }
      ],
      "ports": [
        {
          "id": "in1",
          "type": "input",
          "label": null
        },
        {
          "id": "in2",
          "type": "input",
          "label": null
        },
        {
          "id": "out",
          "type": "output",
          "label": null
        }
      ]
    }
  ],
  "connections": [
    {
      "id": "conn_1769102596971",
      "source_block_id": "sum_1769102547306",
      "source_port_id": "out",
      "target_block_id": "transfer_function_1769102555888",
      "target_port_id": "in",
      "waypoints": [],
      "label": "e",
      "label_visible": true
    },
    {
      "id": "conn_1769102954270",
      "source_block_id": "io_marker_1769102540105",
      "source_port_id": "out",
      "target_block_id": "transfer_function_1769102803187",
      "target_port_id": "in",
      "waypoints": [],
      "label": "r",
      "label_visible": true
    },
    {
      "id": "conn_1769102957236",
      "source_block_id": "io_marker_1769102540105",
      "source_port_id": "out",
      "target_block_id": "sum_1769102547306",
      "target_port_id": "in1",
      "waypoints": [],
      "label": null,
      "label_visible": false
    },
    {
      "id": "conn_1769105255111",
      "source_block_id": "state_space_1769102736336",
      "source_port_id": "out",
      "target_block_id": "sum_1769105252127",
      "target_port_id": "in2",
      "waypoints": [],
      "label": null,
      "label_visible": false
    },
    {
      "id": "conn_1769105258994",
      "source_block_id": "sum_1769105252127",
      "source_port_id": "out",
      "target_block_id": "io_marker_1769102614871",
      "target_port_id": "in",
      "waypoints": [],
      "label": "y",
      "label_visible": true
    },
    {
      "id": "conn_1769105264427",
      "source_block_id": "io_marker_1769105261377",
      "source_port_id": "out",
      "target_block_id": "sum_1769105252127",
      "target_port_id": "in1",
      "waypoints": [],
      "label": "n",
      "label_visible": true
    },
    {
      "id": "conn_1769105280735",
      "source_block_id": "sum_1769105252127",
      "source_port_id": "out",
      "target_block_id": "sum_1769102547306",
      "target_port_id": "in2",
      "waypoints": [
        {
          "x": 839.8483226622534,
          "y": 181.99986528405304
        },
        {
          "x": 839.8483226622534,
          "y": 262.17464544456
        },
        {
          "x": 17.53021170646083,
          "y": 262.17464544456
        }
      ],
      "label": null,
      "label_visible": false
    },
    {
      "id": "conn_1769112852867",
      "source_block_id": "io_marker_1769112847751",
      "source_port_id": "out",
      "target_block_id": "sum_1769102922603",
      "target_port_id": "in1",
      "waypoints": [],
      "label": "d",
      "label_visible": true
    },
    {
      "id": "conn_1769112953201",
      "source_block_id": "transfer_function_1769102555888",
      "source_port_id": "out",
      "target_block_id": "sum_1769112947819",
      "target_port_id": "in2",
      "waypoints": [
        {
          "x": 244.7604067119579,
          "y": 181.99940169064823
        },
        {
          "x": 244.7604067119579,
          "y": 181.99940169064823
        }
      ],
      "label": "u_ff",
      "label_visible": true
    },
    {
      "id": "conn_1769112968418",
      "source_block_id": "transfer_function_1769102803187",
      "source_port_id": "out",
      "target_block_id": "sum_1769112947819",
      "target_port_id": "in1",
      "waypoints": [],
      "label": "u_ff",
      "label_visible": true
    },
    {
      "id": "conn_1769112975389",
      "source_block_id": "sum_1769112947819",
      "source_port_id": "out",
      "target_block_id": "sum_1769102922603",
      "target_port_id": "in2",
      "waypoints": [],
      "label": "u",
      "label_visible": true
    },
    {
      "id": "conn_1769113019019",
      "source_block_id": "sum_1769102922603",
      "source_port_id": "out",
      "target_block_id": "state_space_1769102736336",
      "target_port_id": "in",
      "waypoints": [],
      "label": null,
      "label_visible": false
    }
  ],
  "theme": null
}
"""

feedforward_tf_template = """
{
  "version": "1.0.0",
  "blocks": [
    {
      "id": "io_marker_1769102540105",
      "type": "io_marker",
      "position": {
        "x": -131.63271358428148,
        "y": 58.42401563813837
      },
      "label": "ref",
      "flipped": false,
      "custom_latex": null,
      "label_visible": true,
      "width": null,
      "height": null,
      "parameters": [
        {
          "name": "marker_type",
          "value": "input",
          "expression": null
        },
        {
          "name": "index",
          "value": 0,
          "expression": null
        },
        {
          "name": "label",
          "value": "u",
          "expression": null
        }
      ],
      "ports": [
        {
          "id": "out",
          "type": "output",
          "label": "u"
        }
      ]
    },
    {
      "id": "sum_1769102547306",
      "type": "sum",
      "position": {
        "x": -10.46979370385418,
        "y": 154.0
      },
      "label": "sum_1769102547306",
      "flipped": false,
      "custom_latex": null,
      "label_visible": false,
      "width": null,
      "height": null,
      "parameters": [
        {
          "name": "signs",
          "value": [
            "|",
            "+",
            "-"
          ],
          "expression": null
        }
      ],
      "ports": [
        {
          "id": "in1",
          "type": "input",
          "label": null
        },
        {
          "id": "in2",
          "type": "input",
          "label": null
        },
        {
          "id": "out",
          "type": "output",
          "label": null
        }
      ]
    },
    {
      "id": "transfer_function_1769102555888",
      "type": "transfer_function",
      "position": {
        "x": 109.34708434553534,
        "y": 157.0
      },
      "label": "feedback",
      "flipped": false,
      "custom_latex": "C(s)",
      "label_visible": true,
      "width": null,
      "height": null,
      "parameters": [
        {
          "name": "numerator",
          "value": [
            1
          ],
          "expression": null
        },
        {
          "name": "denominator",
          "value": [
            1,
            1
          ],
          "expression": null
        }
      ],
      "ports": [
        {
          "id": "in",
          "type": "input",
          "label": null
        },
        {
          "id": "out",
          "type": "output",
          "label": null
        }
      ]
    },
    {
      "id": "io_marker_1769102614871",
      "type": "io_marker",
      "position": {
        "x": 916.4374082642759,
        "y": 166.0
      },
      "label": "output",
      "flipped": false,
      "custom_latex": null,
      "label_visible": true,
      "width": null,
      "height": null,
      "parameters": [
        {
          "name": "marker_type",
          "value": "output",
          "expression": null
        },
        {
          "name": "index",
          "value": 0,
          "expression": null
        },
        {
          "name": "label",
          "value": "y",
          "expression": null
        }
      ],
      "ports": [
        {
          "id": "in",
          "type": "input",
          "label": "y"
        }
      ]
    },
    {
      "id": "transfer_function_1769102803187",
      "type": "transfer_function",
      "position": {
        "x": 106.00835790115087,
        "y": 49.42401563813837
      },
      "label": "feedforward",
      "flipped": false,
      "custom_latex": "F(s)",
      "label_visible": true,
      "width": null,
      "height": null,
      "parameters": [
        {
          "name": "numerator",
          "value": [
            1
          ],
          "expression": null
        },
        {
          "name": "denominator",
          "value": [
            1,
            1
          ],
          "expression": null
        }
      ],
      "ports": [
        {
          "id": "in",
          "type": "input",
          "label": null
        },
        {
          "id": "out",
          "type": "output",
          "label": null
        }
      ]
    },
    {
      "id": "sum_1769102922603",
      "type": "sum",
      "position": {
        "x": 440.20578052341557,
        "y": 154.0
      },
      "label": "sum_1769102922603",
      "flipped": false,
      "custom_latex": null,
      "label_visible": false,
      "width": null,
      "height": null,
      "parameters": [
        {
          "name": "signs",
          "value": [
            "+",
            "+",
            "|"
          ],
          "expression": null
        }
      ],
      "ports": [
        {
          "id": "out",
          "type": "output",
          "label": null
        },
        {
          "id": "in1",
          "type": "input",
          "label": null
        },
        {
          "id": "in2",
          "type": "input",
          "label": null
        }
      ]
    },
    {
      "id": "sum_1769105252127",
      "type": "sum",
      "position": {
        "x": 761.848309722594,
        "y": 154.0
      },
      "label": "sum_1769105252127",
      "flipped": false,
      "custom_latex": null,
      "label_visible": false,
      "width": null,
      "height": null,
      "parameters": [
        {
          "name": "signs",
          "value": [
            "+",
            "+",
            "|"
          ],
          "expression": null
        }
      ],
      "ports": [
        {
          "id": "in1",
          "type": "input",
          "label": null
        },
        {
          "id": "in2",
          "type": "input",
          "label": null
        },
        {
          "id": "out",
          "type": "output",
          "label": null
        }
      ]
    },
    {
      "id": "io_marker_1769105261377",
      "type": "io_marker",
      "position": {
        "x": 672.1293363206678,
        "y": 59.05818256954808
      },
      "label": "noise",
      "flipped": false,
      "custom_latex": null,
      "label_visible": true,
      "width": null,
      "height": null,
      "parameters": [
        {
          "name": "marker_type",
          "value": "input",
          "expression": null
        },
        {
          "name": "label",
          "value": "u",
          "expression": null
        },
        {
          "name": "index",
          "value": 2,
          "expression": null
        }
      ],
      "ports": [
        {
          "id": "out",
          "type": "output",
          "label": "u"
        }
      ]
    },
    {
      "id": "io_marker_1769112847751",
      "type": "io_marker",
      "position": {
        "x": 355.2796378054232,
        "y": 60.339578438708486
      },
      "label": "disturbance",
      "flipped": false,
      "custom_latex": null,
      "label_visible": true,
      "width": null,
      "height": null,
      "parameters": [
        {
          "name": "marker_type",
          "value": "input",
          "expression": null
        },
        {
          "name": "label",
          "value": "u",
          "expression": null
        },
        {
          "name": "index",
          "value": 1,
          "expression": null
        }
      ],
      "ports": [
        {
          "id": "out",
          "type": "output",
          "label": "u"
        }
      ]
    },
    {
      "id": "sum_1769112947819",
      "type": "sum",
      "position": {
        "x": 280.173751711254,
        "y": 154.0
      },
      "label": "sum_1769112947819",
      "flipped": false,
      "custom_latex": null,
      "label_visible": false,
      "width": null,
      "height": null,
      "parameters": [
        {
          "name": "signs",
          "value": [
            "+",
            "+",
            "|"
          ],
          "expression": null
        }
      ],
      "ports": [
        {
          "id": "in1",
          "type": "input",
          "label": null
        },
        {
          "id": "in2",
          "type": "input",
          "label": null
        },
        {
          "id": "out",
          "type": "output",
          "label": null
        }
      ]
    },
    {
      "id": "transfer_function_1769113049220",
      "type": "transfer_function",
      "position": {
        "x": 583.2750405020421,
        "y": 157.0
      },
      "label": "plant",
      "flipped": false,
      "custom_latex": "G(s)",
      "label_visible": true,
      "width": null,
      "height": null,
      "parameters": [
        {
          "name": "numerator",
          "value": [
            1
          ],
          "expression": null
        },
        {
          "name": "denominator",
          "value": [
            1,
            1
          ],
          "expression": null
        }
      ],
      "ports": [
        {
          "id": "in",
          "type": "input",
          "label": null
        },
        {
          "id": "out",
          "type": "output",
          "label": null
        }
      ]
    }
  ],
  "connections": [
    {
      "id": "conn_1769102596971",
      "source_block_id": "sum_1769102547306",
      "source_port_id": "out",
      "target_block_id": "transfer_function_1769102555888",
      "target_port_id": "in",
      "waypoints": [],
      "label": "e",
      "label_visible": true
    },
    {
      "id": "conn_1769102954270",
      "source_block_id": "io_marker_1769102540105",
      "source_port_id": "out",
      "target_block_id": "transfer_function_1769102803187",
      "target_port_id": "in",
      "waypoints": [],
      "label": "r",
      "label_visible": true
    },
    {
      "id": "conn_1769102957236",
      "source_block_id": "io_marker_1769102540105",
      "source_port_id": "out",
      "target_block_id": "sum_1769102547306",
      "target_port_id": "in1",
      "waypoints": [],
      "label": null,
      "label_visible": false
    },
    {
      "id": "conn_1769105258994",
      "source_block_id": "sum_1769105252127",
      "source_port_id": "out",
      "target_block_id": "io_marker_1769102614871",
      "target_port_id": "in",
      "waypoints": [],
      "label": "y",
      "label_visible": true
    },
    {
      "id": "conn_1769105264427",
      "source_block_id": "io_marker_1769105261377",
      "source_port_id": "out",
      "target_block_id": "sum_1769105252127",
      "target_port_id": "in1",
      "waypoints": [],
      "label": "n",
      "label_visible": true
    },
    {
      "id": "conn_1769105280735",
      "source_block_id": "sum_1769105252127",
      "source_port_id": "out",
      "target_block_id": "sum_1769102547306",
      "target_port_id": "in2",
      "waypoints": [
        {
          "x": 839.8483226622534,
          "y": 181.99986528405304
        },
        {
          "x": 839.8483226622534,
          "y": 262.17464544456
        },
        {
          "x": 17.53021170646083,
          "y": 262.17464544456
        }
      ],
      "label": null,
      "label_visible": false
    },
    {
      "id": "conn_1769112852867",
      "source_block_id": "io_marker_1769112847751",
      "source_port_id": "out",
      "target_block_id": "sum_1769102922603",
      "target_port_id": "in1",
      "waypoints": [],
      "label": "d",
      "label_visible": true
    },
    {
      "id": "conn_1769112953201",
      "source_block_id": "transfer_function_1769102555888",
      "source_port_id": "out",
      "target_block_id": "sum_1769112947819",
      "target_port_id": "in2",
      "waypoints": [
        {
          "x": 244.7604067119579,
          "y": 181.99940169064823
        },
        {
          "x": 244.7604067119579,
          "y": 181.99940169064823
        }
      ],
      "label": "u_ff",
      "label_visible": true
    },
    {
      "id": "conn_1769112968418",
      "source_block_id": "transfer_function_1769102803187",
      "source_port_id": "out",
      "target_block_id": "sum_1769112947819",
      "target_port_id": "in1",
      "waypoints": [],
      "label": "u_ff",
      "label_visible": true
    },
    {
      "id": "conn_1769112975389",
      "source_block_id": "sum_1769112947819",
      "source_port_id": "out",
      "target_block_id": "sum_1769102922603",
      "target_port_id": "in2",
      "waypoints": [],
      "label": "u",
      "label_visible": true
    },
    {
      "id": "conn_1769113052836",
      "source_block_id": "sum_1769102922603",
      "source_port_id": "out",
      "target_block_id": "transfer_function_1769113049220",
      "target_port_id": "in",
      "waypoints": [],
      "label": null,
      "label_visible": false
    },
    {
      "id": "conn_1769113054420",
      "source_block_id": "transfer_function_1769113049220",
      "source_port_id": "out",
      "target_block_id": "sum_1769105252127",
      "target_port_id": "in2",
      "waypoints": [],
      "label": null,
      "label_visible": false
    }
  ],
  "theme": null
}
"""

filtered_tf_template = """
{
  "version": "1.0.0",
  "blocks": [
    {
      "id": "io_marker_1769102540105",
      "type": "io_marker",
      "position": {
        "x": -153.12942555936795,
        "y": 50.60783804836137
      },
      "label": "ref",
      "flipped": false,
      "custom_latex": null,
      "label_visible": true,
      "width": null,
      "height": null,
      "parameters": [
        {
          "name": "marker_type",
          "value": "input",
          "expression": null
        },
        {
          "name": "index",
          "value": 0,
          "expression": null
        },
        {
          "name": "label",
          "value": "u",
          "expression": null
        }
      ],
      "ports": [
        {
          "id": "out",
          "type": "output",
          "label": "u"
        }
      ]
    },
    {
      "id": "sum_1769102547306",
      "type": "sum",
      "position": {
        "x": 220.0715978892689,
        "y": 154.0
      },
      "label": "sum_1769102547306",
      "flipped": false,
      "custom_latex": null,
      "label_visible": false,
      "width": null,
      "height": null,
      "parameters": [
        {
          "name": "signs",
          "value": [
            "|",
            "+",
            "-"
          ],
          "expression": null
        }
      ],
      "ports": [
        {
          "id": "in1",
          "type": "input",
          "label": null
        },
        {
          "id": "in2",
          "type": "input",
          "label": null
        },
        {
          "id": "out",
          "type": "output",
          "label": null
        }
      ]
    },
    {
      "id": "transfer_function_1769102555888",
      "type": "transfer_function",
      "position": {
        "x": 340.0004316263033,
        "y": 157.0
      },
      "label": "feedback",
      "flipped": false,
      "custom_latex": "C(s)",
      "label_visible": true,
      "width": null,
      "height": null,
      "parameters": [
        {
          "name": "numerator",
          "value": [
            1
          ],
          "expression": null
        },
        {
          "name": "denominator",
          "value": [
            1,
            1
          ],
          "expression": null
        }
      ],
      "ports": [
        {
          "id": "in",
          "type": "input",
          "label": null
        },
        {
          "id": "out",
          "type": "output",
          "label": null
        }
      ]
    },
    {
      "id": "io_marker_1769102614871",
      "type": "io_marker",
      "position": {
        "x": 1105.590790025849,
        "y": 166.0
      },
      "label": "output",
      "flipped": false,
      "custom_latex": null,
      "label_visible": true,
      "width": null,
      "height": null,
      "parameters": [
        {
          "name": "marker_type",
          "value": "output",
          "expression": null
        },
        {
          "name": "index",
          "value": 0,
          "expression": null
        },
        {
          "name": "label",
          "value": "y",
          "expression": null
        }
      ],
      "ports": [
        {
          "id": "in",
          "type": "input",
          "label": "y"
        }
      ]
    },
    {
      "id": "transfer_function_1769102803187",
      "type": "transfer_function",
      "position": {
        "x": 331.2642757748997,
        "y": 41.60783804836137
      },
      "label": "feedforward",
      "flipped": false,
      "custom_latex": "F(s)",
      "label_visible": true,
      "width": null,
      "height": null,
      "parameters": [
        {
          "name": "numerator",
          "value": [
            1
          ],
          "expression": null
        },
        {
          "name": "denominator",
          "value": [
            1,
            1
          ],
          "expression": null
        }
      ],
      "ports": [
        {
          "id": "in",
          "type": "input",
          "label": null
        },
        {
          "id": "out",
          "type": "output",
          "label": null
        }
      ]
    },
    {
      "id": "sum_1769102922603",
      "type": "sum",
      "position": {
        "x": 501.5685791730227,
        "y": 154.0
      },
      "label": "sum_1769102922603",
      "flipped": false,
      "custom_latex": null,
      "label_visible": false,
      "width": null,
      "height": null,
      "parameters": [
        {
          "name": "signs",
          "value": [
            "+",
            "+",
            "|"
          ],
          "expression": null
        }
      ],
      "ports": [
        {
          "id": "in1",
          "type": "input",
          "label": null
        },
        {
          "id": "in2",
          "type": "input",
          "label": null
        },
        {
          "id": "out",
          "type": "output",
          "label": null
        }
      ]
    },
    {
      "id": "transfer_function_1769103013153",
      "type": "transfer_function",
      "position": {
        "x": 790.2928113611342,
        "y": 157.0
      },
      "label": "plant",
      "flipped": false,
      "custom_latex": "G(s)",
      "label_visible": true,
      "width": null,
      "height": null,
      "parameters": [
        {
          "name": "numerator",
          "value": [
            1
          ],
          "expression": null
        },
        {
          "name": "denominator",
          "value": [
            1,
            1
          ],
          "expression": null
        }
      ],
      "ports": [
        {
          "id": "in",
          "type": "input",
          "label": null
        },
        {
          "id": "out",
          "type": "output",
          "label": null
        }
      ]
    },
    {
      "id": "transfer_function_1769103238401",
      "type": "transfer_function",
      "position": {
        "x": 20.004859744412414,
        "y": 41.60783804836137
      },
      "label": "ref_filter",
      "flipped": false,
      "custom_latex": "F_r(s)",
      "label_visible": true,
      "width": null,
      "height": null,
      "parameters": [
        {
          "name": "numerator",
          "value": [
            1
          ],
          "expression": null
        },
        {
          "name": "denominator",
          "value": [
            1,
            1
          ],
          "expression": null
        }
      ],
      "ports": [
        {
          "id": "in",
          "type": "input",
          "label": null
        },
        {
          "id": "out",
          "type": "output",
          "label": null
        }
      ]
    },
    {
      "id": "transfer_function_1769103280085",
      "type": "transfer_function",
      "position": {
        "x": 438.34806264947576,
        "y": 265.1974063017424
      },
      "label": "obs_filter",
      "flipped": true,
      "custom_latex": "F_y(s)",
      "label_visible": true,
      "width": null,
      "height": null,
      "parameters": [
        {
          "name": "numerator",
          "value": [
            1
          ],
          "expression": null
        },
        {
          "name": "denominator",
          "value": [
            1,
            1
          ],
          "expression": null
        }
      ],
      "ports": [
        {
          "id": "in",
          "type": "input",
          "label": null
        },
        {
          "id": "out",
          "type": "output",
          "label": null
        }
      ]
    },
    {
      "id": "io_marker_1769105385044",
      "type": "io_marker",
      "position": {
        "x": 840.207405949233,
        "y": 45.01970459560471
      },
      "label": "noise",
      "flipped": false,
      "custom_latex": null,
      "label_visible": true,
      "width": null,
      "height": null,
      "parameters": [
        {
          "name": "marker_type",
          "value": "input",
          "expression": null
        },
        {
          "name": "index",
          "value": 1,
          "expression": null
        },
        {
          "name": "label",
          "value": "u",
          "expression": null
        }
      ],
      "ports": [
        {
          "id": "out",
          "type": "output",
          "label": "u"
        }
      ]
    },
    {
      "id": "sum_1769105399078",
      "type": "sum",
      "position": {
        "x": 945.8876240766991,
        "y": 154.0
      },
      "label": "sum_1769105399078",
      "flipped": false,
      "custom_latex": null,
      "label_visible": false,
      "width": null,
      "height": null,
      "parameters": [
        {
          "name": "signs",
          "value": [
            "+",
            "+",
            "|"
          ],
          "expression": null
        }
      ],
      "ports": [
        {
          "id": "in1",
          "type": "input",
          "label": null
        },
        {
          "id": "in2",
          "type": "input",
          "label": null
        },
        {
          "id": "out",
          "type": "output",
          "label": null
        }
      ]
    },
    {
      "id": "io_marker_1769113120287",
      "type": "io_marker",
      "position": {
        "x": 563.3750090112035,
        "y": 50.47080788297899
      },
      "label": "disturbance",
      "flipped": false,
      "custom_latex": null,
      "label_visible": true,
      "width": null,
      "height": null,
      "parameters": [
        {
          "name": "marker_type",
          "value": "input",
          "expression": null
        },
        {
          "name": "index",
          "value": 2,
          "expression": null
        },
        {
          "name": "label",
          "value": "u",
          "expression": null
        }
      ],
      "ports": [
        {
          "id": "out",
          "type": "output",
          "label": "u"
        }
      ]
    },
    {
      "id": "sum_1769113134271",
      "type": "sum",
      "position": {
        "x": 641.3210772424165,
        "y": 153.8686534958124
      },
      "label": "sum_1769113134271",
      "flipped": false,
      "custom_latex": null,
      "label_visible": false,
      "width": null,
      "height": null,
      "parameters": [
        {
          "name": "signs",
          "value": [
            "+",
            "+",
            "|"
          ],
          "expression": null
        }
      ],
      "ports": [
        {
          "id": "in1",
          "type": "input",
          "label": null
        },
        {
          "id": "in2",
          "type": "input",
          "label": null
        },
        {
          "id": "out",
          "type": "output",
          "label": null
        }
      ]
    }
  ],
  "connections": [
    {
      "id": "conn_1769102596971",
      "source_block_id": "sum_1769102547306",
      "source_port_id": "out",
      "target_block_id": "transfer_function_1769102555888",
      "target_port_id": "in",
      "waypoints": [],
      "label": "e",
      "label_visible": true
    },
    {
      "id": "conn_1769102942836",
      "source_block_id": "transfer_function_1769102803187",
      "source_port_id": "out",
      "target_block_id": "sum_1769102922603",
      "target_port_id": "in1",
      "waypoints": [],
      "label": "u_ff",
      "label_visible": true
    },
    {
      "id": "conn_1769103255018",
      "source_block_id": "transfer_function_1769103238401",
      "source_port_id": "out",
      "target_block_id": "transfer_function_1769102803187",
      "target_port_id": "in",
      "waypoints": [],
      "label": "r_filt",
      "label_visible": true
    },
    {
      "id": "conn_1769103257450",
      "source_block_id": "transfer_function_1769103238401",
      "source_port_id": "out",
      "target_block_id": "sum_1769102547306",
      "target_port_id": "in1",
      "waypoints": [],
      "label": null,
      "label_visible": false
    },
    {
      "id": "conn_1769103265101",
      "source_block_id": "io_marker_1769102540105",
      "source_port_id": "out",
      "target_block_id": "transfer_function_1769103238401",
      "target_port_id": "in",
      "waypoints": [],
      "label": "r",
      "label_visible": true
    },
    {
      "id": "conn_1769103288968",
      "source_block_id": "transfer_function_1769103280085",
      "source_port_id": "out",
      "target_block_id": "sum_1769102547306",
      "target_port_id": "in2",
      "waypoints": [
        {
          "x": 248.07157575947713,
          "y": 290.19726189139726
        }
      ],
      "label": "y_filt",
      "label_visible": true
    },
    {
      "id": "conn_1769105404145",
      "source_block_id": "transfer_function_1769103013153",
      "source_port_id": "out",
      "target_block_id": "sum_1769105399078",
      "target_port_id": "in2",
      "waypoints": [],
      "label": null,
      "label_visible": false
    },
    {
      "id": "conn_1769105408578",
      "source_block_id": "sum_1769105399078",
      "source_port_id": "out",
      "target_block_id": "io_marker_1769102614871",
      "target_port_id": "in",
      "waypoints": [],
      "label": "y",
      "label_visible": true
    },
    {
      "id": "conn_1769105410877",
      "source_block_id": "io_marker_1769105385044",
      "source_port_id": "out",
      "target_block_id": "sum_1769105399078",
      "target_port_id": "in1",
      "waypoints": [],
      "label": "n",
      "label_visible": true
    },
    {
      "id": "conn_1769105418945",
      "source_block_id": "sum_1769105399078",
      "source_port_id": "out",
      "target_block_id": "transfer_function_1769103280085",
      "target_port_id": "in",
      "waypoints": [],
      "label": null,
      "label_visible": false
    },
    {
      "id": "conn_1769113138371",
      "source_block_id": "sum_1769102922603",
      "source_port_id": "out",
      "target_block_id": "sum_1769113134271",
      "target_port_id": "in2",
      "waypoints": [
        {
          "x": 599.4448470200318,
          "y": 182.00084408405448
        },
        {
          "x": 599.4448470200318,
          "y": 182.00084408405448
        }
      ],
      "label": "u",
      "label_visible": true
    },
    {
      "id": "conn_1769113140119",
      "source_block_id": "sum_1769113134271",
      "source_port_id": "out",
      "target_block_id": "transfer_function_1769103013153",
      "target_port_id": "in",
      "waypoints": [],
      "label": null,
      "label_visible": false
    },
    {
      "id": "conn_1769113143938",
      "source_block_id": "io_marker_1769113120287",
      "source_port_id": "out",
      "target_block_id": "sum_1769113134271",
      "target_port_id": "in1",
      "waypoints": [],
      "label": "d",
      "label_visible": true
    },
    {
      "id": "conn_1769113156872",
      "source_block_id": "transfer_function_1769102555888",
      "source_port_id": "out",
      "target_block_id": "sum_1769102922603",
      "target_port_id": "in2",
      "waypoints": [],
      "label": "u_fb",
      "label_visible": true
    }
  ],
  "theme": null
}
"""

cascaded_tf_template = """
{
  "version": "1.0.0",
  "blocks": [
    {
      "id": "io_marker_1769104376714",
      "type": "io_marker",
      "position": {
        "x": -240.5905970616593,
        "y": 152.0
      },
      "label": "ref",
      "flipped": false,
      "custom_latex": null,
      "label_visible": true,
      "width": null,
      "height": null,
      "parameters": [
        {
          "name": "marker_type",
          "value": "input",
          "expression": null
        },
        {
          "name": "index",
          "value": 0,
          "expression": null
        },
        {
          "name": "label",
          "value": "u",
          "expression": null
        }
      ],
      "ports": [
        {
          "id": "out",
          "type": "output",
          "label": "u"
        }
      ]
    },
    {
      "id": "sum_1769104378916",
      "type": "sum",
      "position": {
        "x": -104.06501749566351,
        "y": 140.0
      },
      "label": "sum_1769104378916",
      "flipped": false,
      "custom_latex": null,
      "label_visible": false,
      "width": null,
      "height": null,
      "parameters": [
        {
          "name": "signs",
          "value": [
            "|",
            "+",
            "-"
          ],
          "expression": null
        }
      ],
      "ports": [
        {
          "id": "in1",
          "type": "input",
          "label": null
        },
        {
          "id": "in2",
          "type": "input",
          "label": null
        },
        {
          "id": "out",
          "type": "output",
          "label": null
        }
      ]
    },
    {
      "id": "transfer_function_1769104391099",
      "type": "transfer_function",
      "position": {
        "x": 34.16442889274356,
        "y": 143.0
      },
      "label": "transfer_function_1769104391099",
      "flipped": false,
      "custom_latex": "C_\\mathrm{outer}",
      "label_visible": false,
      "width": null,
      "height": null,
      "parameters": [
        {
          "name": "numerator",
          "value": [
            1
          ],
          "expression": null
        },
        {
          "name": "denominator",
          "value": [
            1,
            1
          ],
          "expression": null
        }
      ],
      "ports": [
        {
          "id": "in",
          "type": "input",
          "label": null
        },
        {
          "id": "out",
          "type": "output",
          "label": null
        }
      ]
    },
    {
      "id": "sum_1769104411915",
      "type": "sum",
      "position": {
        "x": 292.27694656382863,
        "y": 140.0
      },
      "label": "sum_1769104411915",
      "flipped": false,
      "custom_latex": null,
      "label_visible": false,
      "width": null,
      "height": null,
      "parameters": [
        {
          "name": "signs",
          "value": [
            "|",
            "+",
            "-"
          ],
          "expression": null
        }
      ],
      "ports": [
        {
          "id": "in1",
          "type": "input",
          "label": null
        },
        {
          "id": "in2",
          "type": "input",
          "label": null
        },
        {
          "id": "out",
          "type": "output",
          "label": null
        }
      ]
    },
    {
      "id": "transfer_function_1769104432548",
      "type": "transfer_function",
      "position": {
        "x": 409.02688281546693,
        "y": 143.0
      },
      "label": "transfer_function_1769104432548",
      "flipped": false,
      "custom_latex": "C_\\mathrm{inner}",
      "label_visible": false,
      "width": null,
      "height": null,
      "parameters": [
        {
          "name": "numerator",
          "value": [
            1
          ],
          "expression": null
        },
        {
          "name": "denominator",
          "value": [
            1,
            1
          ],
          "expression": null
        }
      ],
      "ports": [
        {
          "id": "in",
          "type": "input",
          "label": null
        },
        {
          "id": "out",
          "type": "output",
          "label": null
        }
      ]
    },
    {
      "id": "transfer_function_1769104459099",
      "type": "transfer_function",
      "position": {
        "x": 695.0769322737476,
        "y": 143.0
      },
      "label": "transfer_function_1769104459099",
      "flipped": false,
      "custom_latex": "G_\\mathrm{inner}",
      "label_visible": false,
      "width": null,
      "height": null,
      "parameters": [
        {
          "name": "numerator",
          "value": [
            1
          ],
          "expression": null
        },
        {
          "name": "denominator",
          "value": [
            1,
            1
          ],
          "expression": null
        }
      ],
      "ports": [
        {
          "id": "in",
          "type": "input",
          "label": null
        },
        {
          "id": "out",
          "type": "output",
          "label": null
        }
      ]
    },
    {
      "id": "sum_1769104529431",
      "type": "sum",
      "position": {
        "x": 851.8726712302629,
        "y": 140.0
      },
      "label": "sum_1769104529431",
      "flipped": false,
      "custom_latex": null,
      "label_visible": false,
      "width": null,
      "height": null,
      "parameters": [
        {
          "name": "signs",
          "value": [
            "+",
            "+",
            "|"
          ],
          "expression": null
        }
      ],
      "ports": [
        {
          "id": "in1",
          "type": "input",
          "label": null
        },
        {
          "id": "in2",
          "type": "input",
          "label": null
        },
        {
          "id": "out",
          "type": "output",
          "label": null
        }
      ]
    },
    {
      "id": "io_marker_1769104543998",
      "type": "io_marker",
      "position": {
        "x": 709.6746453937349,
        "y": 38.20662152260047
      },
      "label": "noise_inner",
      "flipped": false,
      "custom_latex": null,
      "label_visible": true,
      "width": null,
      "height": null,
      "parameters": [
        {
          "name": "marker_type",
          "value": "input",
          "expression": null
        },
        {
          "name": "index",
          "value": 2,
          "expression": null
        },
        {
          "name": "label",
          "value": "u",
          "expression": null
        }
      ],
      "ports": [
        {
          "id": "out",
          "type": "output",
          "label": "u"
        }
      ]
    },
    {
      "id": "transfer_function_1769104565181",
      "type": "transfer_function",
      "position": {
        "x": 990.9726020194248,
        "y": 143.0
      },
      "label": "transfer_function_1769104565181",
      "flipped": false,
      "custom_latex": "G_\\mathrm{outer}",
      "label_visible": false,
      "width": null,
      "height": null,
      "parameters": [
        {
          "name": "numerator",
          "value": [
            1
          ],
          "expression": null
        },
        {
          "name": "denominator",
          "value": [
            1,
            1
          ],
          "expression": null
        }
      ],
      "ports": [
        {
          "id": "in",
          "type": "input",
          "label": null
        },
        {
          "id": "out",
          "type": "output",
          "label": null
        }
      ]
    },
    {
      "id": "sum_1769104582747",
      "type": "sum",
      "position": {
        "x": 1161.788852540862,
        "y": 140.0
      },
      "label": "sum_1769104582747",
      "flipped": false,
      "custom_latex": null,
      "label_visible": false,
      "width": null,
      "height": null,
      "parameters": [
        {
          "name": "signs",
          "value": [
            "+",
            "+",
            "|"
          ],
          "expression": null
        }
      ],
      "ports": [
        {
          "id": "in1",
          "type": "input",
          "label": null
        },
        {
          "id": "in2",
          "type": "input",
          "label": null
        },
        {
          "id": "out",
          "type": "output",
          "label": null
        }
      ]
    },
    {
      "id": "io_marker_1769104595580",
      "type": "io_marker",
      "position": {
        "x": 1012.0921752580343,
        "y": 41.23079682124262
      },
      "label": "noise_outer",
      "flipped": false,
      "custom_latex": null,
      "label_visible": true,
      "width": null,
      "height": null,
      "parameters": [
        {
          "name": "marker_type",
          "value": "input",
          "expression": null
        },
        {
          "name": "index",
          "value": 1,
          "expression": null
        },
        {
          "name": "label",
          "value": "u",
          "expression": null
        }
      ],
      "ports": [
        {
          "id": "out",
          "type": "output",
          "label": "u"
        }
      ]
    },
    {
      "id": "io_marker_1769104636965",
      "type": "io_marker",
      "position": {
        "x": 1322.4250127701644,
        "y": 152.0
      },
      "label": "output1",
      "flipped": false,
      "custom_latex": null,
      "label_visible": true,
      "width": null,
      "height": null,
      "parameters": [
        {
          "name": "marker_type",
          "value": "output",
          "expression": null
        },
        {
          "name": "index",
          "value": 0,
          "expression": null
        },
        {
          "name": "label",
          "value": "y",
          "expression": null
        }
      ],
      "ports": [
        {
          "id": "in",
          "type": "input",
          "label": "y"
        }
      ]
    },
    {
      "id": "io_marker_1769104757730",
      "type": "io_marker",
      "position": {
        "x": 1018.3223222594959,
        "y": 237.12626315959824
      },
      "label": "output2",
      "flipped": false,
      "custom_latex": null,
      "label_visible": true,
      "width": null,
      "height": null,
      "parameters": [
        {
          "name": "marker_type",
          "value": "output",
          "expression": null
        },
        {
          "name": "index",
          "value": 1,
          "expression": null
        },
        {
          "name": "label",
          "value": "y",
          "expression": null
        }
      ],
      "ports": [
        {
          "id": "in",
          "type": "input",
          "label": "y"
        }
      ]
    },
    {
      "id": "sum_1769113250055",
      "type": "sum",
      "position": {
        "x": 574.1794264976029,
        "y": 140.0
      },
      "label": "sum_1769113250055",
      "flipped": false,
      "custom_latex": null,
      "label_visible": false,
      "width": null,
      "height": null,
      "parameters": [
        {
          "name": "signs",
          "value": [
            "+",
            "+",
            "|"
          ],
          "expression": null
        }
      ],
      "ports": [
        {
          "id": "in1",
          "type": "input",
          "label": null
        },
        {
          "id": "in2",
          "type": "input",
          "label": null
        },
        {
          "id": "out",
          "type": "output",
          "label": null
        }
      ]
    },
    {
      "id": "io_marker_1769113271705",
      "type": "io_marker",
      "position": {
        "x": 430.81897954233045,
        "y": 32.86969681390201
      },
      "label": "disturbance_inner",
      "flipped": false,
      "custom_latex": null,
      "label_visible": true,
      "width": null,
      "height": null,
      "parameters": [
        {
          "name": "marker_type",
          "value": "input",
          "expression": null
        },
        {
          "name": "index",
          "value": 3,
          "expression": null
        },
        {
          "name": "label",
          "value": "u",
          "expression": null
        }
      ],
      "ports": [
        {
          "id": "out",
          "type": "output",
          "label": "u"
        }
      ]
    }
  ],
  "connections": [
    {
      "id": "conn_1769104387949",
      "source_block_id": "io_marker_1769104376714",
      "source_port_id": "out",
      "target_block_id": "sum_1769104378916",
      "target_port_id": "in1",
      "waypoints": [],
      "label": "r1",
      "label_visible": true
    },
    {
      "id": "conn_1769104393831",
      "source_block_id": "sum_1769104378916",
      "source_port_id": "out",
      "target_block_id": "transfer_function_1769104391099",
      "target_port_id": "in",
      "waypoints": [],
      "label": "e1",
      "label_visible": true
    },
    {
      "id": "conn_1769104428715",
      "source_block_id": "transfer_function_1769104391099",
      "source_port_id": "out",
      "target_block_id": "sum_1769104411915",
      "target_port_id": "in1",
      "waypoints": [],
      "label": "r2",
      "label_visible": true
    },
    {
      "id": "conn_1769104448531",
      "source_block_id": "sum_1769104411915",
      "source_port_id": "out",
      "target_block_id": "transfer_function_1769104432548",
      "target_port_id": "in",
      "waypoints": [],
      "label": "e2",
      "label_visible": true
    },
    {
      "id": "conn_1769104533714",
      "source_block_id": "transfer_function_1769104459099",
      "source_port_id": "out",
      "target_block_id": "sum_1769104529431",
      "target_port_id": "in2",
      "waypoints": [
        {
          "x": 823.4748124937616,
          "y": 167.99991891860498
        },
        {
          "x": 823.4748124937616,
          "y": 167.99991891860498
        }
      ],
      "label": null,
      "label_visible": false
    },
    {
      "id": "conn_1769104538315",
      "source_block_id": "sum_1769104529431",
      "source_port_id": "out",
      "target_block_id": "sum_1769104411915",
      "target_port_id": "in2",
      "waypoints": [
        {
          "x": 929.872804556414,
          "y": 168.00051625622424
        },
        {
          "x": 929.872804556414,
          "y": 253.19664370954445
        },
        {
          "x": 320.2769540279223,
          "y": 253.19664370954445
        }
      ],
      "label": null,
      "label_visible": false
    },
    {
      "id": "conn_1769104558381",
      "source_block_id": "io_marker_1769104543998",
      "source_port_id": "out",
      "target_block_id": "sum_1769104529431",
      "target_port_id": "in1",
      "waypoints": [
        {
          "x": 879.8726638557533,
          "y": 54.20691635014241
        }
      ],
      "label": "n2",
      "label_visible": true
    },
    {
      "id": "conn_1769104576967",
      "source_block_id": "sum_1769104529431",
      "source_port_id": "out",
      "target_block_id": "transfer_function_1769104565181",
      "target_port_id": "in",
      "waypoints": [],
      "label": "y2",
      "label_visible": true
    },
    {
      "id": "conn_1769104585831",
      "source_block_id": "transfer_function_1769104565181",
      "source_port_id": "out",
      "target_block_id": "sum_1769104582747",
      "target_port_id": "in2",
      "waypoints": [],
      "label": null,
      "label_visible": false
    },
    {
      "id": "conn_1769104603397",
      "source_block_id": "io_marker_1769104595580",
      "source_port_id": "out",
      "target_block_id": "sum_1769104582747",
      "target_port_id": "in1",
      "waypoints": [],
      "label": "n1",
      "label_visible": true
    },
    {
      "id": "conn_1769104609032",
      "source_block_id": "sum_1769104582747",
      "source_port_id": "out",
      "target_block_id": "sum_1769104378916",
      "target_port_id": "in2",
      "waypoints": [
        {
          "x": 1239.7888728020953,
          "y": 168.00051625622424
        },
        {
          "x": 1239.7888728020953,
          "y": 341.0815860618435
        },
        {
          "x": -76.0649817653404,
          "y": 341.0815860618435
        },
        {
          "x": -76.0649817653404,
          "y": 218.0000202612333
        }
      ],
      "label": null,
      "label_visible": false
    },
    {
      "id": "conn_1769104745363",
      "source_block_id": "sum_1769104582747",
      "source_port_id": "out",
      "target_block_id": "io_marker_1769104636965",
      "target_port_id": "in",
      "waypoints": [],
      "label": "y1",
      "label_visible": true
    },
    {
      "id": "conn_1769104762680",
      "source_block_id": "sum_1769104529431",
      "source_port_id": "out",
      "target_block_id": "io_marker_1769104757730",
      "target_port_id": "in",
      "waypoints": [
        {
          "x": 929.9299449310961,
          "y": 167.9998256390318
        },
        {
          "x": 929.9299449310961,
          "y": 253.12581608609852
        }
      ],
      "label": null,
      "label_visible": false
    },
    {
      "id": "conn_1769113259257",
      "source_block_id": "transfer_function_1769104432548",
      "source_port_id": "out",
      "target_block_id": "sum_1769113250055",
      "target_port_id": "in2",
      "waypoints": [],
      "label": "u2",
      "label_visible": true
    },
    {
      "id": "conn_1769113263656",
      "source_block_id": "sum_1769113250055",
      "source_port_id": "out",
      "target_block_id": "transfer_function_1769104459099",
      "target_port_id": "in",
      "waypoints": [],
      "label": null,
      "label_visible": false
    },
    {
      "id": "conn_1769113281839",
      "source_block_id": "io_marker_1769113271705",
      "source_port_id": "out",
      "target_block_id": "sum_1769113250055",
      "target_port_id": "in1",
      "waypoints": [],
      "label": "d2",
      "label_visible": true
    }
  ],
  "theme": null
}
"""

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
