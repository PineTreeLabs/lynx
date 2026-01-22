feedback_tf_template = """
{
  "version": "1.0.0",
  "blocks": [
    {
      "id": "io_marker_1769102540105",
      "type": "io_marker",
      "position": {
        "x": 184.71724307551472,
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
    }
  ],
  "connections": [
    {
      "id": "conn_1769102595204",
      "source_block_id": "io_marker_1769102540105",
      "source_port_id": "out",
      "target_block_id": "sum_1769102547306",
      "target_port_id": "in1",
      "waypoints": [
        {
          "x": 277.8586489058141,
          "y": 182.0007595761906
        },
        {
          "x": 277.8586489058141,
          "y": 182.0007595761906
        }
      ],
      "label": "r",
      "label_visible": true
    },
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
      "label": "d",
      "label_visible": true
    },
    {
      "id": "conn_1769105111328",
      "source_block_id": "sum_1769105068595",
      "source_port_id": "out",
      "target_block_id": "sum_1769102547306",
      "target_port_id": "in2",
      "waypoints": [
        {
          "x": 863.9531372296697,
          "y": 182.2599835427484
        },
        {
          "x": 863.9531372296697,
          "y": 272.93570431591763
        },
        {
          "x": 338.99999274425363,
          "y": 272.93570431591763
        }
      ],
      "label": null,
      "label_visible": false
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
        "x": 184.71724307551472,
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
    }
  ],
  "connections": [
    {
      "id": "conn_1769102595204",
      "source_block_id": "io_marker_1769102540105",
      "source_port_id": "out",
      "target_block_id": "sum_1769102547306",
      "target_port_id": "in1",
      "waypoints": [
        {
          "x": 277.8586489058141,
          "y": 182.0007595761906
        },
        {
          "x": 277.8586489058141,
          "y": 182.0007595761906
        }
      ],
      "label": "r",
      "label_visible": true
    },
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
      "label": "d",
      "label_visible": true
    },
    {
      "id": "conn_1769105206929",
      "source_block_id": "sum_1769105176411",
      "source_port_id": "out",
      "target_block_id": "sum_1769102547306",
      "target_port_id": "in2",
      "waypoints": [
        {
          "x": 887.0,
          "y": 182.0
        },
        {
          "x": 887.0,
          "y": 275.0
        },
        {
          "x": 339.0,
          "y": 275.0
        }
      ],
      "label": null,
      "label_visible": false
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
        "x": 49.451299563914574,
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
        "x": 331.9539545719116,
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
        "x": 957.4541110881123,
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
      "id": "sum_1769105252127",
      "type": "sum",
      "position": {
        "x": 820.6389171034264,
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
        "x": 657.7853448707134,
        "y": 49.65358211475905
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
      "id": "conn_1769102926686",
      "source_block_id": "transfer_function_1769102555888",
      "source_port_id": "out",
      "target_block_id": "sum_1769102922603",
      "target_port_id": "in2",
      "waypoints": [
        {
          "x": 466.76125743406,
          "y": 182.0005484117843
        },
        {
          "x": 466.76125743406,
          "y": 182.0005484117843
        }
      ],
      "label": "u_fb",
      "label_visible": true
    },
    {
      "id": "conn_1769102929737",
      "source_block_id": "sum_1769102922603",
      "source_port_id": "out",
      "target_block_id": "state_space_1769102736336",
      "target_port_id": "in",
      "waypoints": [
        {
          "x": 592.3960078498353,
          "y": 182.00041533431335
        },
        {
          "x": 592.3960078498353,
          "y": 182.00041533431335
        }
      ],
      "label": "u",
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
      "waypoints": [
        {
          "x": 917.0464929299028,
          "y": 181.99989931581985
        },
        {
          "x": 917.0464929299028,
          "y": 181.99989931581985
        }
      ],
      "label": "y",
      "label_visible": true
    },
    {
      "id": "conn_1769105264427",
      "source_block_id": "io_marker_1769105261377",
      "source_port_id": "out",
      "target_block_id": "sum_1769105252127",
      "target_port_id": "in1",
      "waypoints": [
        {
          "x": 848.6388959375597,
          "y": 65.65321369941486
        }
      ],
      "label": "d",
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
          "x": 898.6389193935538,
          "y": 182.00053546232806
        },
        {
          "x": 898.6389193935538,
          "y": 265.8740224244129
        },
        {
          "x": 248.07157672340227,
          "y": 265.8740224244129
        }
      ],
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
        "x": 49.451299563914574,
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
        "x": 324.09307076279043,
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
        "x": 923.2951376397539,
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
        "x": 643.9450914168157,
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
      "id": "sum_1769105312492",
      "type": "sum",
      "position": {
        "x": 806.8261394737924,
        "y": 154.0
      },
      "label": "sum_1769105312492",
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
      "id": "io_marker_1769105320258",
      "type": "io_marker",
      "position": {
        "x": 664.1394412336331,
        "y": 56.15324730260363
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
      "id": "conn_1769102926686",
      "source_block_id": "transfer_function_1769102555888",
      "source_port_id": "out",
      "target_block_id": "sum_1769102922603",
      "target_port_id": "in2",
      "waypoints": [],
      "label": "u_fb",
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
      "id": "conn_1769103016552",
      "source_block_id": "sum_1769102922603",
      "source_port_id": "out",
      "target_block_id": "transfer_function_1769103013153",
      "target_port_id": "in",
      "waypoints": [
        {
          "x": 600.7568270924306,
          "y": 182.00005177125237
        },
        {
          "x": 600.7568270924306,
          "y": 182.00005177125237
        }
      ],
      "label": "u",
      "label_visible": true
    },
    {
      "id": "conn_1769105323293",
      "source_block_id": "io_marker_1769105320258",
      "source_port_id": "out",
      "target_block_id": "sum_1769105312492",
      "target_port_id": "in1",
      "waypoints": [],
      "label": "d",
      "label_visible": true
    },
    {
      "id": "conn_1769105335309",
      "source_block_id": "transfer_function_1769103013153",
      "source_port_id": "out",
      "target_block_id": "sum_1769105312492",
      "target_port_id": "in2",
      "waypoints": [],
      "label": null,
      "label_visible": false
    },
    {
      "id": "conn_1769105338560",
      "source_block_id": "sum_1769105312492",
      "source_port_id": "out",
      "target_block_id": "io_marker_1769102614871",
      "target_port_id": "in",
      "waypoints": [
        {
          "x": 893.06065965301,
          "y": 181.99977328172633
        },
        {
          "x": 893.06065965301,
          "y": 181.99977328172633
        }
      ],
      "label": "y",
      "label_visible": true
    },
    {
      "id": "conn_1769105342780",
      "source_block_id": "sum_1769105312492",
      "source_port_id": "out",
      "target_block_id": "sum_1769102547306",
      "target_port_id": "in2",
      "waypoints": [
        {
          "x": 884.8261863744586,
          "y": 181.99977328172633
        },
        {
          "x": 882.8261394737924,
          "y": 265.641201335666
        },
        {
          "x": 248.0716543875787,
          "y": 265.641201335666
        }
      ],
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
        "x": 324.09307076279043,
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
        "x": 948.1079174770715,
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
        "x": 643.9450914168157,
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
        "x": 647.7283395007272,
        "y": 51.38264894100939
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
        "x": 809.0843206504884,
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
      "id": "conn_1769102926686",
      "source_block_id": "transfer_function_1769102555888",
      "source_port_id": "out",
      "target_block_id": "sum_1769102922603",
      "target_port_id": "in2",
      "waypoints": [],
      "label": "u_fb",
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
      "id": "conn_1769103016552",
      "source_block_id": "sum_1769102922603",
      "source_port_id": "out",
      "target_block_id": "transfer_function_1769103013153",
      "target_port_id": "in",
      "waypoints": [
        {
          "x": 600.7568270924306,
          "y": 182.00005177125237
        },
        {
          "x": 600.7568270924306,
          "y": 182.00005177125237
        }
      ],
      "label": "u",
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
      "waypoints": [
        {
          "x": 906.5961343899528,
          "y": 181.9996697685248
        },
        {
          "x": 906.5961343899528,
          "y": 181.9996697685248
        }
      ],
      "label": "y",
      "label_visible": true
    },
    {
      "id": "conn_1769105410877",
      "source_block_id": "io_marker_1769105385044",
      "source_port_id": "out",
      "target_block_id": "sum_1769105399078",
      "target_port_id": "in1",
      "waypoints": [
        {
          "x": 837.0843359766612,
          "y": 67.3824838252718
        }
      ],
      "label": "d",
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
        "x": -97.95164940271401,
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
      "id": "sum_1769104378916",
      "type": "sum",
      "position": {
        "x": 96.0,
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
        "x": 212.0,
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
        "x": 375.6373705203551,
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
        "x": 506.26814342985404,
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
      "id": "transfer_function_1769104565181",
      "type": "transfer_function",
      "position": {
        "x": 993.947123466176,
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
      "label": "disturbance_outer",
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
          "name": "label",
          "value": "y",
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
          "id": "in",
          "type": "input",
          "label": "y"
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
      "waypoints": [
        {
          "x": 29.024188624660265,
          "y": 168.0007249518778
        },
        {
          "x": 29.024188624660265,
          "y": 168.0007249518778
        }
      ],
      "label": "r1",
      "label_visible": true
    },
    {
      "id": "conn_1769104393831",
      "source_block_id": "sum_1769104378916",
      "source_port_id": "out",
      "target_block_id": "transfer_function_1769104391099",
      "target_port_id": "in",
      "waypoints": [
        {
          "x": 181.999976332301,
          "y": 167.9987036540806
        },
        {
          "x": 181.999976332301,
          "y": 167.9987036540806
        }
      ],
      "label": "e1",
      "label_visible": true
    },
    {
      "id": "conn_1769104428715",
      "source_block_id": "transfer_function_1769104391099",
      "source_port_id": "out",
      "target_block_id": "sum_1769104411915",
      "target_port_id": "in1",
      "waypoints": [
        {
          "x": 343.81866471882614,
          "y": 167.99886569732053
        },
        {
          "x": 343.81866471882614,
          "y": 167.99886569732053
        }
      ],
      "label": "r2",
      "label_visible": true
    },
    {
      "id": "conn_1769104448531",
      "source_block_id": "sum_1769104411915",
      "source_port_id": "out",
      "target_block_id": "transfer_function_1769104432548",
      "target_port_id": "in",
      "waypoints": [
        {
          "x": 468.95277438623134,
          "y": 168.0002314542869
        },
        {
          "x": 468.95277438623134,
          "y": 168.0002314542869
        }
      ],
      "label": "e2",
      "label_visible": true
    },
    {
      "id": "conn_1769104526148",
      "source_block_id": "transfer_function_1769104432548",
      "source_port_id": "out",
      "target_block_id": "transfer_function_1769104459099",
      "target_port_id": "in",
      "waypoints": [],
      "label": "u2",
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
          "x": 929.8727322265489,
          "y": 167.99984589069058
        },
        {
          "x": 929.8727322265489,
          "y": 253.18716750434473
        },
        {
          "x": 403.6373659117468,
          "y": 253.18716750434473
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
      "label": "d2",
      "label_visible": true
    },
    {
      "id": "conn_1769104576967",
      "source_block_id": "sum_1769104529431",
      "source_port_id": "out",
      "target_block_id": "transfer_function_1769104565181",
      "target_port_id": "in",
      "waypoints": [
        {
          "x": 950.9098526593604,
          "y": 167.99939559589706
        },
        {
          "x": 950.9098526593604,
          "y": 167.99939559589706
        }
      ],
      "label": "y2",
      "label_visible": true
    },
    {
      "id": "conn_1769104585831",
      "source_block_id": "transfer_function_1769104565181",
      "source_port_id": "out",
      "target_block_id": "sum_1769104582747",
      "target_port_id": "in2",
      "waypoints": [
        {
          "x": 1127.8679642844204,
          "y": 167.9999806640506
        },
        {
          "x": 1127.8679642844204,
          "y": 167.9999806640506
        }
      ],
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
      "label": "d1",
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
          "x": 1239.7889198760483,
          "y": 167.9999732549366
        },
        {
          "x": 1237.788852540862,
          "y": 310.23667561938794
        },
        {
          "x": 124.00001940021218,
          "y": 310.23667561938794
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
    }
  ],
  "theme": null
}
"""