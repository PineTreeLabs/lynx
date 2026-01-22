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
            "|",
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
        "x": 644.6416269173607,
        "y": 157.26005326187624
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
        "x": 836.2910533469737,
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
      "waypoints": [
        {
          "x": 598.1590210992194,
          "y": 181.99943440765568
        },
        {
          "x": 598.1590210992194,
          "y": 181.99943440765568
        }
      ],
      "label": "u",
      "label_visible": true
    },
    {
      "id": "conn_1769102621572",
      "source_block_id": "transfer_function_1769102559255",
      "source_port_id": "out",
      "target_block_id": "io_marker_1769102614871",
      "target_port_id": "in",
      "waypoints": [
        {
          "x": 790.4664172812206,
          "y": 182.26000354523168
        },
        {
          "x": 790.4664172812206,
          "y": 182.26000354523168
        }
      ],
      "label": "y",
      "label_visible": true
    },
    {
      "id": "conn_1769102638454",
      "source_block_id": "transfer_function_1769102559255",
      "source_port_id": "out",
      "target_block_id": "sum_1769102547306",
      "target_port_id": "in2",
      "waypoints": [
        {
          "x": 766.6417545920573,
          "y": 182.26000354523168
        },
        {
          "x": 766.6417545920573,
          "y": 260.24117429209565
        },
        {
          "x": 339.0000252628216,
          "y": 260.24117429209565
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
            "|",
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
        "x": 836.2910533469737,
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
      "id": "conn_1769102742460",
      "source_block_id": "state_space_1769102736336",
      "source_port_id": "out",
      "target_block_id": "io_marker_1769102614871",
      "target_port_id": "in",
      "waypoints": [],
      "label": "y",
      "label_visible": true
    },
    {
      "id": "conn_1769102747388",
      "source_block_id": "state_space_1769102736336",
      "source_port_id": "out",
      "target_block_id": "sum_1769102547306",
      "target_port_id": "in2",
      "waypoints": [
        {
          "x": 769.223309109467,
          "y": 181.9994282384926
        },
        {
          "x": 769.223309109467,
          "y": 293.02786618761826
        },
        {
          "x": 339.0000079436196,
          "y": 293.02786618761826
        },
        {
          "x": 339.0000079436196,
          "y": 232.00023120553038
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
        "x": 836.2910533469737,
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
      "id": "conn_1769102742460",
      "source_block_id": "state_space_1769102736336",
      "source_port_id": "out",
      "target_block_id": "io_marker_1769102614871",
      "target_port_id": "in",
      "waypoints": [],
      "label": "y",
      "label_visible": true
    },
    {
      "id": "conn_1769102747388",
      "source_block_id": "state_space_1769102736336",
      "source_port_id": "out",
      "target_block_id": "sum_1769102547306",
      "target_port_id": "in2",
      "waypoints": [
        {
          "x": 769.2233762333185,
          "y": 182.00057327501287
        },
        {
          "x": 769.2233762333185,
          "y": 298.32008853114587
        },
        {
          "x": 248.0715969864969,
          "y": 298.32008853114587
        },
        {
          "x": 248.0715969864969,
          "y": 232.00024863228563
        }
      ],
      "label": null,
      "label_visible": false
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
        "x": 836.2910533469737,
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
      "id": "conn_1769103020186",
      "source_block_id": "transfer_function_1769103013153",
      "source_port_id": "out",
      "target_block_id": "io_marker_1769102614871",
      "target_port_id": "in",
      "waypoints": [],
      "label": "y",
      "label_visible": true
    },
    {
      "id": "conn_1769103031219",
      "source_block_id": "transfer_function_1769103013153",
      "source_port_id": "out",
      "target_block_id": "sum_1769102547306",
      "target_port_id": "in2",
      "waypoints": [
        {
          "x": 765.9449943188492,
          "y": 181.999445562436
        },
        {
          "x": 765.9449943188492,
          "y": 279.1651708165388
        },
        {
          "x": 248.0715596999098,
          "y": 279.1651708165388
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
        "x": 836.2910533469737,
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
      "id": "conn_1769103020186",
      "source_block_id": "transfer_function_1769103013153",
      "source_port_id": "out",
      "target_block_id": "io_marker_1769102614871",
      "target_port_id": "in",
      "waypoints": [],
      "label": "y",
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
      "id": "conn_1769103292317",
      "source_block_id": "transfer_function_1769103013153",
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